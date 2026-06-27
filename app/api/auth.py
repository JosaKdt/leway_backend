from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_bachelier
from app.models.bachelier import Bachelier, BachelierCreate, BachelierRead
from app.models.administrateur import Administrateur
from app.models.representant_universite import RepresentantUniversite, RepresentantCreate
from app.models.demande_representant import DemandeRepresentantCreate
from app.services.email_service import send_otp_bachelier
from pydantic import BaseModel
import random
from datetime import datetime, timedelta, timezone

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

# ─── Devenir représentant (CU06 : demande d'accréditation) ────────────────────
# Workflow self-service : le futur représentant soumet une demande qui part en
# validation chez l'Administrateur (CU10). AUCUN compte n'est créé tant que la
# demande n'est pas validée — le demandeur n'a donc pas d'accès à ce stade.

@router.post(
    "/devenir-representant",
    status_code=status.HTTP_201_CREATED,
    summary="Soumettre une demande pour devenir représentant d'université",
)
def devenir_representant(data: DemandeRepresentantCreate, session: Session = Depends(get_session)):
    from app.models.demande_representant import DemandeRepresentant
    from app.models.universite import Universite
    from app.models.administrateur import Administrateur
    from app.models.notification import creer_notification
    from uuid import UUID as _UUID

    # 1. L'email ne doit pas déjà correspondre à un compte actif
    if email_deja_utilise(data.email, session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email",
        )

    # 2. Refuser une demande déjà en attente pour le même email
    demande_existante = session.exec(
        select(DemandeRepresentant)
        .where(DemandeRepresentant.email == data.email)
        .where(DemandeRepresentant.statut == "en_attente")
    ).first()
    if demande_existante:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une demande est déjà en cours de traitement pour cet email",
        )

    # 3. Vérifier la cohérence de l'établissement (existant OU proposé)
    nom_etablissement = None
    if data.id_universite:
        universite = session.get(Universite, data.id_universite)
        if not universite:
            raise HTTPException(status_code=404, detail="Université introuvable")
        nom_etablissement = universite.nom
    elif data.universite_proposee_nom:
        nom_etablissement = data.universite_proposee_nom
    else:
        raise HTTPException(
            status_code=400,
            detail="Indiquez une université existante (id_universite) ou proposez-en une (universite_proposee_nom)",
        )

    # 4. Créer la demande EN ATTENTE (pas de compte créé)
    demande = DemandeRepresentant(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        telephone=data.telephone,
        mot_de_passe_hash=hash_password(data.mot_de_passe),
        fonction=data.fonction,
        id_universite=data.id_universite,
        universite_proposee_nom=data.universite_proposee_nom,
        universite_proposee_ville=data.universite_proposee_ville,
        dossier=data.dossier,
        statut="en_attente",
    )
    session.add(demande)
    session.flush()

    # 5. Notifier tous les administrateurs
    admins = session.exec(select(Administrateur)).all()
    for a in admins:
        creer_notification(
            session=session,
            destinataire_id=a.id_administrateur,
            destinataire_role="administrateur",
            type="demande_representant",
            titre="Nouvelle demande de représentant 🏛️",
            message=f"{data.prenom} {data.nom} demande à représenter {nom_etablissement}. En attente de validation.",
        )

    session.commit()
    session.refresh(demande)

    return {
        "message": "Votre demande a été soumise. Vous serez notifié après validation par l'administrateur.",
        "id_demande": str(demande.id_demande),
        "statut": demande.statut,
    }
