"""
ORIAB — api/recommandations.py
CU03 — Pipeline complet de génération de recommandations.

POST /api/recommandations/generer  → Top 3 + Veto + RAG + LLM + persistance DB
GET  /api/recommandations/moi      → historique
GET  /api/recommandations/{id}     → détail + scores
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.recommandation import Recommandation, RecommandationRead
from app.models.score_compatibilite import ScoreCompatibilite
from app.models.profil_psychometrique import ProfilPsychometrique
from app.models.bachelier import Bachelier
from app.models.filiere import Filiere
from app.scoring.cosinus import toutes_filieres_scorees          # lit depuis DB PostgreSQL
from app.scoring.veto import appliquer_veto
from app.scoring.prompt_builder import construire_prompt_llm, construire_prompt_mistral

router = APIRouter()


@router.post(
    "/generer",
    response_model=RecommandationRead,
    status_code=status.HTTP_201_CREATED,
    summary="CU03 — Générer Top 3 + Veto Factors + rapport LLM (RAG intégré)",
)
async def generer_recommandation(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Pipeline complet (mémoire Fig. 7 & 9) :

    1. Récupère le profil RIASEC du bachelier (DB)
    2. Calcule le Weighted Score pour toutes les filières (cosinus + marché + IA)
    3. Applique les 4 Veto Factors (durée, budget, mobilité, série bac)
    4. Construit le prompt avec contexte RAG (données marché béninoises injectées)
    5. Appelle le LLM (Mistral local ou Claude Haiku cloud)
    6. Persiste Recommandation + ScoreCompatibilite (Top 3 validés)

    RD16 : aucune PII transmise au LLM — profil anonymisé.
    RD18 : Veto Factors appliqués avant toute transmission au LLM.
    RD19 : un seul mode LLM par recommandation (cloud OU local).
    """
    id_bachelier = UUID(current_user["sub"])

    # ── 1. Profil RIASEC ──────────────────────────────────────────────────────
    profil = session.exec(
        select(ProfilPsychometrique).where(
            ProfilPsychometrique.id_bachelier == id_bachelier
        )
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun profil psychométrique. Complétez d'abord POST /api/profil/",
        )

    scores_riasec = {
        "R": profil.score_r, "I": profil.score_i, "A": profil.score_a,
        "S": profil.score_s, "E": profil.score_e, "C": profil.score_c,
    }
    dim_dom = max(scores_riasec, key=scores_riasec.get)

    # Récupérer la série bac du bachelier pour VETO 4
    bachelier = session.get(Bachelier, id_bachelier)
    serie_bac = getattr(bachelier, "serie_bac", None) if bachelier else None

    # ── 2. Top 5 filières (Weighted Score depuis DB) ──────────────────────────
    top5_raw = toutes_filieres_scorees(scores_riasec, session)

    # ── 3. Veto Factors ───────────────────────────────────────────────────────
    veto = appliquer_veto(
        top5=top5_raw,
        ressources_financieres=profil.ressources_financieres,
        mobilite_geo=profil.mobilite_geo,
        horizon_temporel=profil.horizon_temporel,
        serie_bac=serie_bac,
    )
    top3_valides   = veto["top5_valides"][:3]  # On garde le Top 3 final
    top3_eliminees = veto["eliminees"]

    # Déterminer le type de veto pour le message d'avertissement
    veto_serie_bac = any(
        "série" in " ".join(e["raisons_veto"]).lower()
        for e in top3_eliminees
    ) if top3_eliminees else False

    if top3_valides:
        top3_pour_llm = top3_valides
        avertissement_veto = None
    elif veto_serie_bac:
        # Veto série bac = irrévocable, pas de fallback trompeur
        top3_pour_llm = []
        avertissement_veto = (
            "Aucune filière compatible avec ta série bac. "
            "Les filières recommandées exigent des séries différentes."
        )
    else:
        # Veto budget/durée = révisable, on affiche quand même le Top 3 brut
        top3_pour_llm = top5_raw[:3]
        avertissement_veto = (
            "Toutes les filières ont été filtrées par tes contraintes "
            "(budget, durée, mobilité). Révise-les si possible."
        )

    # ── 4. Rapport LLM avec contexte RAG ─────────────────────────────────────
    mode_llm = os.getenv("LLM_MODE", "local")
    rapport_llm: dict = {}

    try:
        if mode_llm == "cloud":
            from app.providers.claude_haiku import ClaudeHaikuProvider
            provider = ClaudeHaikuProvider()
            prompt = construire_prompt_llm(
                scores_riasec, top3_pour_llm, dim_dom, serie_bac
            )
            rapport_llm = await provider.generer_rapport(prompt)
        else:
            from app.providers.ollama import OllamaProvider
            rapport_llm = await OllamaProvider().generer_avec_fallback(
                scores_riasec, top3_pour_llm, dim_dom, serie_bac
            )
    except Exception as e:
        rapport_llm = {
            "rapport_synthese": (
                f"Profil {dim_dom} dominant. Rapport généré hors-LLM."
                + (f" ({avertissement_veto})" if avertissement_veto else "")
            ),
            "top3_justifiees": [],
            "mode": f"erreur_llm: {str(e)[:80]}",
        }

    # Si aucune filière valide, le rapport LLM ne génère rien d'utile
    if not top3_valides and not top3_pour_llm:
        rapport_llm = {
            "rapport_synthese": avertissement_veto or "Aucune filière recommandée.",
            "top3_justifiees": [],
            "mode": "veto_total",
        }

    # ── 5. Persistance DB ─────────────────────────────────────────────────────
    score_max = top3_valides[0]["weighted_score"] if top3_valides else (
        top5_raw[0]["weighted_score"] if top5_raw else None
    )

    recommandation = Recommandation(
        id_bachelier=id_bachelier,
        date_generation=datetime.now(timezone.utc),
        version_algo="1.0",
        score_max=score_max,
        statut="generee",
    )
    session.add(recommandation)
    session.commit()
    session.refresh(recommandation)

    # Persister Top 3 validés dans score_compatibilite
    for i, f in enumerate(top3_valides[:3], start=1):
        justif = next(
            (x.get("justification") for x in rapport_llm.get("top3_justifiees", [])
             if x.get("nom") == f["nom"]),
            None,
        )
        session.add(ScoreCompatibilite(
            id_recommandation  = recommandation.id_recommandation,
            id_filiere         = UUID(f["id_filiere"]),
            score_weighted     = f["weighted_score"],
            score_riasec_match = round(f["sim_riasec"] * 100, 1),
            score_marche       = round(f["score_marche"] * 100, 1),
            score_ia           = round(f["score_ia"] * 100, 1),
            classement         = i,
            justification_ia   = justif,
        ))

    # Persister les filières éliminées (motif_veto)
    for elim in top3_eliminees:
        session.add(ScoreCompatibilite(
            id_recommandation  = recommandation.id_recommandation,
            id_filiere         = UUID(elim["id_filiere"]),
            score_weighted     = elim["weighted_score"],
            classement         = None,
            motif_veto         = " | ".join(elim["raisons_veto"]),
        ))

    session.commit()
    session.refresh(recommandation)
    return recommandation


@router.get(
    "/moi",
    response_model=List[RecommandationRead],
    summary="Mes recommandations (les plus récentes en premier)",
)
def mes_recommandations(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    id_bachelier = UUID(current_user["sub"])
    return session.exec(
        select(Recommandation)
        .where(Recommandation.id_bachelier == id_bachelier)
        .order_by(Recommandation.date_generation.desc())
    ).all()


@router.get(
    "/{id_recommandation}",
    summary="Détail d'une recommandation — enrichi avec scores et filières",
)
def get_recommandation(
    id_recommandation: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Retourne la recommandation enrichie pour le RapportPage :
    - scores[]    : filières recommandées (classement non nul), avec données filière
    - eliminees[] : filières exclues par Veto Factors, avec motif
    """
    rec = session.get(Recommandation, id_recommandation)
    if not rec:
        raise HTTPException(404, "Recommandation introuvable")
    if str(rec.id_bachelier) != current_user["sub"]:
        raise HTTPException(403, "Accès interdit")

    # Marquer comme consultée
    if rec.statut == "generee":
        rec.statut = "consultee"
        session.add(rec); session.commit(); session.refresh(rec)

    # Charger les scores liés + données filière
    sc_rows = session.exec(
        select(ScoreCompatibilite, Filiere)
        .join(Filiere, Filiere.id_filiere == ScoreCompatibilite.id_filiere)
        .where(ScoreCompatibilite.id_recommandation == rec.id_recommandation)
    ).all()

    scores, eliminees = [], []
    for sc, fil in sc_rows:
        if sc.classement is not None:
            scores.append({
                "classement":          sc.classement,
                "id_filiere":          str(fil.id_filiere),
                "nom":                 fil.nom,
                "domaine":             fil.domaine,
                "weighted_score":      sc.score_weighted,
                "sim_riasec":          sc.score_riasec_match,
                "score_marche":        sc.score_marche,
                "score_ia":            sc.score_ia,
                "duree_theorique":     fil.duree_theorique,
                "salaire_median_p50":  fil.salaire_median_p50,
                "taux_insertion":      fil.taux_insertion,
                "indice_saturation":   fil.indice_saturation,
                "tendance_ia":         fil.tendance_ia,
                "justification_ia":    sc.justification_ia,
            })
        else:
            eliminees.append({
                "nom":            fil.nom,
                "weighted_score": sc.score_weighted,
                "motif_veto":     sc.motif_veto,
            })

    scores.sort(key=lambda x: x["classement"])

    return {
        "id_recommandation": rec.id_recommandation,
        "id_bachelier":      rec.id_bachelier,
        "date_generation":   rec.date_generation,
        "version_algo":      rec.version_algo,
        "score_max":         rec.score_max,
        "statut":            rec.statut,
        "scores":            scores,
        "eliminees":         eliminees,
    }
