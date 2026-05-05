from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime


class Bachelier(SQLModel, table=True):
    """
    Table BACHELIER — SLR Léway
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
    # JSONB : stocke les notes par matière  ex: {"Maths": 14, "SVT": 16}
    notes_bac: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    mot_de_passe_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
    date_creation: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )


# ─── Schémas Pydantic (read / create) ────────────────────────────────────────

class BachelierCreate(SQLModel):
    """Données attendues à la création d'un compte bachelier."""
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    serie_bac: Optional[str] = None
    notes_bac: Optional[Dict[str, Any]] = None
    mot_de_passe: str  # mot de passe en clair → sera hashé avant insertion


class BachelierRead(SQLModel):
    """Données renvoyées au frontend (sans le hash du mot de passe)."""
    id_bachelier: UUID
    nom: str
    prenom: str
    email: str
    telephone: Optional[str]
    serie_bac: Optional[str]
    notes_bac: Optional[Dict[str, Any]]
    date_creation: Optional[datetime]
