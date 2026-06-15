from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies import get_current_bachelier
from app.models.filiere import Filiere, FiliereCreate, FiliereRead
from app.models.bachelier import Bachelier

router = APIRouter()


# ─── GET /api/filieres ────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[FiliereRead],
    summary="Lister toutes les filières",
)
def list_filieres(
    domaine: Optional[str] = Query(None, description="Filtrer par domaine"),
    search: Optional[str] = Query(None, description="Recherche par nom"),
    session: Session = Depends(get_session),
):
    query = select(Filiere)
    if domaine:
        query = query.where(Filiere.domaine == domaine)
    filieres = session.exec(query).all()
    if search:
        filieres = [
            f for f in filieres
            if search.lower() in f.nom.lower()
        ]
    return filieres


# ─── GET /api/filieres/{id} ───────────────────────────────────────────────────
@router.get(
    "/{id_filiere}",
    response_model=FiliereRead,
    summary="Détail d'une filière",
)
def get_filiere(
    id_filiere: UUID,
    session: Session = Depends(get_session),
):
    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière introuvable",
        )
    return filiere


# ─── POST /api/filieres ───────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=FiliereRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une filière (admin)",
)
def create_filiere(
    data: FiliereCreate,
    session: Session = Depends(get_session),
):
    filiere = Filiere(**data.model_dump())
    session.add(filiere)
    session.commit()
    session.refresh(filiere)
    return filiere

# ─── POST /api/filieres/comparer ─────────────────────────────────────────────
from pydantic import BaseModel as PydanticBase

class ComparerRequest(PydanticBase):
    noms: list[str]

@router.post(
    "/comparer",
    response_model=list[FiliereRead],
    summary="Comparer plusieurs filières par nom",
)
def comparer_filieres(
    data: ComparerRequest,
    session: Session = Depends(get_session),
):
    """Retourne les filières correspondant aux noms fournis (comparaison multicritères)."""
    if not data.noms:
        return []
    filieres = session.exec(
        select(Filiere).where(Filiere.nom.in_(data.noms))
    ).all()
    # Conserver l'ordre de la requête
    ordre = {nom: i for i, nom in enumerate(data.noms)}
    return sorted(filieres, key=lambda f: ordre.get(f.nom, 99))
