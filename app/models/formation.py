from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Integer, ForeignKey
from typing import Optional
from uuid import UUID, uuid4


class Formation(SQLModel, table=True):
    """
    Table FORMATION — SLR Léway

    Table de liaison entre FILIERE et UNIVERSITE.
    Une formation = une filière proposée dans une université précise,
    avec ses propres frais d'inscription, durée réelle et places disponibles.
    """
    __tablename__ = "formation"

    id_formation: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    # ─── Clés étrangères ─────────────────────────────────────────────────────
    id_filiere: UUID = Field(
        sa_column=Column(
            "id_filiere",
            ForeignKey("filiere.id_filiere", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    id_universite: UUID = Field(
        sa_column=Column(
            "id_universite",
            ForeignKey("universite.id_universite", ondelete="RESTRICT"),
            nullable=False,
        )
    )

    # ex: 'Licence', 'Master', 'BTS', 'DUT', 'Doctorat', 'Ingénieur'
    diplome: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
    )
    frais_inscription: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    # Durée réelle en années (peut différer de duree_theorique de la filière)
    duree_reelle: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    places_disponibles: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class FormationCreate(SQLModel):
    id_filiere: UUID
    id_universite: UUID
    diplome: Optional[str] = None
    frais_inscription: Optional[int] = None
    duree_reelle: Optional[int] = None
    places_disponibles: Optional[int] = None


class FormationRead(SQLModel):
    id_formation: UUID
    id_filiere: UUID
    id_universite: UUID
    diplome: Optional[str]
    frais_inscription: Optional[int]
    duree_reelle: Optional[int]
    places_disponibles: Optional[int]
