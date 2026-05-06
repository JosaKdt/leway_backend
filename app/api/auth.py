from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_bachelier
from app.models.bachelier import Bachelier, BachelierCreate, BachelierRead
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    bachelier: BachelierRead


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouveau bachelier",
)
def register(data: BachelierCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Bachelier).where(Bachelier.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email",
        )
    bachelier = Bachelier(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        telephone=data.telephone,
        serie_bac=data.serie_bac,
        notes_bac=data.notes_bac,
        mot_de_passe_hash=hash_password(data.mot_de_passe),
    )
    session.add(bachelier)
    session.commit()
    session.refresh(bachelier)
    token = create_access_token(
        subject=str(bachelier.id_bachelier),
        role="bachelier",
    )
    return TokenResponse(
        access_token=token,
        bachelier=BachelierRead.model_validate(bachelier),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Connexion bachelier — retourne un JWT",
)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    bachelier = session.exec(
        select(Bachelier).where(Bachelier.email == data.email)
    ).first()
    if not bachelier or not verify_password(data.mot_de_passe, bachelier.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = create_access_token(
        subject=str(bachelier.id_bachelier),
        role="bachelier",
    )
    return TokenResponse(
        access_token=token,
        bachelier=BachelierRead.model_validate(bachelier),
    )


@router.get(
    "/me",
    response_model=BachelierRead,
    summary="Profil du bachelier connecté",
)
def me(current_bachelier: Bachelier = Depends(get_current_bachelier)):
    return BachelierRead.model_validate(current_bachelier)