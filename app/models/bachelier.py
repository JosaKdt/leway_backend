from sqlmodel import Boolean, SQLModel, Field
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime


class Bachelier(SQLModel, table=True):
    """
    Table BACHELIER — SLR ORIAB
    Clé primaire UUID pour protection contre les attaques IDOR.
    """
    __tablename__ = "bachelier"

    id_bachelier: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    nom: str = Field(
        sa_column=Column(String(100), nullable=False)
    )
    prenom: str = Field(
        sa_column=Column(String(100), nullable=False)
    )
    email: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False)
    )
    telephone: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True)
    )
    serie_bac: Optional[str] = Field(
        default=None,
        sa_column=Column(String(10), nullable=True)
    )
    notes_bac: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    mot_de_passe_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    role: str = Field(
        default="bachelier",
        sa_column=Column(String(20), nullable=False, server_default="bachelier")
    )

    date_creation: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            onupdate=text("NOW()"),
            nullable=True,
        ),
    )


    is_verified: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="false")
    )
    otp_code: Optional[str] = Field(
        default=None,
        sa_column=Column(String(6), nullable=True)
    )
    otp_expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True)
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class BachelierCreate(SQLModel):
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    serie_bac: Optional[str] = None
    notes_bac: Optional[Dict[str, Any]] = None
    mot_de_passe: str


class BachelierRead(SQLModel):
    id_bachelier: UUID
    nom: str
    prenom: str
    email: str
    telephone: Optional[str]
    serie_bac: Optional[str]
    notes_bac: Optional[Dict[str, Any]]
    date_creation: Optional[datetime]
    updated_at: Optional[datetime]