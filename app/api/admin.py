from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.filiere import Filiere, FiliereCreate, FiliereRead
from app.models.universite import Universite, UniversiteCreate, UniversiteRead
from app.models.recommandation import Recommandation

router = APIRouter()


# ─── Garde admin ──────────────────────────────────────────────────────────────

def require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != "administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve aux administrateurs",
        )
    return current_user


# ─── Métriques ────────────────────────────────────────────────────────────────

@router.get("/metriques", summary="Tableau de bord — métriques algorithmiques")
def get_metriques(
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from app.models.bachelier import Bachelier
    from app.models.profil_psychometrique import ProfilPsychometrique

    nb_bacheliers     = len(session.exec(select(Bachelier)).all())
    nb_filieres       = len(session.exec(select(Filiere)).all())
    nb_universites    = len(session.exec(select(Universite)).all())
    nb_recommandations = len(session.exec(select(Recommandation)).all())
    nb_profils        = len(session.exec(select(ProfilPsychometrique)).all())
    nb_generees       = len(session.exec(select(Recommandation).where(Recommandation.statut == "generee")).all())
    nb_consultees     = len(session.exec(select(Recommandation).where(Recommandation.statut == "consultee")).all())

    taux_completion = round(nb_profils / nb_bacheliers, 3) if nb_bacheliers > 0 else 0.0

    return {
        "bacheliers":      nb_bacheliers,
        "filieres":        nb_filieres,
        "universites":     nb_universites,
        "taux_completion": taux_completion,
        "recommandations": {
            "total":     nb_recommandations,
            "generees":  nb_generees,
            "consultees": nb_consultees,
        },
    }

# ─── Gestion des filières ─────────────────────────────────────────────────────

@router.get(
    "/filieres",
    response_model=List[FiliereRead],
    summary="Admin — liste toutes les filières",
)
def admin_list_filieres(
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    return session.exec(select(Filiere)).all()


@router.post(
    "/filieres",
    response_model=FiliereRead,
    status_code=status.HTTP_201_CREATED,
    summary="Admin — créer une filière",
)
def admin_create_filiere(
    data: FiliereCreate,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    filiere = Filiere(**data.model_dump())
    session.add(filiere)
    session.commit()
    session.refresh(filiere)
    return filiere


@router.patch(
    "/filieres/{id_filiere}",
    response_model=FiliereRead,
    summary="Admin — mettre à jour une filière",
)
def admin_update_filiere(
    id_filiere: UUID,
    data: dict,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere introuvable")
    for key, value in data.items():
        setattr(filiere, key, value)
    session.add(filiere)
    session.commit()
    session.refresh(filiere)
    return filiere


@router.delete(
    "/filieres/{id_filiere}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Admin — supprimer une filière",
)
def admin_delete_filiere(
    id_filiere: UUID,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere introuvable")
    session.delete(filiere)
    session.commit()


# ─── Validation accréditations ────────────────────────────────────────────────

@router.patch(
    "/universites/{id_universite}/accreditation",
    response_model=UniversiteRead,
    summary="Admin — valider accréditation MESRS / CAMES",
)
def valider_accreditation(
    id_universite: UUID,
    accreditation_mesrs: bool = None,
    accreditation_cames: bool = None,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    """
    CU : Valider Accréditation (mémoire II.3.1 — diagramme de cas d'utilisation)
    """
    universite = session.get(Universite, id_universite)
    if not universite:
        raise HTTPException(status_code=404, detail="Universite introuvable")
    if accreditation_mesrs is not None:
        universite.accreditation_mesrs = accreditation_mesrs
    if accreditation_cames is not None:
        universite.accreditation_cames = accreditation_cames
    session.add(universite)
    session.commit()
    session.refresh(universite)
    return universite


# ─── Rapports agrégés ─────────────────────────────────────────────────────────

@router.get(
    "/rapports/filieres-populaires",
    summary="Admin — filières les plus recommandées (anonymisé)",
)
def filieres_populaires(
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    """
    Rapport agrégé anonymisé pour les partenaires institutionnels.
    Bloc 5 — Back-office administratif (mémoire II.2.1)
    """
    from app.models.score_compatibilite import ScoreCompatibilite
    from sqlmodel import func

    resultats = session.exec(
        select(
            ScoreCompatibilite.id_filiere,
            func.count(ScoreCompatibilite.id_filiere).label("nb_recommandations"),
            func.avg(ScoreCompatibilite.score_weighted).label("score_moyen"),
        ).where(ScoreCompatibilite.classement == 1)
        .group_by(ScoreCompatibilite.id_filiere)
        .order_by(func.count(ScoreCompatibilite.id_filiere).desc())
        .limit(10)
    ).all()

    return [
        {
            "id_filiere": str(r.id_filiere),
            "nb_fois_top1": r.nb_recommandations,
            "score_weighted_moyen": round(r.score_moyen or 0, 2),
        }
        for r in resultats
    ]