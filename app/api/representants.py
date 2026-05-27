from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import Optional
from uuid import UUID

from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.representant_universite import RepresentantUniversite, RepresentantCreate, RepresentantRead
from app.models.universite import Universite
from app.models.score_compatibilite import ScoreCompatibilite
from app.models.recommandation import Recommandation

router = APIRouter()


# ─── Guard représentant ───────────────────────────────────────────────────────

def require_representant(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.get("role") != "representant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve aux representants d'universite",
        )
    representant = session.exec(
        select(RepresentantUniversite).where(
            RepresentantUniversite.id_representant == UUID(current_user["sub"])
        )
    ).first()
    if not representant:
        raise HTTPException(status_code=404, detail="Representant introuvable")
    return representant


# ─── Mon université ───────────────────────────────────────────────────────────

@router.get(
    "/mon-universite",
    response_model=Universite,
    summary="Récupérer le profil de son université",
)
def get_mon_universite(
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    universite = session.get(Universite, representant.id_universite)
    if not universite:
        raise HTTPException(status_code=404, detail="Universite introuvable")
    return universite


@router.patch(
    "/mon-universite",
    response_model=Universite,
    summary="Mettre à jour le profil de son université",
)
def update_mon_universite(
    data: dict,
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    """
    Le représentant peut mettre à jour les infos publiques de son université.
    Les accréditations ne peuvent être modifiées que par un admin.
    """
    universite = session.get(Universite, representant.id_universite)
    if not universite:
        raise HTTPException(status_code=404, detail="Universite introuvable")

    # Champs interdits au représentant — réservés à l'admin
    champs_proteges = {"accreditation_mesrs", "accreditation_cames", "id_universite"}
    for key, value in data.items():
        if key not in champs_proteges:
            setattr(universite, key, value)

    session.add(universite)
    session.commit()
    session.refresh(universite)
    return universite


# ─── Statistiques / Leads qualifiés ──────────────────────────────────────────

@router.get(
    "/stats",
    summary="Statistiques de l'université — leads qualifiés",
)
def get_stats(
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    """
    CU : Gérer Profil établissement (mémoire Fig. 5)
    Retourne les métriques de l'université :
    - Nombre de fois recommandée (Top 1, 2, 3)
    - Score de compatibilité moyen
    - Recommandations totales la concernant
    """
    from app.models.formation import Formation
    from app.models.filiere import Filiere

    id_universite = representant.id_universite

    # Filières proposées par cette université via Formation
    formations = session.exec(
        select(Formation).where(Formation.id_universite == id_universite)
    ).all()
    ids_filieres = [f.id_filiere for f in formations]

    if not ids_filieres:
        return {
            "universite_id": str(id_universite),
            "formations": len(formations),
            "leads_total": 0,
            "leads_top1": 0,
            "score_moyen": 0.0,
            "message": "Aucune formation enregistrée pour cette université.",
        }

    # Scores de compatibilité concernant ces filières
    scores = session.exec(
        select(ScoreCompatibilite).where(
            ScoreCompatibilite.id_filiere.in_(ids_filieres)
        )
    ).all()

    leads_total = len(scores)
    leads_top1  = sum(1 for s in scores if s.classement == 1)
    score_moyen = round(
        sum(s.score_weighted or 0 for s in scores) / leads_total, 2
    ) if leads_total > 0 else 0.0

    return {
        "universite_id":  str(id_universite),
        "formations":     len(formations),
        "leads_total":    leads_total,
        "leads_top1":     leads_top1,
        "score_moyen":    score_moyen,
    }


# ─── Profil représentant ──────────────────────────────────────────────────────

@router.get(
    "/moi",
    response_model=RepresentantRead,
    summary="Profil du représentant connecté",
)
def get_moi(
    representant: RepresentantUniversite = Depends(require_representant),
):
    return representant