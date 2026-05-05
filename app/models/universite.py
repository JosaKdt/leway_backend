from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Float, Integer, Boolean
from typing import Optional
from uuid import UUID, uuid4


class Universite(SQLModel, table=True):
    """
    Table UNIVERSITE — SLR Léway

    Stocke les universités béninoises (publiques et privées).
    accreditation_mesrs / accreditation_cames : validées par l'administrateur backoffice.
    """
    __tablename__ = "universite"

    id_universite: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    nom: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
    # ex: 'public' | 'prive' | 'confessionnel'
    type: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
    )
    localisation: Optional[str] = Field(
        default=None,
        sa_column=Column(String(200), nullable=True),
    )
    cout_annuel_min: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    cout_annuel_max: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    taux_reussite: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )
    accreditation_mesrs: Optional[bool] = Field(
        default=None,
        sa_column=Column(Boolean, nullable=True),
    )
    accreditation_cames: Optional[bool] = Field(
        default=None,
        sa_column=Column(Boolean, nullable=True),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class UniversiteCreate(SQLModel):
    nom: str
    type: Optional[str] = None
    localisation: Optional[str] = None
    cout_annuel_min: Optional[int] = None
    cout_annuel_max: Optional[int] = None
    taux_reussite: Optional[float] = None
    accreditation_mesrs: Optional[bool] = None
    accreditation_cames: Optional[bool] = None


class UniversiteRead(SQLModel):
    id_universite: UUID
    nom: str
    type: Optional[str]
    localisation: Optional[str]
    cout_annuel_min: Optional[int]
    cout_annuel_max: Optional[int]
    taux_reussite: Optional[float]
    accreditation_mesrs: Optional[bool]
    accreditation_cames: Optional[bool]
