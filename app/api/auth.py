from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_bachelier
from app.models.bachelier import Bachelier, BachelierCreate, BachelierRead
from app.models.administrateur import Administrateur
from app.models.representant_universite import RepresentantUniversite, RepresentantCreate
from pydantic import BaseModel
import random
from datetime import datetime, timedelta, timezone

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    bachelier: BachelierRead


class RepresentantTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    nom: str
    prenom: str
    id_universite: str



class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    nom: str
    prenom: str


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
            detail="Un compte existe deja avec cet email",
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


@router.post(
    "/admin-login",
    response_model=AdminTokenResponse,
    summary="Connexion administrateur",
)
def admin_login(data: LoginRequest, session: Session = Depends(get_session)):
    admin = session.exec(
        select(Administrateur).where(Administrateur.email == data.email)
    ).first()
    if not admin or not verify_password(data.mot_de_passe, admin.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = create_access_token(
        subject=str(admin.id_administrateur),
        role="administrateur",
    )
    return AdminTokenResponse(
        access_token=token,
        role="administrateur",
        nom=admin.nom,
        prenom=admin.prenom,
    )


@router.get(
    "/me",
    response_model=BachelierRead,
    summary="Profil du bachelier connecte",
)
def me(current_bachelier: Bachelier = Depends(get_current_bachelier)):
    return BachelierRead.model_validate(current_bachelier)


@router.post(
    "/send-otp",
    summary="Genere et envoie un code OTP au bachelier",
)
def send_otp(email: str, session: Session = Depends(get_session)):
    bachelier = session.exec(
        select(Bachelier).where(Bachelier.email == email)
    ).first()
    if not bachelier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte associe a cet email",
        )
    if bachelier.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est deja verifie",
        )

    code = str(random.randint(100000, 999999))
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)

    bachelier.otp_code = code
    bachelier.otp_expires_at = expire
    session.add(bachelier)
    session.commit()

    print(f"[OTP MOCK] Code pour {email} : {code} (expire dans 10 min)")

    return {"message": "Code OTP envoye", "expires_in_minutes": 10}


@router.post(
    "/verify-otp",
    response_model=TokenResponse,
    summary="Verifie le code OTP et active le compte",
)
def verify_otp(
    email: str,
    code: str,
    session: Session = Depends(get_session),
):
    bachelier = session.exec(
        select(Bachelier).where(Bachelier.email == email)
    ).first()
    if not bachelier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte associe a cet email",
        )
    if bachelier.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est deja verifie",
        )
    if bachelier.otp_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code OTP incorrect",
        )

    now = datetime.now(timezone.utc)
    if bachelier.otp_expires_at is None or bachelier.otp_expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code OTP expire — demandez un nouveau code",
        )

    bachelier.is_verified = True
    bachelier.otp_code = None
    bachelier.otp_expires_at = None
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
    "/representant-login",
    response_model=RepresentantTokenResponse,
    summary="Connexion représentant d'université",
)
def representant_login(data: LoginRequest, session: Session = Depends(get_session)):
    rep = session.exec(
        select(RepresentantUniversite).where(
            RepresentantUniversite.email == data.email
        )
    ).first()
    if not rep or not verify_password(data.mot_de_passe, rep.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = create_access_token(
        subject=str(rep.id_representant),
        role="representant",
    )
    return RepresentantTokenResponse(
        access_token=token,
        role="representant",
        nom=rep.nom,
        prenom=rep.prenom,
        id_universite=str(rep.id_universite),
    )


@router.post(
    "/representant-register",
    response_model=RepresentantTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription représentant d'université",
)
def representant_register(
    data: RepresentantCreate,
    session: Session = Depends(get_session),
):
    from app.models.representant_universite import RepresentantCreate as RC
    existing = session.exec(
        select(RepresentantUniversite).where(
            RepresentantUniversite.email == data.email
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe deja avec cet email",
        )
    rep = RepresentantUniversite(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        mot_de_passe_hash=hash_password(data.mot_de_passe),
        id_universite=data.id_universite,
    )
    session.add(rep)
    session.commit()
    session.refresh(rep)
    token = create_access_token(
        subject=str(rep.id_representant),
        role="representant",
    )
    return RepresentantTokenResponse(
        access_token=token,
        role="representant",
        nom=rep.nom,
        prenom=rep.prenom,
        id_universite=str(rep.id_universite),
    )