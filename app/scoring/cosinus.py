"""
ORIAB — scoring/cosinus.py
Similarité cosinus + Weighted Score 60/25/15.

Source des données : table filiere (PostgreSQL via SQLModel).
Le cosinus compare le vecteur RIASEC du bachelier avec le profil_riasec_dominant
de chaque filière stocké en JSONB dans la DB.

Score marché = 0.6 × taux_insertion/100 + 0.4 × (1 - indice_saturation)
Score IA     = f(tendance_ia) : 0→1.0 | 1→0.75 | 2→0.40 | 3→0.10
WS           = 60% × cosinus + 25% × score_marché + 15% × score_IA  → [0, 100]
"""
import numpy as np
from sqlmodel import Session, select
from app.models.filiere import Filiere


# ─── Constantes ───────────────────────────────────────────────────────────────
DIMS = ["R", "I", "A", "S", "E", "C"]

IA_SCORE_MAP = {0: 1.00, 1: 0.75, 2: 0.40, 3: 0.10}


# ─── Fonctions de calcul ──────────────────────────────────────────────────────

def distance_cosinus(v_bach: dict[str, float], v_filiere: dict[str, float]) -> float:
    """
    Similarité cosinus entre le profil RIASEC du bachelier
    et le profil idéal de la filière.
    Retourne une valeur ∈ [0.0, 1.0].
    """
    vb = np.array([float(v_bach.get(d, 0)) for d in DIMS])
    vf = np.array([float(v_filiere.get(d, 0)) for d in DIMS])
    nb, nf = np.linalg.norm(vb), np.linalg.norm(vf)
    if nb == 0 or nf == 0:
        return 0.0
    return float(np.dot(vb, vf) / (nb * nf))


def score_marche_normalise(filiere: Filiere) -> float:
    """
    Score marché normalisé [0, 1].
    Combine taux d'insertion (60%) et indice de saturation inversé (40%).
    """
    t = float(filiere.taux_insertion or 0) / 100.0
    s = float(filiere.indice_saturation or 0.5)
    return round(0.6 * t + 0.4 * (1.0 - s), 4)


def score_ia_normalise(filiere: Filiere) -> float:
    """
    Score IA normalisé [0, 1] depuis tendance_ia (0-3).
    0 = secteur en forte croissance → excellent (1.0)
    3 = secteur fortement automatisable → faible (0.10)
    """
    return IA_SCORE_MAP.get(filiere.tendance_ia or 1, 0.75)


def weighted_score(sim_riasec: float, s_marche: float, s_ia: float) -> float:
    """
    Weighted Score = 60% cosinus + 25% marché + 15% IA → score ∈ [0, 100].
    Formule conforme au mémoire (Tableau de pondération).
    """
    return round((0.60 * sim_riasec + 0.25 * s_marche + 0.15 * s_ia) * 100, 1)


# ─── Fonction principale ──────────────────────────────────────────────────────

def toutes_filieres_scorees(scores_bach: dict[str, float], session: Session) -> list[dict]:
    """
    Calcule le Weighted Score de TOUTES les filières actives en DB
    et retourne TOUTES les filières triées par score décroissant.
    Le veto sera appliqué après par appliquer_veto().

    Utilisée par /api/recommandations/generer.
    Retourne TOUTES les filières pour que appliquer_veto() puisse
    sélectionner le Top 3 parmi les filières valides.

    Args:
        scores_bach: {'R': 72.4, 'I': 85.1, ...} — sortie de calculer_scores_riasec()
        session:     Session SQLModel active (injectée par FastAPI)

    Returns:
        Liste de 5 dicts enrichis avec tous les champs utiles pour le rapport LLM.
    """
    filieres = session.exec(select(Filiere)).all()
    resultats = []

    for filiere in filieres:
        profil_ideal = filiere.profil_riasec_dominant or {}
        if not profil_ideal:
            continue  # Filière sans profil RIASEC — on l'ignore

        sim    = distance_cosinus(scores_bach, profil_ideal)
        s_m    = score_marche_normalise(filiere)
        s_ia   = score_ia_normalise(filiere)
        ws     = weighted_score(sim, s_m, s_ia)

        # Veto Factors spécifiques à la filière (stockés en JSONB dans la DB)
        vf = filiere.veto_factors or {}

        resultats.append({
            "id_filiere":            str(filiere.id_filiere),
            "nom":                   filiere.nom,
            "domaine":               filiere.domaine,
            "weighted_score":        ws,
            "sim_riasec":            round(sim, 4),
            "score_marche":          s_m,
            "score_ia":              s_ia,
            # Données marché — utilisées par le prompt LLM ET les Veto Factors
            "duree_theorique":       filiere.duree_theorique,
            "salaire_median_p50":    filiere.salaire_median_p50,
            "taux_insertion":        filiere.taux_insertion,
            "indice_saturation":     filiere.indice_saturation,
            "tendance_ia":           filiere.tendance_ia,
            "tendance_curricula_marche": filiere.tendance_curricula_marche,
            # Veto Factors de la filière depuis DB
            "budget_min_fcfa":       vf.get("budget_min_fcfa", 0),
            "serie_bac_requise":     vf.get("serie_bac_requise", []),
            "mobilite_requise":      vf.get("mobilite_requise", False),
        })

    resultats.sort(key=lambda x: x["weighted_score"], reverse=True)
    return resultats  # toutes — veto appliqué en aval
