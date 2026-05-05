from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Float, Integer, Text, ForeignKey
from typing import Optional
from uuid import UUID, uuid4


class ScoreCompatibilite(SQLModel, table=True):
    """
    Table SCORE_COMPATIBILITE — SLR Léway

    Relation : RECOMMANDATION → SCORE_COMPATIBILITE  (1 — 1..*)
    Un rapport contient au moins un score par filière évaluée.

    Weighted Score = décomposé en 3 composantes :
        score_riasec_match  → 60% — compatibilité profil RIASEC bachelier / profil idéal filière
        score_marche        → 25% — taux d'insertion + salaire médian à 3 ans
        score_ia            → 15% — tendance_ia du secteur (automatisabilité)

    justification_ia : texte généré par le LLM en français naturel (géré par le binôme)
    """
    __tablename__ = "score_compatibilite"

    id_score: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    # ─── Clés étrangères ─────────────────────────────────────────────────────
    id_recommandation: UUID = Field(
        sa_column=Column(
            "id_recommandation",
            ForeignKey("recommandation.id_recommandation", ondelete="CASCADE"),
            nullable=False,
        )
    )
    id_filiere: UUID = Field(
        sa_column=Column(
            "id_filiere",
            ForeignKey("filiere.id_filiere", ondelete="RESTRICT"),
            nullable=False,
        )
    )

    # ─── Weighted Score global ────────────────────────────────────────────────
    score_weighted: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )

    # ─── Décomposition du score (60 / 25 / 15 %) ─────────────────────────────
    score_riasec_match: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )
    score_marche: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )
    score_ia: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )

    # Rang dans le Top 5 (1 = meilleure recommandation)
    classement: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )

    # Texte LLM — généré par le moteur d'inférence (binôme)
    justification_ia: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class ScoreCompatibiliteRead(SQLModel):
    id_score: UUID
    id_recommandation: UUID
    id_filiere: UUID
    score_weighted: Optional[float]
    score_riasec_match: Optional[float]
    score_marche: Optional[float]
    score_ia: Optional[float]
    classement: Optional[int]
    justification_ia: Optional[str]
