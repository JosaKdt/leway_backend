from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.notification import Notification, NotificationRead
from app.models.representant_universite import RepresentantUniversite
from app.models.administrateur import Administrateur

router = APIRouter()


# ─── Guard générique ──────────────────────────────────────────────────────────

def get_current_identity(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    role = current_user.get("role")
    uid  = UUID(current_user["sub"])
    if role not in ("representant", "administrateur"):
        raise HTTPException(status_code=403, detail="Accès refusé")
    return {"uid": uid, "role": role}


# ─── GET /notifications — mes notifications ───────────────────────────────────

@router.get(
    "/",
    response_model=List[NotificationRead],
    summary="Mes notifications",
)
def get_notifications(
    identity=Depends(get_current_identity),
    session: Session = Depends(get_session),
):
    notifs = session.exec(
        select(Notification)
        .where(Notification.destinataire_id == identity["uid"])
        .where(Notification.destinataire_role == identity["role"])
        .order_by(Notification.created_at.desc())
        .limit(50)
    ).all()
    return notifs


# ─── GET /notifications/non-lues — compteur ───────────────────────────────────

@router.get(
    "/non-lues",
    summary="Nombre de notifications non lues",
)
def count_non_lues(
    identity=Depends(get_current_identity),
    session: Session = Depends(get_session),
):
    notifs = session.exec(
        select(Notification)
        .where(Notification.destinataire_id == identity["uid"])
        .where(Notification.destinataire_role == identity["role"])
        .where(Notification.lu == False)
    ).all()
    return {"count": len(notifs)}


# ─── PATCH /notifications/{id}/lire ──────────────────────────────────────────

@router.patch(
    "/{id_notification}/lire",
    summary="Marquer une notification comme lue",
)
def marquer_lue(
    id_notification: UUID,
    identity=Depends(get_current_identity),
    session: Session = Depends(get_session),
):
    notif = session.get(Notification, id_notification)
    if not notif or notif.destinataire_id != identity["uid"]:
        raise HTTPException(status_code=404, detail="Notification introuvable")
    notif.lu = True
    session.add(notif)
    session.commit()
    return {"message": "Notification marquée comme lue"}


# ─── PATCH /notifications/tout-lire ──────────────────────────────────────────

@router.patch(
    "/tout-lire",
    summary="Marquer toutes les notifications comme lues",
)
def tout_marquer_lu(
    identity=Depends(get_current_identity),
    session: Session = Depends(get_session),
):
    notifs = session.exec(
        select(Notification)
        .where(Notification.destinataire_id == identity["uid"])
        .where(Notification.lu == False)
    ).all()
    for n in notifs:
        n.lu = True
        session.add(n)
    session.commit()
    return {"message": f"{len(notifs)} notifications marquées comme lues"}