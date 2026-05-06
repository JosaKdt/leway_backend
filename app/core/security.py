import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(
    subject: str,
    role: str = "bachelier",
    expires_delta: timedelta | None = None
) -> str:
    expire_minutes = (
        settings.ACCESS_TOKEN_EXPIRE_MINUTES_BACHELIER
        if role == "bachelier"
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN
    )
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=expire_minutes)
    )
    to_encode = {
        "sub": subject,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except Exception:
        return None