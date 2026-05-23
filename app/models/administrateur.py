from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class Administrateur(SQLModel, table=True):
    """
    Table ADMINISTRATEUR — SLR ORIAB
    role      : toujours 'administrateur' — distingue du bachelier dans le JWT
    niveau_acces : droits internes 'super_admin' | 'admin' | 'moderateur'
    Token JWT durée : 8h (ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN=480)
    """
    __tablename__ = "administrateur"

    id_administrateur: UUID = Field(
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
    mot_de_passe_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
    # role Utilisateur : toujours 'administrateur' pour cette table
    role: str = Field(
        default="administrateur",
        sa_column=Column(String(20), nullable=False, server_default="administrateur")
    )
    # niveau_acces : droits internes de l'admin
    niveau_acces: str = Field(
        default="admin",
        sa_column=Column(String(50), nullable=False, server_default="admin")
    )
    date_creation: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class AdministrateurCreate(SQLModel):
    nom: str
    prenom: str
    email: str
    mot_de_passe: str
    niveau_acces: str = "admin"


class AdministrateurRead(SQLModel):
    id_administrateur: UUID
    nom: str
    prenom: str
    email: str
    role: str
    niveau_acces: str
    date_creation: Optional[datetime]