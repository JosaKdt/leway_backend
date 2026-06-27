from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies import get_current_bachelier
from app.models.filiere import Filiere, FiliereCreate, FiliereRead
from app.models.bachelier import Bachelier
from app.models.formation import Formation
from app.models.universite import Universite

router = APIRouter()


# ─── GET /api/filieres ────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[FiliereRead],
    summary="Lister toutes les filières",
)
def list_filieres(
    domaine: Optional[str] = Query(None, description="Filtrer par domaine"),
    search: Optional[str] = Query(None, description="Recherche par nom"),
    session: Session = Depends(get_session),
):
    query = select(Filiere)
    if domaine:
        query = query.where(Filiere.domaine == domaine)
    filieres = session.exec(query).all()
    if search:
        filieres = [
            f for f in filieres
            if search.lower() in f.nom.lower()
        ]
    return filieres


# ─── GET /api/filieres/{id} ───────────────────────────────────────────────────
@router.get(
    "/{id_filiere}",
    response_model=FiliereRead,
    summary="Détail d'une filière",
)
def get_filiere(
    id_filiere: UUID,
    session: Session = Depends(get_session),
):
    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière introuvable",
        )
    return filiere


# ─── GET /api/filieres/{id}/universites ───────────────────────────────────────
@router.get(
    "/{id_filiere}/universites",
    summary="Universités proposant cette filière",
)
def get_universites_pour_filiere(
    id_filiere: UUID,
    session: Session = Depends(get_session),
):
    """
    Retourne la liste des universités proposant cette filière,
    avec les détails spécifiques de chaque formation (frais, durée).
    Permet au bachelier de savoir OÙ étudier une filière recommandée.
    """
    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filière introuvable",
        )

    formations = session.exec(
        select(Formation).where(Formation.id_filiere == id_filiere)
    ).all()

    if not formations:
        return {
            "id_filiere": str(id_filiere),
            "nom_filiere": filiere.nom,
            "universites": [],
            "message": "Aucune université ne propose actuellement cette filière.",
        }

    resultats = []
    for f in formations:
        universite = session.get(Universite, f.id_universite)
        if not universite:
            continue
        resultats.append({
            "id_universite":        str(universite.id_universite),
            "nom_universite":       universite.nom,
            "localisation":        universite.localisation,
            "type":                 universite.type,
            "accreditation_mesrs":  universite.accreditation_mesrs,
            "accreditation_cames":  universite.accreditation_cames,
            "diplome":              f.diplome,
            "frais_inscription":    f.frais_inscription,
            "duree_reelle":         f.duree_reelle,
            "places_disponibles":   f.places_disponibles,
        })

    return {
        "id_filiere":   str(id_filiere),
        "nom_filiere":  filiere.nom,
        "universites":  resultats,
    }


# ─── POST /api/filieres ───────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=FiliereRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une filière (admin)",
)
def create_filiere(
    data: FiliereCreate,
    session: Session = Depends(get_session),
):
    filiere = Filiere(**data.model_dump())
    session.add(filiere)
    session.commit()
    session.refresh(filiere)
    return filiere

# ─── POST /api/filieres/comparer ─────────────────────────────────────────────
from pydantic import BaseModel as PydanticBase

class ComparerRequest(PydanticBase):
    noms: list[str]

@router.post(
    "/comparer",
    response_model=list[FiliereRead],
    summary="Comparer plusieurs filières par nom",
)
def comparer_filieres(
    data: ComparerRequest,
    session: Session = Depends(get_session),
):
    """Retourne les filières correspondant aux noms fournis (comparaison multicritères)."""
    if not data.noms:
        return []
    filieres = session.exec(
        select(Filiere).where(Filiere.nom.in_(data.noms))
    ).all()
    # Conserver l'ordre de la requête
    ordre = {nom: i for i, nom in enumerate(data.noms)}
    return sorted(filieres, key=lambda f: ordre.get(f.nom, 99))


# ─── GET /api/filieres/{id}/universites ───────────────────────────────────────
# « Où étudier ça ? » — liste les universités qui dispensent une formation
# dans cette filière, avec frais, durée réelle, diplôme et places.

@router.get(
    "/{id_filiere}/universites",
    summary="Où étudier cette filière — universités qui la dispensent",
)
def universites_de_la_filiere(
    id_filiere: UUID,
    session: Session = Depends(get_session),
):
    from app.models.formation import Formation
    from app.models.universite import Universite

    filiere = session.get(Filiere, id_filiere)
    if not filiere:
        raise HTTPException(status_code=404, detail="Filière introuvable")

    formations = session.exec(
        select(Formation).where(Formation.id_filiere == id_filiere)
    ).all()

    resultat = []
    for fo in formations:
        univ = session.get(Universite, fo.id_universite)
        if not univ:
            continue
        resultat.append({
            "id_universite":     str(univ.id_universite),
            "nom":               univ.nom,
            "type":              univ.type,
            "localisation":      univ.localisation,
            "taux_reussite":     univ.taux_reussite,
            "accreditation_mesrs": univ.accreditation_mesrs,
            "accreditation_cames": univ.accreditation_cames,
            # Données propres à la formation (filière dans CETTE université)
            "diplome":           fo.diplome,
            "frais_inscription": fo.frais_inscription,
            "duree_reelle":      fo.duree_reelle,
            "places_disponibles": fo.places_disponibles,
            # Fourchette de coût annuel de l'université (repli si frais non saisis)
            "cout_annuel_min":   univ.cout_annuel_min,
            "cout_annuel_max":   univ.cout_annuel_max,
        })

    # Trier : universités accréditées MESRS d'abord, puis par frais croissants
    resultat.sort(key=lambda u: (
        not bool(u["accreditation_mesrs"]),
        u["frais_inscription"] if u["frais_inscription"] is not None else 10**9,
    ))

    return {
        "filiere": filiere.nom,
        "nombre_universites": len(resultat),
        "universites": resultat,
    }
