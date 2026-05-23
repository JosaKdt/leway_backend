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

router = APIRouter()


@router.post(
    "/generer",
    response_model=RecommandationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Générer un rapport de recommandation RIASEC",
)
def generer_recommandation(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    CU03 — Génération des recommandations.

    Pipeline (mémoire Fig. 7 & Fig. 9) :
    1. Récupère le profil RIASEC du bachelier
    2. Applique les Veto Factors
    3. Appelle le moteur LLM (Folawè — port 8001)
       → mocké ici en attendant l'intégration
    4. Sauvegarde Recommandation + ScoreCompatibilite
    5. Met en cache Redis (TTL 24h) — TODO
    """
    id_bachelier = UUID(current_user["sub"])

    # ── 1. Vérifier que le profil existe ─────────────────────────────────────
    profil = session.exec(
        select(ProfilPsychometrique).where(
            ProfilPsychometrique.id_bachelier == id_bachelier
        )
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun profil psychometrique trouve. Completez d'abord le questionnaire via POST /api/profil.",
        )

    # ── 2. Créer l'entrée Recommandation ─────────────────────────────────────
    recommandation = Recommandation(
        id_bachelier=id_bachelier,
        date_generation=datetime.now(timezone.utc),
        version_algo="1.0",
        score_max=None,   # sera mis à jour après scoring
        statut="generee",
    )
    session.add(recommandation)
    session.commit()
    session.refresh(recommandation)

    # ── 3. Moteur LLM — STUB (intégration Folawè) ────────────────────────────
    # TODO : remplacer ce bloc par l'appel réel au moteur de scoring
    # POST http://localhost:8001/api/scoring avec le profil anonymisé
    # RD16 : aucune PII transmise — uniquement les 6 scores RIASEC + Veto Factors
    print(
        f"[SCORING MOCK] Profil RIASEC : "
        f"R={profil.score_r} I={profil.score_i} A={profil.score_a} "
        f"S={profil.score_s} E={profil.score_e} C={profil.score_c}"
    )

    # ── 4. Retourner la recommandation créée ─────────────────────────────────
    return recommandation


@router.get(
    "/moi",
    response_model=List[RecommandationRead],
    summary="Historique de mes recommandations",
)
def mes_recommandations(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Retourne toutes les recommandations générées par le bachelier connecté."""
    id_bachelier = UUID(current_user["sub"])
    recommandations = session.exec(
        select(Recommandation)
        .where(Recommandation.id_bachelier == id_bachelier)
        .order_by(Recommandation.date_generation.desc())
    ).all()
    return recommandations


@router.get(
    "/{id_recommandation}",
    response_model=RecommandationRead,
    summary="Détail d'une recommandation avec ses scores",
)
def get_recommandation(
    id_recommandation: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    recommandation = session.get(Recommandation, id_recommandation)
    if not recommandation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommandation introuvable",
        )
    # Vérifier que la recommandation appartient au bachelier connecté
    if str(recommandation.id_bachelier) != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces interdit",
        )
    # Marquer comme consultée
    if recommandation.statut == "generee":
        recommandation.statut = "consultee"
        session.add(recommandation)
        session.commit()
        session.refresh(recommandation)
    return recommandation