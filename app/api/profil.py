"""
ORIAB — api/profil.py
CU01 — Soumission du questionnaire psychométrique RIASEC.

Banque de questions v2 :
  GET  /api/profil/items → tire 29 items depuis items_bank.json (4/dim + 5 VETO)
  POST /api/profil/      → calcule les 6 scores RIASEC et les persiste
  GET  /api/profil/moi   → scores RIASEC du bachelier connecté
  PATCH /api/profil/moi  → recalcul avec nouvelles réponses

Format réponses : {'B_R_01': 4, 'B_I_03': 3, ..., 'Q18': 2, ...} — Likert 1-5.
Section D (Q18-Q22, dimension=VETO) présente mais JAMAIS dans les scores RIASEC.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.profil_psychometrique import ProfilPsychometrique
from app.scoring.riasec import calculer_scores_riasec, dimension_dominante, tirer_session

router = APIRouter()


class QuestionnaireSubmit(BaseModel):
    """
    Réponses aux items du questionnaire RIASEC.
    Format : {'B_R_01': 4, 'B_I_03': 3, ..., 'Q18': 2} — Likert 1-5.
    Les IDs correspondent aux items retournés par GET /api/profil/items.
    Section D (Q18-Q22) = Veto Factors — présents mais JAMAIS dans les scores RIASEC.
    """
    reponses: dict[str, int]
    ressources_financieres: Optional[int] = None   # tranche 1-4
    mobilite_geo: Optional[bool] = None
    horizon_temporel: Optional[str] = None          # 'court' | 'moyen' | 'long'


class ProfilResponse(BaseModel):
    id_profil: UUID
    id_bachelier: UUID
    score_r: float
    score_i: float
    score_a: float
    score_s: float
    score_e: float
    score_c: float
    dimension_dominante: str
    ressources_financieres: Optional[int]
    mobilite_geo: Optional[bool]
    horizon_temporel: Optional[str]
    date_passage: Optional[datetime]


@router.get(
    "/items",
    summary="Banque RIASEC — tirage de 29 items (4 par dimension + 5 VETO)"
)
def get_items():
    """
    Retourne une session de 29 items tirés aléatoirement depuis la banque :
    - 4 items par dimension RIASEC (6 × 4 = 24 items RIASEC)
    - 5 items VETO fixes (Section D — contraintes pratiques)

    Le résultat est fiable quelle que soit la combinaison de 4 items tirée
    (normalisation automatique par rapport aux items de la session).
    """
    items = tirer_session()
    return {
        "items": items,
        "total": len(items),
        "riasec_items": len([i for i in items if i["dimension"] != "VETO"]),
        "veto_items": len([i for i in items if i["dimension"] == "VETO"]),
        "sections": ["A", "B", "C", "D", "E"],
        "note": "Session aléatoire — 4 items par dimension depuis banque de 48 items"
    }


def _build_response(profil: ProfilPsychometrique) -> ProfilResponse:
    scores = {
        "R": profil.score_r, "I": profil.score_i, "A": profil.score_a,
        "S": profil.score_s, "E": profil.score_e, "C": profil.score_c,
    }
    return ProfilResponse(
        id_profil=profil.id_profil,
        id_bachelier=profil.id_bachelier,
        score_r=profil.score_r,
        score_i=profil.score_i,
        score_a=profil.score_a,
        score_s=profil.score_s,
        score_e=profil.score_e,
        score_c=profil.score_c,
        dimension_dominante=dimension_dominante(scores),
        ressources_financieres=profil.ressources_financieres,
        mobilite_geo=profil.mobilite_geo,
        horizon_temporel=profil.horizon_temporel,
        date_passage=profil.date_passage,
    )


@router.post(
    "/",
    response_model=ProfilResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CU01 — Soumettre le questionnaire et calculer les scores RIASEC"
)
def soumettre_questionnaire(
    data: QuestionnaireSubmit,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Calcule les 6 scores RIASEC depuis les réponses soumises et les persiste.
    Les items VETO (Q18-Q22) sont ignorés du calcul psychométrique.
    """
    id_bachelier = UUID(current_user["sub"])
    existing = session.exec(
        select(ProfilPsychometrique).where(
            ProfilPsychometrique.id_bachelier == id_bachelier
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Profil déjà existant. Utilisez PATCH /api/profil/moi pour recalculer."
        )

    try:
        scores = calculer_scores_riasec(data.reponses)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

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
    return _build_response(profil)


@router.get(
    "/moi",
    response_model=ProfilResponse,
    summary="Mon profil RIASEC — scores calculés"
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
            status_code=404,
            detail="Aucun profil — complétez d'abord le questionnaire via POST /api/profil/"
        )
    return _build_response(profil)


@router.patch(
    "/moi",
    response_model=ProfilResponse,
    summary="Recalculer mon profil avec de nouvelles réponses"
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
            status_code=404,
            detail="Aucun profil — soumettez d'abord via POST /api/profil/"
        )
    try:
        scores = calculer_scores_riasec(data.reponses)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    profil.score_r = scores["R"]
    profil.score_i = scores["I"]
    profil.score_a = scores["A"]
    profil.score_s = scores["S"]
    profil.score_e = scores["E"]
    profil.score_c = scores["C"]
    if data.ressources_financieres is not None:
        profil.ressources_financieres = data.ressources_financieres
    if data.mobilite_geo is not None:
        profil.mobilite_geo = data.mobilite_geo
    if data.horizon_temporel is not None:
        profil.horizon_temporel = data.horizon_temporel
    profil.date_passage = datetime.now(timezone.utc)

    session.add(profil)
    session.commit()
    session.refresh(profil)
    return _build_response(profil)
