from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Float, Integer, Text, String, ForeignKey
from typing import Optional
from uuid import UUID, uuid4


class ScoreCompatibilite(SQLModel, table=True):
    """
    Table SCORE_COMPATIBILITE — SLR ORIAB

    Weighted Score = 3 composantes :
        score_riasec_match  → 60%
        score_marche        → 25%
        score_ia            → 15%
    """
    __tablename__ = "score_compatibilite"

    id_score: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

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

    score_weighted: Optional[float] = Field(
        default=None,
        sa_column=Column(Float, nullable=True),
    )
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
    classement: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    # Raison d'élimination si Veto Factor déclenché
    motif_veto: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )
    # Texte généré par le LLM — géré par le binôme
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
    motif_veto: Optional[str]
    justification_ia: Optional[str]