from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_bachelier
from app.models.bachelier import Bachelier, BachelierRead
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()


class BachelierUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    serie_bac: Optional[str] = None
    notes_bac: Optional[Dict[str, Any]] = None


# ─── GET /api/bacheliers/me ───────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=BachelierRead,
    summary="Mon profil complet",
)
def get_my_profile(
    current_bachelier: Bachelier = Depends(get_current_bachelier),
):
    return BachelierRead.model_validate(current_bachelier)


# ─── PATCH /api/bacheliers/me ─────────────────────────────────────────────────
@router.patch(
    "/me",
    response_model=BachelierRead,
    summary="Mettre à jour mon profil",
)
def update_my_profile(
    data: BachelierUpdate,
    current_bachelier: Bachelier = Depends(get_current_bachelier),
    session: Session = Depends(get_session),
):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_bachelier, key, value)
    session.add(current_bachelier)
    session.commit()
    session.refresh(current_bachelier)
    return BachelierRead.model_validate(current_bachelier)