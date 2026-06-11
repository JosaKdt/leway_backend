from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4


class Filiere(SQLModel, table=True):
    """
    Table FILIERE — SLR ORIAB
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

    id_filiere: UUID = Field(default_factory=uuid4, primary_key=True)

    nom: str = Field(sa_column=Column(String(200), nullable=False))

    domaine: Optional[str] = Field(
        default=None, sa_column=Column(String(100), nullable=True))

    duree_theorique: Optional[int] = Field(
        default=None, sa_column=Column(Integer, nullable=True))

    salaire_median_p50: Optional[int] = Field(
        default=None, sa_column=Column(Integer, nullable=True))

    taux_insertion: Optional[float] = Field(
        default=None, sa_column=Column(Float, nullable=True))

    indice_saturation: Optional[float] = Field(
        default=None, sa_column=Column(Float, nullable=True))

    tendance_ia: Optional[int] = Field(
        default=None, sa_column=Column(Integer, nullable=True))

    # H3 — variable explicite (alignement curricula/marché)
    tendance_curricula_marche: Optional[float] = Field(
        default=None, sa_column=Column(Float, nullable=True))

    # Profil RIASEC idéal de la filière  ex: {"R": 20, "I": 80, ...}
    profil_riasec_dominant: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True))

    # Règles d'élimination — appliquées avant le moteur LLM
    veto_factors: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True))

    # Poids de scoring spécifiques à la filière
    poids_scoring: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True))

    # ── Nouveaux champs ───────────────────────────────────────────────────────

    # Texte court décrivant la filière (affiché dans les cards)
    description: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True))

    # Liste des débouchés métiers  ex: ["Ingénieur logiciel", "Data Analyst"]
    debouches: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True))

    # Niveau d'admission requis  ex: "Bac", "Bac+2", "Bac+3"
    niveau_admission: Optional[str] = Field(
        default=None, sa_column=Column(String(20), nullable=True))

    # Accréditation MESRS de la filière (distincte de celle de l'université)
    accreditation_mesrs: Optional[bool] = Field(
        default=None, sa_column=Column(Boolean, nullable=True))

    # Accréditation CAMES de la filière
    accreditation_cames: Optional[bool] = Field(
        default=None, sa_column=Column(Boolean, nullable=True))

    # Fourchette de coût annuel en FCFA
    cout_annuel_min: Optional[int] = Field(
        default=None, sa_column=Column(Integer, nullable=True))

    cout_annuel_max: Optional[int] = Field(
        default=None, sa_column=Column(Integer, nullable=True))

    # Langue d'enseignement  ex: "Français", "Anglais", "Bilingue"
    langue_enseignement: Optional[str] = Field(
        default=None, sa_column=Column(String(20), nullable=True))

    # Taux de réussite moyen des étudiants (0.0 à 1.0)
    taux_reussite: Optional[float] = Field(
        default=None, sa_column=Column(Float, nullable=True))

    # Nombre de fois recommandée par le moteur (calculé automatiquement)
    popularite: Optional[int] = Field(
        default=0, sa_column=Column(Integer, nullable=True, server_default="0"))

    # Statut de validation — 'active' | 'en_attente' | 'rejetee'
    statut: Optional[str] = Field(
        default='active',
        sa_column=Column(String(20), nullable=False, server_default='active'))


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
    veto_factors: Optional[Dict[str, Any]] = None
    poids_scoring: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    debouches: Optional[Dict[str, Any]] = None
    niveau_admission: Optional[str] = None
    accreditation_mesrs: Optional[bool] = None
    accreditation_cames: Optional[bool] = None
    cout_annuel_min: Optional[int] = None
    cout_annuel_max: Optional[int] = None
    langue_enseignement: Optional[str] = None
    taux_reussite: Optional[float] = None


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
    veto_factors: Optional[Dict[str, Any]]
    poids_scoring: Optional[Dict[str, Any]]
    description: Optional[str]
    debouches: Optional[Dict[str, Any]]
    niveau_admission: Optional[str]
    accreditation_mesrs: Optional[bool]
    accreditation_cames: Optional[bool]
    cout_annuel_min: Optional[int]
    cout_annuel_max: Optional[int]
    langue_enseignement: Optional[str]
    taux_reussite: Optional[float]
    popularite: Optional[int]
    statut: Optional[str] = None