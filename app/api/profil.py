from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.profil_psychometrique import ProfilPsychometrique

router = APIRouter()


# ─── Schéma d'entrée — 28 items RIASEC ───────────────────────────────────────

class QuestionnaireSubmit(ProfilPsychometrique.__base__):
    """
    Réponses brutes au questionnaire psychométrique.
    Les scores RIASEC sont calculés côté serveur à partir des réponses.

    Section A — Profil académique     (items 1-5)
    Section B — Personnalité & Valeurs (items 6-17)
    Section C — Ambitions & Objectifs  (items 18-21)
    Section D — Contexte Socioéco      (items 22-25)
    Section E — Capacités Personnelles (items 26-28)

    Chaque item : valeur Likert 1-5
    """
    # Réponses brutes par section — stockées en JSONB
    reponses_section_a: Optional[Dict[str, int]] = None  # 5 items → R, I, C
    reponses_section_b: Optional[Dict[str, int]] = None  # 12 items → R, I, A, S, E, C
    reponses_section_c: Optional[Dict[str, int]] = None  # 4 items  → E + Veto Factors
    reponses_section_d: Optional[Dict[str, int]] = None  # 4 items  → Veto Factors uniquement
    reponses_section_e: Optional[Dict[str, int]] = None  # 3 items  → R, I, A

    # Veto Factors — collectés via Section D
    ressources_financieres: Optional[int] = None
    mobilite_geo: Optional[bool] = None
    horizon_temporel: Optional[str] = None


def calculer_scores_riasec(data: QuestionnaireSubmit) -> Dict[str, float]:
    """
    Calcule les 6 scores RIASEC normalisés entre 0 et 100.
    Chaque score = somme pondérée des items correspondants / max possible × 100.

    Pondérations :
    - Items situationnels précis  → poids 2
    - Items généraux              → poids 1

    Section A (5 items) → R×2, I×2, C×1
    Section B (12 items) → tous les 6 dimensions
    Section C (4 items)  → E×2
    Section E (3 items)  → R×1, I×1, A×2
    """
    scores = {"R": 0.0, "I": 0.0, "A": 0.0, "S": 0.0, "E": 0.0, "C": 0.0}
    max_scores = {"R": 0.0, "I": 0.0, "A": 0.0, "S": 0.0, "E": 0.0, "C": 0.0}

    # ── Section A — contributions R, I, C ────────────────────────────────────
    poids_a = {
        "a1": ("R", 2), "a2": ("I", 2), "a3": ("C", 1),
        "a4": ("R", 1), "a5": ("I", 1),
    }
    for key, (dim, poids) in poids_a.items():
        val = (data.reponses_section_a or {}).get(key, 0)
        scores[dim] += val * poids
        max_scores[dim] += 5 * poids

    # ── Section B — toutes les dimensions ────────────────────────────────────
    poids_b = {
        "b1": ("R", 2), "b2": ("I", 2), "b3": ("A", 2), "b4": ("S", 2),
        "b5": ("E", 2), "b6": ("C", 2), "b7": ("R", 1), "b8": ("I", 1),
        "b9": ("A", 1), "b10": ("S", 1), "b11": ("E", 1), "b12": ("C", 1),
    }
    for key, (dim, poids) in poids_b.items():
        val = (data.reponses_section_b or {}).get(key, 0)
        scores[dim] += val * poids
        max_scores[dim] += 5 * poids

    # ── Section C — contributions E ───────────────────────────────────────────
    poids_c = {
        "c1": ("E", 2), "c2": ("E", 1), "c3": ("E", 2), "c4": ("E", 1),
    }
    for key, (dim, poids) in poids_c.items():
        val = (data.reponses_section_c or {}).get(key, 0)
        scores[dim] += val * poids
        max_scores[dim] += 5 * poids

    # ── Section E — contributions R, I, A ────────────────────────────────────
    poids_e = {
        "e1": ("R", 1), "e2": ("I", 1), "e3": ("A", 2),
    }
    for key, (dim, poids) in poids_e.items():
        val = (data.reponses_section_e or {}).get(key, 0)
        scores[dim] += val * poids
        max_scores[dim] += 5 * poids

    # ── Normalisation 0-100 ───────────────────────────────────────────────────
    scores_normalises = {}
    for dim in scores:
        if max_scores[dim] > 0:
            scores_normalises[dim] = round((scores[dim] / max_scores[dim]) * 100, 2)
        else:
            scores_normalises[dim] = 0.0

    return scores_normalises


@router.post(
    "/",
    response_model=ProfilPsychometrique,
    status_code=status.HTTP_201_CREATED,
    summary="Soumettre le questionnaire psychométrique — 28 items RIASEC",
)
def soumettre_questionnaire(
    data: QuestionnaireSubmit,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    CU01 — Étape finale : soumission du questionnaire.
    FastAPI calcule les 6 scores RIASEC, anonymise le profil
    et déclenche la sauvegarde (RD16 : aucune PII transmise au LLM).
    """
    id_bachelier = UUID(current_user["sub"])

    # Vérifier qu'un profil n'existe pas déjà (RD2 : 1 profil par bachelier)
    existing = session.exec(
        select(ProfilPsychometrique).where(
            ProfilPsychometrique.id_bachelier == id_bachelier
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un profil psychométrique existe déjà pour ce bachelier. Utilisez PATCH pour le mettre à jour.",
        )

    # Calcul des scores RIASEC
    scores = calculer_scores_riasec(data)

    profil = ProfilPsychometrique(
        id_bachelier=id_bachelier,
        score_r=scores["R"],
        score_i=scores["I"],
        score_a=scores["A"],
        score_s=scores["S"],
        score_e=scores["E"],
        score_c=scores["C"],
        ressources_financieres=data.ressources_financieres,
        mobilite_geo=data.mobilite_geo,
        horizon_temporel=data.horizon_temporel,
        date_passage=datetime.now(timezone.utc),
    )

    session.add(profil)
    session.commit()
    session.refresh(profil)
    return profil


@router.get(
    "/moi",
    response_model=ProfilPsychometrique,
    summary="Récupérer son propre profil psychométrique",
)
def get_mon_profil(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    id_bachelier = UUID(current_user["sub"])
    profil = session.exec(
        select(ProfilPsychometrique).where(
            ProfilPsychometrique.id_bachelier == id_bachelier
        )
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun profil trouvé — complétez d'abord le questionnaire.",
        )
    return profil


@router.patch(
    "/moi",
    response_model=ProfilPsychometrique,
    summary="Recalculer son profil en soumettant de nouvelles réponses",
)
def mettre_a_jour_profil(
    data: QuestionnaireSubmit,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    id_bachelier = UUID(current_user["sub"])
    profil = session.exec(
        select(ProfilPsychometrique).where(
            ProfilPsychometrique.id_bachelier == id_bachelier
        )
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun profil trouvé — soumettez d'abord le questionnaire via POST.",
        )

    scores = calculer_scores_riasec(data)
    profil.score_r = scores["R"]
    profil.score_i = scores["I"]
    profil.score_a = scores["A"]
    profil.score_s = scores["S"]
    profil.score_e = scores["E"]
    profil.score_c = scores["C"]
    profil.ressources_financieres = data.ressources_financieres
    profil.mobilite_geo = data.mobilite_geo
    profil.horizon_temporel = data.horizon_temporel
    profil.date_passage = datetime.now(timezone.utc)

    session.add(profil)
    session.commit()
    session.refresh(profil)
    return profil