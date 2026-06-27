from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from pydantic import BaseModel as PydanticBase
from app.api.auth import email_deja_utilise

from app.core.database import get_session
from app.core.security import get_current_user, hash_password
from app.models.filiere import Filiere, FiliereCreate, FiliereRead
from app.models.universite import Universite, UniversiteCreate, UniversiteRead
from app.models.recommandation import Recommandation
from app.models.representant_universite import RepresentantUniversite
from app.models.demande_representant import (
    DemandeRepresentant,
    DemandeRepresentantRead,
    RefusDemandeRequest,
)
from app.models.notification import creer_notification
from app.services.email_service import send_invitation_representant, generate_temp_password

router = APIRouter()


# ─── Garde admin ──────────────────────────────────────────────────────────────

def require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != "administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve aux administrateurs",
        )
    return current_user


# ─── Métriques ────────────────────────────────────────────────────────────────

@router.get("/metriques", summary="Tableau de bord — métriques algorithmiques")
def get_metriques(
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from app.models.bachelier import Bachelier
    from app.models.profil_psychometrique import ProfilPsychometrique

    nb_bacheliers      = len(session.exec(select(Bachelier)).all())
    nb_filieres        = len(session.exec(select(Filiere).where(Filiere.statut == "active")).all())
    nb_universites     = len(session.exec(select(Universite)).all())
    nb_recommandations = len(session.exec(select(Recommandation)).all())
    nb_profils         = len(session.exec(select(ProfilPsychometrique)).all())
    nb_generees        = len(session.exec(select(Recommandation).where(Recommandation.statut == "generee")).all())
    nb_consultees      = len(session.exec(select(Recommandation).where(Recommandation.statut == "consultee")).all())

    taux_completion = round(nb_profils / nb_bacheliers, 3) if nb_bacheliers > 0 else 0.0

    return {
        "bacheliers":      nb_bacheliers,
        "filieres":        nb_filieres,
        "universites":     nb_universites,
        "taux_completion": taux_completion,
        "recommandations": {
            "total":      nb_recommandations,
            "generees":   nb_generees,
            "consultees": nb_consultees,
        },
    }


# ─── Gestion des filières ─────────────────────────────────────────────────────

@router.get("/filieres", response_model=List[FiliereRead], summary="Admin — liste toutes les filières")
def admin_list_filieres(session: Session = Depends(get_session), admin=Depends(require_admin)):
    return session.exec(select(Filiere).order_by(Filiere.domaine, Filiere.nom)).all()


@router.post("/filieres", response_model=FiliereRead, status_code=status.HTTP_201_CREATED, summary="Admin — créer une filière")
def admin_create_filiere(data: FiliereCreate, session: Session = Depends(get_session), admin=Depends(require_admin)):
    filiere = Filiere(**data.model_dump())
    session.add(filiere)
    session.commit()
    session.refresh(filiere)
    return filiere


@router.patch("/filieres/{id_filiere}", response_model=FiliereRead, summary="Admin — mettre à jour une filière")
def admin_update_filiere(id_filiere: UUID, data: dict, session: Session = Depends(get_session), admin=Depends(require_admin)):
    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere introuvable")
    for key, value in data.items():
        setattr(filiere, key, value)
    session.add(filiere)
    session.commit()
    session.refresh(filiere)
    return filiere


@router.delete("/filieres/{id_filiere}", status_code=status.HTTP_204_NO_CONTENT, summary="Admin — supprimer une filière")
def admin_delete_filiere(id_filiere: UUID, session: Session = Depends(get_session), admin=Depends(require_admin)):
    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere introuvable")
    session.delete(filiere)
    session.commit()


# ─── Filières en attente de validation ───────────────────────────────────────

@router.get("/filieres/en-attente", summary="Admin — filières soumises par les représentants")
def admin_filieres_en_attente(
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from app.models.formation import Formation

    filieres = session.exec(
        select(Filiere).where(Filiere.statut == "en_attente").order_by(Filiere.nom)
    ).all()

    resultat = []
    for f in filieres:
        formation = session.exec(
            select(Formation).where(Formation.id_filiere == f.id_filiere)
        ).first()
        univ_nom = None
        if formation:
            univ = session.get(Universite, formation.id_universite)
            univ_nom = univ.nom if univ else None

        resultat.append({
            "id_filiere":       str(f.id_filiere),
            "nom":              f.nom,
            "domaine":          f.domaine,
            "duree_theorique":  f.duree_theorique,
            "description":      f.description,
            "taux_insertion":   f.taux_insertion,
            "frais_inscription": formation.frais_inscription if formation else None,
            "universite_nom":   univ_nom,
            "statut":           f.statut,
        })

    return resultat


@router.patch("/filieres/{id_filiere}/valider", response_model=FiliereRead, summary="Admin — valider une filière en attente")
def admin_valider_filiere(
    id_filiere: UUID,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from app.models.formation import Formation

    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere introuvable")
    if filiere.statut != "en_attente":
        raise HTTPException(status_code=400, detail="Cette filiere n'est pas en attente de validation")

    filiere.statut = "active"
    session.add(filiere)

    # Notifier le représentant de l'université qui a soumis
    formation = session.exec(
        select(Formation).where(Formation.id_filiere == id_filiere)
    ).first()
    if formation:
        rep = session.exec(
            select(RepresentantUniversite)
            .where(RepresentantUniversite.id_universite == formation.id_universite)
        ).first()
        if rep:
            creer_notification(
                session=session,
                destinataire_id=rep.id_representant,
                destinataire_role="representant",
                type="filiere_validee",
                titre="Filière validée ✅",
                message=f"Votre filière « {filiere.nom} » a été validée par l'administrateur. Elle est maintenant visible pour les bacheliers.",
            )

    session.commit()
    session.refresh(filiere)
    return filiere


@router.delete("/filieres/{id_filiere}/rejeter", status_code=status.HTTP_200_OK, summary="Admin — rejeter une filière en attente")
def admin_rejeter_filiere(
    id_filiere: UUID,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from app.models.formation import Formation

    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere introuvable")
    if filiere.statut != "en_attente":
        raise HTTPException(status_code=400, detail="Seules les filieres en attente peuvent etre rejetees")

    # Notifier le représentant avant suppression
    formation = session.exec(
        select(Formation).where(Formation.id_filiere == id_filiere)
    ).first()
    if formation:
        rep = session.exec(
            select(RepresentantUniversite)
            .where(RepresentantUniversite.id_universite == formation.id_universite)
        ).first()
        if rep:
            creer_notification(
                session=session,
                destinataire_id=rep.id_representant,
                destinataire_role="representant",
                type="filiere_rejetee",
                titre="Filière rejetée ❌",
                message=f"Votre filière « {filiere.nom} » a été rejetée par l'administrateur. Contactez l'administration pour plus d'informations.",
            )

    # Supprimer formations liées puis filière
    formations = session.exec(
        select(Formation).where(Formation.id_filiere == id_filiere)
    ).all()
    for fo in formations:
        session.delete(fo)

    session.delete(filiere)
    session.commit()
    return {"message": "Filiere rejetee et supprimee", "id_filiere": str(id_filiere)}


# ─── Validation accréditations ────────────────────────────────────────────────

@router.patch("/universites/{id_universite}/accreditation", response_model=UniversiteRead, summary="Admin — valider accréditation MESRS / CAMES")
def valider_accreditation(
    id_universite: UUID,
    accreditation_mesrs: bool = None,
    accreditation_cames: bool = None,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    universite = session.get(Universite, id_universite)
    if not universite:
        raise HTTPException(status_code=404, detail="Universite introuvable")
    if accreditation_mesrs is not None:
        universite.accreditation_mesrs = accreditation_mesrs
    if accreditation_cames is not None:
        universite.accreditation_cames = accreditation_cames
    session.add(universite)
    session.commit()
    session.refresh(universite)
    return universite


# ─── Rapports agrégés ─────────────────────────────────────────────────────────

@router.get("/rapports/filieres-populaires", summary="Admin — filières les plus recommandées")
def filieres_populaires(session: Session = Depends(get_session), admin=Depends(require_admin)):
    from app.models.score_compatibilite import ScoreCompatibilite
    from sqlmodel import func

    resultats = session.exec(
        select(
            ScoreCompatibilite.id_filiere,
            func.count(ScoreCompatibilite.id_filiere).label("nb_recommandations"),
            func.avg(ScoreCompatibilite.score_weighted).label("score_moyen"),
        ).where(ScoreCompatibilite.classement == 1)
        .group_by(ScoreCompatibilite.id_filiere)
        .order_by(func.count(ScoreCompatibilite.id_filiere).desc())
        .limit(10)
    ).all()

    # Récupérer le nom de chaque filière (jointure manuelle pour rester simple)
    reponse = []
    for r in resultats:
        filiere = session.get(Filiere, r.id_filiere)
        reponse.append({
            "id_filiere":          str(r.id_filiere),
            "nom_filiere":         filiere.nom if filiere else "Filière supprimée",
            "domaine":             filiere.domaine if filiere else None,
            "nb_fois_top1":        r.nb_recommandations,
            "score_weighted_moyen": round(r.score_moyen or 0, 2),
        })

    return reponse


# ─── Invitation représentant ──────────────────────────────────────────────────

class InvitationRepresentantRequest(PydanticBase):
    nom: str
    prenom: str
    email: str
    id_universite: str


@router.post("/inviter-representant", summary="Admin — inviter un représentant d'université")
def inviter_representant(
    data: InvitationRepresentantRequest,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from app.models.administrateur import Administrateur

    universite = session.get(Universite, UUID(data.id_universite))
    if not universite:
        raise HTTPException(status_code=404, detail="Universite introuvable")

    existing = session.exec(
        select(RepresentantUniversite).where(RepresentantUniversite.email == data.email)
    ).first()
    if email_deja_utilise(data.email, session):
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email")

    mot_de_passe_temp = generate_temp_password()

    rep = RepresentantUniversite(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        mot_de_passe_hash=hash_password(mot_de_passe_temp),
        id_universite=UUID(data.id_universite),
    )
    session.add(rep)
    session.flush()

    # Notifier tous les admins
    admins = session.exec(select(Administrateur)).all()
    for a in admins:
        creer_notification(
            session=session,
            destinataire_id=a.id_administrateur,
            destinataire_role="administrateur",
            type="nouveau_representant",
            titre="Nouveau représentant créé 👤",
            message=f"{data.prenom} {data.nom} a été ajouté comme représentant de {universite.nom}.",
        )

    session.commit()

    email_ok = send_invitation_representant(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        nom_universite=universite.nom,
        mot_de_passe_temp=mot_de_passe_temp,
    )

    return {
        "message": "Representant cree avec succes",
        "email_envoye": email_ok,
        "representant": {
            "nom":        data.nom,
            "prenom":     data.prenom,
            "email":      data.email,
            "universite": universite.nom,
        }
    }


# ─── Liste représentants ──────────────────────────────────────────────────────

@router.get("/representants", summary="Admin — liste tous les représentants")
def list_representants(session: Session = Depends(get_session), admin=Depends(require_admin)):
    reps = session.exec(select(RepresentantUniversite)).all()
    return [
        {
            "id":            str(r.id_representant),
            "nom":           r.nom,
            "prenom":        r.prenom,
            "email":         r.email,
            "id_universite": str(r.id_universite),
            "created_at":    str(r.created_at),
        }
        for r in reps
    ]

# ─── Demandes de représentant (CU06 → CU10) ───────────────────────────────────

@router.get(
    "/demandes-representants",
    summary="Admin — demandes de représentant en attente",
)
def admin_demandes_representants(
    statut: str = "en_attente",
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    """Liste les demandes par statut (en_attente | validee | refusee)."""
    demandes = session.exec(
        select(DemandeRepresentant)
        .where(DemandeRepresentant.statut == statut)
        .order_by(DemandeRepresentant.created_at)
    ).all()

    resultat = []
    for d in demandes:
        # Nom de l'établissement (existant ou proposé)
        if d.id_universite:
            univ = session.get(Universite, d.id_universite)
            etablissement = univ.nom if univ else "—"
            etablissement_type = "existant"
        else:
            etablissement = d.universite_proposee_nom or "—"
            etablissement_type = "proposé"

        resultat.append({
            "id_demande":     str(d.id_demande),
            "nom":            d.nom,
            "prenom":         d.prenom,
            "email":          d.email,
            "telephone":      d.telephone,
            "fonction":       d.fonction,
            "etablissement":  etablissement,
            "etablissement_type": etablissement_type,
            "ville_proposee": d.universite_proposee_ville,
            "dossier":        d.dossier,
            "statut":         d.statut,
            "created_at":     str(d.created_at),
        })

    return resultat


@router.patch(
    "/demandes-representants/{id_demande}/valider",
    summary="Admin — valider une demande et créer le compte représentant",
)
def admin_valider_demande_representant(
    id_demande: UUID,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from datetime import datetime, timezone

    demande = session.get(DemandeRepresentant, id_demande)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    if demande.statut != "en_attente":
        raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")

    # Sécurité : l'email ne doit pas avoir été pris entre-temps
    if email_deja_utilise(demande.email, session):
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email")

    # 1. Résoudre l'établissement : existant ou à créer
    if demande.id_universite:
        universite = session.get(Universite, demande.id_universite)
        if not universite:
            raise HTTPException(status_code=404, detail="Université liée introuvable")
    else:
        # Créer la nouvelle université proposée (accréditation à valider ensuite)
        universite = Universite(
            nom=demande.universite_proposee_nom,
            localisation=demande.universite_proposee_ville,
            accreditation_mesrs=False,
            accreditation_cames=False,
        )
        session.add(universite)
        session.flush()

    # 2. Créer le compte représentant (réutilise le mot de passe déjà haché)
    rep = RepresentantUniversite(
        nom=demande.nom,
        prenom=demande.prenom,
        email=demande.email,
        mot_de_passe_hash=demande.mot_de_passe_hash,
        id_universite=universite.id_universite,
    )
    session.add(rep)

    # 3. Clore la demande
    demande.statut = "validee"
    demande.traite_at = datetime.now(timezone.utc)
    if not demande.id_universite:
        demande.id_universite = universite.id_universite
    session.add(demande)
    session.flush()

    # 4. Notifier le représentant (in-app)
    creer_notification(
        session=session,
        destinataire_id=rep.id_representant,
        destinataire_role="representant",
        type="demande_validee",
        titre="Demande acceptée ✅",
        message=f"Votre demande pour représenter {universite.nom} a été acceptée. Vous pouvez désormais vous connecter avec votre email et votre mot de passe.",
    )

    session.commit()
    session.refresh(rep)

    # 5. Notifier par email (best-effort, ne bloque pas la validation)
    email_ok = False
    try:
        from app.services.email_service import send_demande_representant_validee
        email_ok = send_demande_representant_validee(
            nom=rep.nom, prenom=rep.prenom, email=rep.email, nom_universite=universite.nom,
        )
    except Exception:
        email_ok = False

    return {
        "message": "Demande validée, compte représentant créé.",
        "email_envoye": email_ok,
        "representant": {
            "id":         str(rep.id_representant),
            "nom":        rep.nom,
            "prenom":     rep.prenom,
            "email":      rep.email,
            "universite": universite.nom,
        },
    }


@router.patch(
    "/demandes-representants/{id_demande}/refuser",
    summary="Admin — refuser une demande de représentant",
)
def admin_refuser_demande_representant(
    id_demande: UUID,
    data: RefusDemandeRequest = RefusDemandeRequest(),
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    from datetime import datetime, timezone

    demande = session.get(DemandeRepresentant, id_demande)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    if demande.statut != "en_attente":
        raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")

    demande.statut = "refusee"
    demande.motif_refus = data.motif_refus
    demande.traite_at = datetime.now(timezone.utc)
    session.add(demande)

    session.commit()

    # Notifier par email (best-effort)
    email_ok = False
    try:
        from app.services.email_service import send_demande_representant_refusee
        email_ok = send_demande_representant_refusee(
            nom=demande.nom, prenom=demande.prenom, email=demande.email,
            motif=data.motif_refus or "Dossier incomplet",
        )
    except Exception:
        email_ok = False

    return {
        "message": "Demande refusée.",
        "email_envoye": email_ok,
        "id_demande": str(id_demande),
    }
