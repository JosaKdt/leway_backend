from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class ProfilPsychometrique(SQLModel, table=True):
    """
    Table PROFIL_PSYCHOMETRIQUE — SLR Léway

    Relation : BACHELIER → PROFIL_PSYCHOMETRIQUE  (1 — 1)
    Un bachelier possède exactement un profil psychométrique.

    Les 6 scores RIASEC sont normalisés entre 0 et 100 (moteur géré par le binôme).
    La Section D (Contexte Socioéconomique) alimente UNIQUEMENT les Veto Factors :
    ressources_financieres et mobilite_geo ne participent JAMAIS au calcul RIASEC.
    """
    __tablename__ = "profil_psychometrique"

    id_profil: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    # ─── Clé étrangère vers BACHELIER ─────────────────────────────────────────
    id_bachelier: UUID = Field(
        sa_column=Column(
            "id_bachelier",
            ForeignKey("bachelier.id_bachelier", ondelete="CASCADE"),
            nullable=False,
        )
    )

    # ─── 6 scores RIASEC (Section B principalement + A et E) ─────────────────
    score_r: float = Field(
        sa_column=Column("score_r", Float, nullable=False)
    )
    score_i: float = Field(
        sa_column=Column("score_i", Float, nullable=False)
    )
    score_a: float = Field(
        sa_column=Column("score_a", Float, nullable=False)
    )
    score_s: float = Field(
        sa_column=Column("score_s", Float, nullable=False)
    )
    score_e: float = Field(
        sa_column=Column("score_e", Float, nullable=False)
    )
    score_c: float = Field(
        sa_column=Column("score_c", Float, nullable=False)
    )

    # ─── Veto Factors — Section D (Contexte Socioéconomique) ─────────────────
    # Ne participent PAS au calcul des scores RIASEC
    ressources_financieres: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    mobilite_geo: Optional[bool] = Field(
        default=None,
        sa_column=Column(Boolean, nullable=True),
    )
    # Section C — horizon temporel : 'court' | 'moyen' | 'long'
    horizon_temporel: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True),
    )

    date_passage: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class ProfilPsychometriqueRead(SQLModel):
    id_profil: UUID
    id_bachelier: UUID
    score_r: float
    score_i: float
    score_a: float
    score_s: float
    score_e: float
    score_c: float
    ressources_financieres: Optional[int]
    mobilite_geo: Optional[bool]
    horizon_temporel: Optional[str]
    date_passage: Optional[datetime]
