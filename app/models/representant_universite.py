from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class RepresentantUniversite(SQLModel, table=True):
    """
    Table REPRESENTANT_UNIVERSITE — SLR ORIAB
    Acteur B2B secondaire (Tableau 3 du mémoire)
    Gère le profil de son établissement + consulte les leads qualifiés.
    Token JWT durée : 8h
    """
    __tablename__ = "representant_universite"

    id_representant: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    nom: str = Field(sa_column=Column(String(100), nullable=False))
    prenom: str = Field(sa_column=Column(String(100), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    mot_de_passe_hash: str = Field(sa_column=Column(String(255), nullable=False))
    role: str = Field(
        default="representant",
        sa_column=Column(String(20), nullable=False, server_default="representant"),
    )
    # Lien vers l'université qu'il représente
    id_universite: UUID = Field(
        sa_column=Column(
            "id_universite",
            ForeignKey("universite.id_universite", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class RepresentantCreate(SQLModel):
    nom: str
    prenom: str
    email: str
    mot_de_passe: str
    id_universite: UUID


class RepresentantRead(SQLModel):
    id_representant: UUID
    nom: str
    prenom: str
    email: str
    role: str
    id_universite: UUID
    created_at: Optional[datetime]