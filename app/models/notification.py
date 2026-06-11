from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID as PGUUID
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class Notification(SQLModel, table=True):
    """
    Table NOTIFICATION — ORIAB
    destinataire_role : 'representant' | 'administrateur'
    type : 'filiere_validee' | 'filiere_rejetee' | 'nouvelle_soumission' |
           'nouveau_representant' | 'bachelier_interesse' | 'seuil_atteint'
    """
    __tablename__ = "notification"

    id_notification: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    destinataire_id: UUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), nullable=False)
    )
    destinataire_role: str = Field(
        sa_column=Column(String(20), nullable=False)
    )
    type: str = Field(
        sa_column=Column(String(50), nullable=False)
    )
    titre: str = Field(
        sa_column=Column(String(200), nullable=False)
    )
    message: str = Field(
        sa_column=Column(Text, nullable=False)
    )
    lu: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="false")
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default="NOW()",
            nullable=False,
        ),
    )


# ─── Schémas Pydantic ─────────────────────────────────────────────────────────

class NotificationRead(SQLModel):
    id_notification: UUID
    destinataire_id: UUID
    destinataire_role: str
    type: str
    titre: str
    message: str
    lu: bool
    created_at: Optional[datetime]


# ─── Helper ───────────────────────────────────────────────────────────────────

def creer_notification(
    session,
    destinataire_id: UUID,
    destinataire_role: str,
    type: str,
    titre: str,
    message: str,
):
    notif = Notification(
        destinataire_id=destinataire_id,
        destinataire_role=destinataire_role,
        type=type,
        titre=titre,
        message=message,
    )
    session.add(notif)
    # Pas de commit ici — le caller commit
    return notif