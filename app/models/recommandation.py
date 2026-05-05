from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class Recommandation(SQLModel, table=True):
    """
    Table RECOMMANDATION — SLR Léway

    Relation : BACHELIER → RECOMMANDATION  (1 — 0..*)
    Un bachelier peut générer plusieurs rapports au fil du temps.

    statut : 'generee' | 'consultee' | 'archivee'
    version_algo : ex '1.0', '1.1', '2.0' — permet l'amélioration rétrospective
    """
    __tablename__ = "recommandation"

    id_recommandation: UUID = Field(
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

    date_generation: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )
    version_algo: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True),
    )
    # DEFAULT 'generee' — conforme au script CREATE TABLE du mémoire
    statut: str = Field(
        sa_column=Column(
            String(20),
            nullable=False,
            server_default="generee",
        )
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class RecommandationRead(SQLModel):
    id_recommandation: UUID
    id_bachelier: UUID
    date_generation: Optional[datetime]
    version_algo: Optional[str]
    statut: str
