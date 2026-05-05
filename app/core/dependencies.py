from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.bachelier import Bachelier
from app.models.administrateur import Administrateur

bearer_scheme = HTTPBearer()


def get_current_bachelier(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> Bachelier:
    """
    Dépendance : vérifie le JWT et retourne le bachelier connecté.
    À utiliser sur toutes les routes protégées bachelier.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None or payload.get("role") != "bachelier":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
        )

    bachelier = session.get(Bachelier, payload["sub"])
    if bachelier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bachelier introuvable",
        )
    return bachelier


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> Administrateur:
    """
    Dépendance : vérifie le JWT et retourne l'administrateur connecté.
    À utiliser sur toutes les routes protégées admin.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré — accès admin requis",
        )

    admin = session.get(Administrateur, payload["sub"])
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrateur introuvable",
        )
    return admin
