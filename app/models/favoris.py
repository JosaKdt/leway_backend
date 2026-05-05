from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class Favoris(SQLModel, table=True):
    """
    Table FAVORIS — SLR Léway

    Permet au bachelier de sauvegarder des filières ou universités en favoris
    depuis le module de comparaison ou le moteur de recherche.
    id_filiere et id_universite sont tous deux optionnels :
    on peut mettre en favori une filière seule, une université seule, ou les deux.
    """
    __tablename__ = "favoris"

    id_favori: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    # ─── Clés étrangères ─────────────────────────────────────────────────────
    id_bachelier: UUID = Field(
        sa_column=Column(
            "id_bachelier",
            ForeignKey("bachelier.id_bachelier", ondelete="CASCADE"),
            nullable=False,
        )
    )
    id_filiere: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            "id_filiere",
            ForeignKey("filiere.id_filiere", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    id_universite: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            "id_universite",
            ForeignKey("universite.id_universite", ondelete="CASCADE"),
            nullable=True,
        ),
    )

    date_ajout: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class FavorisCreate(SQLModel):
    id_filiere: Optional[UUID] = None
    id_universite: Optional[UUID] = None


class FavorisRead(SQLModel):
    id_favori: UUID
    id_bachelier: UUID
    id_filiere: Optional[UUID]
    id_universite: Optional[UUID]
    date_ajout: Optional[datetime]
