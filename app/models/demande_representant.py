from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID as PGUUID
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class DemandeRepresentant(SQLModel, table=True):
    """
    Table DEMANDE_REPRESENTANT — ORIAB (CU06 « Devenir représentant d'université »)

    Une demande d'accréditation soumise par un futur représentant d'université.
    Tant que l'Administrateur ne l'a pas validée (CU10), aucun compte
    RepresentantUniversite n'est créé : le demandeur n'a donc pas d'accès.

    statut : 'en_attente' | 'validee' | 'refusee'

    Deux cas pour l'établissement :
      - université déjà référencée  → id_universite renseigné
      - nouvel établissement proposé → universite_proposee_nom / _ville renseignés,
        l'université est créée au moment de la validation.
    """
    __tablename__ = "demande_representant"

    id_demande: UUID = Field(default_factory=uuid4, primary_key=True)

    # ─── Identité du demandeur ───────────────────────────────────────────────
    nom: str = Field(sa_column=Column(String(100), nullable=False))
    prenom: str = Field(sa_column=Column(String(100), nullable=False))
    email: str = Field(sa_column=Column(String(255), nullable=False))
    telephone: Optional[str] = Field(default=None, sa_column=Column(String(20), nullable=True))
    # Mot de passe choisi à l'inscription, conservé haché jusqu'à la validation
    mot_de_passe_hash: str = Field(sa_column=Column(String(255), nullable=False))
    fonction: Optional[str] = Field(default=None, sa_column=Column(String(120), nullable=True))

    # ─── Établissement : soit existant, soit proposé ─────────────────────────
    id_universite: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("universite.id_universite", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    universite_proposee_nom: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    universite_proposee_ville: Optional[str] = Field(default=None, sa_column=Column(String(120), nullable=True))

    # ─── Dossier / justificatifs ─────────────────────────────────────────────
    # Lien vers les pièces (mandat, justificatif) ou note de motivation
    dossier: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    # ─── Suivi ───────────────────────────────────────────────────────────────
    statut: str = Field(
        default="en_attente",
        sa_column=Column(String(20), nullable=False, server_default="en_attente"),
    )
    motif_refus: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), server_default="NOW()", nullable=False),
    )
    traite_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class DemandeRepresentantCreate(SQLModel):
    """Payload public du formulaire « Devenir représentant »."""
    nom: str
    prenom: str
    email: str
    mot_de_passe: str
    telephone: Optional[str] = None
    fonction: Optional[str] = None
    # Cas 1 : université existante
    id_universite: Optional[UUID] = None
    # Cas 2 : nouvel établissement proposé
    universite_proposee_nom: Optional[str] = None
    universite_proposee_ville: Optional[str] = None
    dossier: Optional[str] = None


class DemandeRepresentantRead(SQLModel):
    id_demande: UUID
    nom: str
    prenom: str
    email: str
    telephone: Optional[str]
    fonction: Optional[str]
    id_universite: Optional[UUID]
    universite_proposee_nom: Optional[str]
    universite_proposee_ville: Optional[str]
    dossier: Optional[str]
    statut: str
    motif_refus: Optional[str]
    created_at: Optional[datetime]
    traite_at: Optional[datetime]


class RefusDemandeRequest(SQLModel):
    motif_refus: Optional[str] = None
