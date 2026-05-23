from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID

from app.core.database import get_session
from app.models.formation import Formation

router = APIRouter()


@router.get("/", response_model=List[Formation], summary="Liste toutes les formations")
def list_formations(
    id_filiere: Optional[UUID] = Query(None, description="Filtrer par filière"),
    id_universite: Optional[UUID] = Query(None, description="Filtrer par université"),
    diplome: Optional[str] = Query(None, description="Filtrer par diplôme ex: Licence, Master"),
    session: Session = Depends(get_session),
):
    query = select(Formation)
    if id_filiere:
        query = query.where(Formation.id_filiere == id_filiere)
    if id_universite:
        query = query.where(Formation.id_universite == id_universite)
    if diplome:
        query = query.where(Formation.diplome == diplome)
    return session.exec(query).all()


@router.get("/{id_formation}", response_model=Formation, summary="Détail d'une formation")
def get_formation(id_formation: UUID, session: Session = Depends(get_session)):
    formation = session.get(Formation, id_formation)
    if not formation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formation introuvable",
        )
    return formation


@router.post("/", response_model=Formation, status_code=status.HTTP_201_CREATED, summary="Créer une formation")
def create_formation(formation: Formation, session: Session = Depends(get_session)):
    session.add(formation)
    session.commit()
    session.refresh(formation)
    return formation


@router.delete("/{id_formation}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer une formation")
def delete_formation(id_formation: UUID, session: Session = Depends(get_session)):
    formation = session.get(Formation, id_formation)
    if not formation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formation introuvable",
        )
    session.delete(formation)
    session.commit()