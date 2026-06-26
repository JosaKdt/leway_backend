from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_bachelier
from app.models.bachelier import Bachelier, BachelierCreate, BachelierRead
from app.models.administrateur import Administrateur
from app.models.representant_universite import RepresentantUniversite, RepresentantCreate
from app.services.email_service import send_otp_bachelier
from pydantic import BaseModel
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


# ─── Helper : vérification email cross-tables ─────────────────────────────────

def email_deja_utilise(email: str, session: Session) -> bool:
    """Vérifie si l'email existe dans bachelier, representant ou administrateur."""
    if session.exec(select(Bachelier).where(Bachelier.email == email)).first():
        return True
    if session.exec(select(RepresentantUniversite).where(RepresentantUniversite.email == email)).first():
        return True
    if session.exec(select(Administrateur).where(Administrateur.email == email)).first():
        return True
    return False


# ─── Schémas ──────────────────────────────────────────────────────────────────

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


# ─── Inscription bachelier ────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouveau bachelier",
)
def register(data: BachelierCreate, session: Session = Depends(get_session)):
    if email_deja_utilise(data.email, session):
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
    token = create_access_token(subject=str(bachelier.id_bachelier), role="bachelier")
    return TokenResponse(access_token=token, bachelier=BachelierRead.model_validate(bachelier))


# ─── Connexion unifiée ────────────────────────────────────────────────────────

@router.post("/login", summary="Connexion unifiée — détecte automatiquement le type de compte")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    # 1. Admin ?
    admin = session.exec(select(Administrateur).where(Administrateur.email == data.email)).first()
    if admin and verify_password(data.mot_de_passe, admin.mot_de_passe_hash):
        token = create_access_token(subject=str(admin.id_administrateur), role="administrateur")
        return {"access_token": token, "token_type": "bearer", "role": "administrateur"}

    # 2. Représentant ?
    rep = session.exec(select(RepresentantUniversite).where(RepresentantUniversite.email == data.email)).first()
    if rep and verify_password(data.mot_de_passe, rep.mot_de_passe_hash):
        token = create_access_token(subject=str(rep.id_representant), role="representant")
        return {"access_token": token, "token_type": "bearer", "role": "representant"}

    # 3. Bachelier ?
    bachelier = session.exec(select(Bachelier).where(Bachelier.email == data.email)).first()
    if bachelier and verify_password(data.mot_de_passe, bachelier.mot_de_passe_hash):
        token = create_access_token(subject=str(bachelier.id_bachelier), role="bachelier")
        return {"access_token": token, "token_type": "bearer", "role": "bachelier"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")


# ─── Connexion admin ──────────────────────────────────────────────────────────

@router.post("/admin-login", response_model=AdminTokenResponse, summary="Connexion administrateur")
def admin_login(data: LoginRequest, session: Session = Depends(get_session)):
    admin = session.exec(select(Administrateur).where(Administrateur.email == data.email)).first()
    if not admin or not verify_password(data.mot_de_passe, admin.mot_de_passe_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    token = create_access_token(subject=str(admin.id_administrateur), role="administrateur")
    return AdminTokenResponse(access_token=token, role="administrateur", nom=admin.nom, prenom=admin.prenom)


# ─── Profil bachelier connecté ────────────────────────────────────────────────

@router.get("/me", response_model=BachelierRead, summary="Profil du bachelier connecté")
def me(current_bachelier: Bachelier = Depends(get_current_bachelier)):
    return BachelierRead.model_validate(current_bachelier)


# ─── OTP ──────────────────────────────────────────────────────────────────────

@router.post("/send-otp", summary="Génère et envoie un code OTP au bachelier")
def send_otp(email: str, session: Session = Depends(get_session)):
    bachelier = session.exec(select(Bachelier).where(Bachelier.email == email)).first()
    if not bachelier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun compte associé à cet email")
    if bachelier.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce compte est déjà vérifié")

    code = str(random.randint(100000, 999999))
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    bachelier.otp_code = code
    bachelier.otp_expires_at = expire
    session.add(bachelier)
    session.commit()

    email_envoye = send_otp_bachelier(email=email, prenom=bachelier.prenom, code=code)
    if not email_envoye:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de l'envoi de l'email OTP")

    return {"message": "Code OTP envoyé", "expires_in_minutes": 10}


@router.post("/verify-otp", response_model=TokenResponse, summary="Vérifie le code OTP et active le compte")
def verify_otp(email: str, code: str, session: Session = Depends(get_session)):
    bachelier = session.exec(select(Bachelier).where(Bachelier.email == email)).first()
    if not bachelier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun compte associé à cet email")
    if bachelier.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce compte est déjà vérifié")
    if bachelier.otp_code != code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code OTP incorrect")

    now = datetime.now(timezone.utc)
    if bachelier.otp_expires_at is None or bachelier.otp_expires_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code OTP expiré — demandez un nouveau code")

    bachelier.is_verified = True
    bachelier.otp_code = None
    bachelier.otp_expires_at = None
    session.add(bachelier)
    session.commit()
    session.refresh(bachelier)

    token = create_access_token(subject=str(bachelier.id_bachelier), role="bachelier")
    return TokenResponse(access_token=token, bachelier=BachelierRead.model_validate(bachelier))


# ─── Connexion représentant ───────────────────────────────────────────────────

@router.post("/representant-login", response_model=RepresentantTokenResponse, summary="Connexion représentant d'université")
def representant_login(data: LoginRequest, session: Session = Depends(get_session)):
    rep = session.exec(select(RepresentantUniversite).where(RepresentantUniversite.email == data.email)).first()
    if not rep or not verify_password(data.mot_de_passe, rep.mot_de_passe_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    token = create_access_token(subject=str(rep.id_representant), role="representant")
    return RepresentantTokenResponse(
        access_token=token, role="representant",
        nom=rep.nom, prenom=rep.prenom, id_universite=str(rep.id_universite),
    )


# ─── Inscription représentant ─────────────────────────────────────────────────

@router.post(
    "/representant-register",
    response_model=RepresentantTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription représentant d'université",
)
def representant_register(data: RepresentantCreate, session: Session = Depends(get_session)):
    if email_deja_utilise(data.email, session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email",
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
    token = create_access_token(subject=str(rep.id_representant), role="representant")
    return RepresentantTokenResponse(
        access_token=token, role="representant",
        nom=rep.nom, prenom=rep.prenom, id_universite=str(rep.id_universite),
    )

# ─── Changement mot de passe bachelier ───────────────────────────────────────

class ChangerMotDePasseRequest(BaseModel):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str
    confirmation: str

@router.patch("/changer-mot-de-passe", summary="Changer son mot de passe")
def changer_mot_de_passe(
    data: ChangerMotDePasseRequest,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    bachelier = session.get(Bachelier, UUID(current_user["sub"]))
    if not bachelier:
        raise HTTPException(status_code=404, detail="Compte introuvable")
    if not verify_password(data.ancien_mot_de_passe, bachelier.mot_de_passe_hash):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
    if data.nouveau_mot_de_passe != data.confirmation:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")
    if len(data.nouveau_mot_de_passe) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères")
    bachelier.mot_de_passe_hash = hash_password(data.nouveau_mot_de_passe)
    session.add(bachelier)
    session.commit()
    return {"message": "Mot de passe modifié avec succès"}    