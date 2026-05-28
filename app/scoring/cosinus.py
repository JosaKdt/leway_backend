"""
LÉWAY — scoring/cosinus.py
Distance cosinus bachelier ↔ filière + Weighted Score 60/25/15.
"""
import json
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def charger_filieres() -> dict:
    with open(DATA_DIR / "filieres.json", encoding="utf-8") as f:
        return json.load(f)


def distance_cosinus(v_bach: dict[str, float], v_fil: dict[str, float]) -> float:
    dims = ["R", "I", "A", "S", "E", "C"]
    vb = np.array([v_bach[d] for d in dims], dtype=float)
    vf = np.array([v_fil[d] for d in dims], dtype=float)
    nb, nf = np.linalg.norm(vb), np.linalg.norm(vf)
    if nb == 0 or nf == 0:
        return 0.0
    return float(np.dot(vb, vf) / (nb * nf))


def weighted_score(sim_riasec: float, score_marche: float, score_ia: float) -> float:
    """WS = 60% cosinus + 25% marché + 15% IA → score 0-100."""
    return round((0.60 * sim_riasec + 0.25 * score_marche + 0.15 * score_ia) * 100, 1)


def top5_filieres(scores_bach: dict[str, float]) -> list[dict]:
    """Calcule et retourne les 5 meilleures filières triées par WS décroissant."""
    filieres_db = charger_filieres()
    resultats = []
    for nom, data in filieres_db.items():
        sim = distance_cosinus(scores_bach, data)
        ws = weighted_score(sim, data["score_marche"], data["score_ia"])
        resultats.append({
            "filiere": nom,
            "weighted_score": ws,
            "sim_riasec": round(sim, 4),
            "score_marche": data["score_marche"],
            "score_ia": data["score_ia"],
            "duree_ans": data["duree_ans"],
            "budget_min_fcfa": data["budget_min_fcfa"],
            "bac_recommande": data["bac_recommande"],
            "salaire_median_fcfa": data.get("salaire_median_fcfa"),
            "taux_insertion_pct": data.get("taux_insertion_pct"),
            "indice_saturation": data.get("indice_saturation"),
        })
    resultats.sort(key=lambda x: x["weighted_score"], reverse=True)
    return resultats[:5]
