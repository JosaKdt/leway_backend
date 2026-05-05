from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies import get_current_bachelier
from app.models.favoris import Favoris, FavorisCreate, FavorisRead
from app.models.bachelier import Bachelier

router = APIRouter()


# ─── GET /api/favoris ─────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[FavorisRead],
    summary="Mes filières favorites",
)
def get_favoris(
    current_bachelier: Bachelier = Depends(get_current_bachelier),
    session: Session = Depends(get_session),
):
    favoris = session.exec(
        select(Favoris).where(
            Favoris.id_bachelier == current_bachelier.id_bachelier
        )
    ).all()
    return favoris


# ─── POST /api/favoris ────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=FavorisRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un favori",
)
def add_favori(
    data: FavorisCreate,
    current_bachelier: Bachelier = Depends(get_current_bachelier),
    session: Session = Depends(get_session),
):
    # Vérifier si déjà en favori
    existing = session.exec(
        select(Favoris).where(
            Favoris.id_bachelier == current_bachelier.id_bachelier,
            Favoris.id_filiere == data.id_filiere,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Déjà dans vos favoris",
        )
    favori = Favoris(
        id_bachelier=current_bachelier.id_bachelier,
        **data.model_dump(),
    )
    session.add(favori)
    session.commit()
    session.refresh(favori)
    return favori


# ─── DELETE /api/favoris/{id} ─────────────────────────────────────────────────
@router.delete(
    "/{id_favori}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un favori",
)
def delete_favori(
    id_favori: UUID,
    current_bachelier: Bachelier = Depends(get_current_bachelier),
    session: Session = Depends(get_session),
):
    favori = session.get(Favoris, id_favori)
    if not favori:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favori introuvable",
        )
    if favori.id_bachelier != current_bachelier.id_bachelier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé",
        )
    session.delete(favori)
    session.commit()