from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Float, Integer, CheckConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class Filiere(SQLModel, table=True):
    """
    Table FILIERE — SLR Léway

    Base de connaissances des filières béninoises.
    Variable tendance_curricula_marche : facteur aggravant indépendant (H3)
    traitée comme variable EXPLICITE dans le Weighted Score, distincte de tendance_ia.

    tendance_ia : échelle 0-3 (automatisabilité du secteur)
        0 = En forte croissance
        1 = Stable
        2 = En transformation
        3 = Fortement affecté par l'IA
    """
    __tablename__ = "filiere"

    __table_args__ = (
        CheckConstraint("tendance_ia BETWEEN 0 AND 3", name="ck_filiere_tendance_ia"),
    )

    id_filiere: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    nom: str = Field(
        sa_column=Column(String(200), nullable=False)
    )
    domaine: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
    )
    duree_theorique: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    salaire_median_p50: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    taux_insertion: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )
    indice_saturation: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )
    # Échelle 0-3 — CHECK(tendance_ia BETWEEN 0 AND 3)
    tendance_ia: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    # H3 — variable explicite et indépendante (alignement curricula/marché)
    tendance_curricula_marche: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )
    # JSONB : profil RIASEC idéal de la filière  ex: {"R": 20, "I": 80, "A": 40, ...}
    profil_riasec_dominant: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class FiliereCreate(SQLModel):
    nom: str
    domaine: Optional[str] = None
    duree_theorique: Optional[int] = None
    salaire_median_p50: Optional[int] = None
    taux_insertion: Optional[float] = None
    indice_saturation: Optional[float] = None
    tendance_ia: Optional[int] = None
    tendance_curricula_marche: Optional[float] = None
    profil_riasec_dominant: Optional[Dict[str, Any]] = None


class FiliereRead(SQLModel):
    id_filiere: UUID
    nom: str
    domaine: Optional[str]
    duree_theorique: Optional[int]
    salaire_median_p50: Optional[int]
    taux_insertion: Optional[float]
    indice_saturation: Optional[float]
    tendance_ia: Optional[int]
    tendance_curricula_marche: Optional[float]
    profil_riasec_dominant: Optional[Dict[str, Any]]
