from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID

from app.core.database import get_session
from app.models.universite import Universite

router = APIRouter()


@router.get("/", response_model=List[Universite], summary="Liste toutes les universités")
def list_universites(
    type: Optional[str] = Query(None, description="Filtrer par type : public | prive | confessionnel"),
    localisation: Optional[str] = Query(None, description="Filtrer par ville"),
    accreditation_mesrs: Optional[bool] = Query(None),
    accreditation_cames: Optional[bool] = Query(None),
    session: Session = Depends(get_session),
):
    query = select(Universite)
    if type:
        query = query.where(Universite.type == type)
    if localisation:
        query = query.where(Universite.localisation == localisation)
    if accreditation_mesrs is not None:
        query = query.where(Universite.accreditation_mesrs == accreditation_mesrs)
    if accreditation_cames is not None:
        query = query.where(Universite.accreditation_cames == accreditation_cames)
    return session.exec(query).all()


@router.get("/{id_universite}", response_model=Universite, summary="Détail d'une université")
def get_universite(id_universite: UUID, session: Session = Depends(get_session)):
    universite = session.get(Universite, id_universite)
    if not universite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Université introuvable",
        )
    return universite


@router.post("/", response_model=Universite, status_code=status.HTTP_201_CREATED, summary="Créer une université")
def create_universite(universite: Universite, session: Session = Depends(get_session)):
    session.add(universite)
    session.commit()
    session.refresh(universite)
    return universite


@router.patch("/{id_universite}", response_model=Universite, summary="Mettre à jour une université")
def update_universite(
    id_universite: UUID,
    data: dict,
    session: Session = Depends(get_session),
):
    universite = session.get(Universite, id_universite)
    if not universite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Université introuvable",
        )
    for key, value in data.items():
        setattr(universite, key, value)
    session.add(universite)
    session.commit()
    session.refresh(universite)
    return universite