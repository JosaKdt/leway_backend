from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID

from app.core.database import get_session
from app.core.security import create_access_token, get_current_user
from app.models.representant_universite import RepresentantUniversite, RepresentantCreate, RepresentantRead
from app.models.universite import Universite
from app.models.score_compatibilite import ScoreCompatibilite
from app.models.recommandation import Recommandation
from app.models.filiere import Filiere, FiliereRead
from app.models.formation import Formation
from app.models.notification import creer_notification
from app.models.administrateur import Administrateur
from app.core.security import verify_password, hash_password
from pydantic import BaseModel as PydanticBase

router = APIRouter()


# ─── Guard représentant ───────────────────────────────────────────────────────

def require_representant(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.get("role") != "representant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve aux representants d'universite",
        )
    representant = session.exec(
        select(RepresentantUniversite).where(
            RepresentantUniversite.id_representant == UUID(current_user["sub"])
        )
    ).first()
    if not representant:
        raise HTTPException(status_code=404, detail="Representant introuvable")
    return representant


# ─── Mon université ───────────────────────────────────────────────────────────

@router.get("/mon-universite", response_model=Universite)
def get_mon_universite(
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    universite = session.get(Universite, representant.id_universite)
    if not universite:
        raise HTTPException(status_code=404, detail="Universite introuvable")
    return universite


@router.patch("/mon-universite", response_model=Universite)
def update_mon_universite(
    data: dict,
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    universite = session.get(Universite, representant.id_universite)
    if not universite:
        raise HTTPException(status_code=404, detail="Universite introuvable")

    champs_proteges = {"accreditation_mesrs", "accreditation_cames", "id_universite"}
    for key, value in data.items():
        if key not in champs_proteges:
            setattr(universite, key, value)

    session.add(universite)
    session.commit()
    session.refresh(universite)
    return universite


# ─── Statistiques ─────────────────────────────────────────────────────────────

@router.get("/stats")
def get_stats(
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    id_universite = representant.id_universite

    formations = session.exec(
        select(Formation).where(Formation.id_universite == id_universite)
    ).all()
    ids_filieres = [f.id_filiere for f in formations]

    if not ids_filieres:
        return {
            "universite_id": str(id_universite),
            "formations": len(formations),
            "leads_total": 0,
            "leads_top1": 0,
            "score_moyen": 0.0,
            "message": "Aucune formation enregistree pour cette universite.",
        }

    # Tous les scores pour le score moyen
    tous_scores = session.exec(
        select(ScoreCompatibilite).where(
            ScoreCompatibilite.id_filiere.in_(ids_filieres)
        )
    ).all()

    # Uniquement les scores classés (top réel — classement non null)
    scores_classes = [s for s in tous_scores if s.classement is not None]

    leads_total = len(scores_classes)
    leads_top1  = sum(1 for s in scores_classes if s.classement == 1)
    score_moyen = round(
        sum(s.score_weighted or 0 for s in tous_scores) / len(tous_scores), 2
    ) if tous_scores else 0.0

    return {
        "universite_id": str(id_universite),
        "formations":    len(formations),
        "leads_total":   leads_total,
        "leads_top1":    leads_top1,
        "score_moyen":   score_moyen,
    }


# ─── Profil représentant ──────────────────────────────────────────────────────

@router.get("/moi", response_model=RepresentantRead)
def get_moi(representant: RepresentantUniversite = Depends(require_representant)):
    return representant


# ─── Filières de mon université ───────────────────────────────────────────────

@router.get("/mes-filieres", response_model=list[FiliereRead])
def get_mes_filieres(
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    formations = session.exec(
        select(Formation).where(Formation.id_universite == representant.id_universite)
    ).all()
    ids_filieres = [f.id_filiere for f in formations]
    if not ids_filieres:
        return []
    return session.exec(
        select(Filiere)
        .where(Filiere.id_filiere.in_(ids_filieres))
        .order_by(Filiere.domaine, Filiere.nom)
    ).all()


# ─── Modifier une formation ───────────────────────────────────────────────────

@router.patch("/mes-filieres/{id_filiere}", response_model=FiliereRead)
def update_ma_formation(
    id_filiere: UUID,
    data: dict,
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    formation = session.exec(
        select(Formation)
        .where(Formation.id_filiere == id_filiere)
        .where(Formation.id_universite == representant.id_universite)
    ).first()
    if not formation:
        raise HTTPException(status_code=404, detail="Formation introuvable pour votre universite")

    champs_formation = {"duree_reelle", "frais_inscription"}
    for key, value in data.items():
        if key in champs_formation:
            setattr(formation, key, value)
    session.add(formation)

    if "duree_theorique" in data:
        filiere = session.get(Filiere, id_filiere)
        if filiere:
            filiere.duree_theorique = data["duree_theorique"]
            session.add(filiere)

    session.commit()
    return session.get(Filiere, id_filiere)


# ─── Ajouter une formation (lier filière existante) ───────────────────────────

@router.post("/mes-formations", status_code=status.HTTP_201_CREATED)
def add_formation(
    data: dict,
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    id_filiere = data.get("id_filiere")
    if not id_filiere:
        raise HTTPException(status_code=400, detail="id_filiere requis")

    filiere = session.get(Filiere, UUID(str(id_filiere)))
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere introuvable")

    existing = session.exec(
        select(Formation)
        .where(Formation.id_filiere == UUID(str(id_filiere)))
        .where(Formation.id_universite == representant.id_universite)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Cette filiere est deja liee a votre universite")

    formation = Formation(
        id_filiere=UUID(str(id_filiere)),
        id_universite=representant.id_universite,
        diplome=data.get("diplome", "Licence"),
        frais_inscription=data.get("frais_inscription"),
        duree_reelle=data.get("duree_reelle"),
    )
    session.add(formation)
    session.commit()
    session.refresh(formation)
    return {"message": "Formation ajoutee", "id_formation": str(formation.id_formation)}


# ─── Ajouter une filière (en attente de validation) ───────────────────────────

@router.post("/mes-filieres", status_code=status.HTTP_201_CREATED)
def add_filiere(
    data: dict,
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    nom = data.get("nom", "").strip()
    if not nom:
        raise HTTPException(status_code=400, detail="Le nom de la filiere est requis")

    existing = session.exec(select(Filiere).where(Filiere.nom == nom)).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Une filiere avec ce nom existe deja. Utilisez 'Ajouter une formation' pour la lier a votre universite."
        )

    filiere = Filiere(
        nom=nom,
        domaine=data.get("domaine"),
        duree_theorique=data.get("duree_theorique", 3),
        description=data.get("description"),
        niveau_admission=data.get("niveau_admission", "Bac"),
        langue_enseignement=data.get("langue_enseignement", "Français"),
        statut="en_attente",
        salaire_median_p50=data.get("salaire_median_p50", 200000),
        taux_insertion=data.get("taux_insertion", 60.0),
        indice_saturation=data.get("indice_saturation", 0.8),
        tendance_ia=data.get("tendance_ia", 1),
        tendance_curricula_marche=0.7,
        poids_scoring={"riasec": 0.60, "marche": 0.25, "ia": 0.15},
    )
    session.add(filiere)
    session.flush()

    # Lier à l'université du représentant
    formation = Formation(
        id_filiere=filiere.id_filiere,
        id_universite=representant.id_universite,
        diplome=data.get("diplome", "Licence"),
        frais_inscription=data.get("frais_inscription"),
        duree_reelle=data.get("duree_theorique", 3),
    )
    session.add(formation)

    # Récupérer l'université pour le message
    universite = session.get(Universite, representant.id_universite)
    univ_nom = universite.nom if universite else "une université"

    # Notifier tous les admins
    admins = session.exec(select(Administrateur)).all()
    for a in admins:
        creer_notification(
            session=session,
            destinataire_id=a.id_administrateur,
            destinataire_role="administrateur",
            type="nouvelle_soumission",
            titre="Nouvelle filière à valider 📝",
            message=f"« {nom} » a été soumise par {representant.prenom} {representant.nom} ({univ_nom}). En attente de votre validation.",
        )

    session.commit()

    return {
        "message": "Filiere soumise pour validation. Elle sera visible apres approbation de l'administrateur.",
        "id_filiere": str(filiere.id_filiere),
        "statut": "en_attente",
    }


# ─── Changer mot de passe ─────────────────────────────────────────────────────

class ChangerMotDePasseRequest(PydanticBase):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str
    confirmation: str


@router.patch(
    "/changer-mot-de-passe",
    summary="Changer son mot de passe",
)
def changer_mot_de_passe(
    data: ChangerMotDePasseRequest,
    representant: RepresentantUniversite = Depends(require_representant),
    session: Session = Depends(get_session),
):
    if not verify_password(data.ancien_mot_de_passe, representant.mot_de_passe_hash):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

    if data.nouveau_mot_de_passe != data.confirmation:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")

    if len(data.nouveau_mot_de_passe) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caracteres")

    representant.mot_de_passe_hash = hash_password(data.nouveau_mot_de_passe)
    session.add(representant)
    session.commit()
    return {"message": "Mot de passe modifie avec succes"}