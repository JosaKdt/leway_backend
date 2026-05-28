"""
LÉWAY — scoring/riasec.py
Calcul des 6 scores RIASEC normalisés 0-100 depuis les 28 réponses.
Items Section D (VETO) exclus du calcul — règle absolue.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def charger_items() -> list[dict]:
    with open(DATA_DIR / "items.json", encoding="utf-8") as f:
        return json.load(f)


def calculer_scores_riasec(reponses: dict[str, int]) -> dict[str, float]:
    """
    Calcule les 6 scores RIASEC normalisés 0-100.

    Args:
        reponses: {'Q01': 4, 'Q02': 2, ...} — Likert 1-5.
                  Items VETO (Section D) présents mais ignorés.

    Returns:
        {'R': 72.4, 'I': 85.1, 'A': 34.0, 'S': 61.2, 'E': 55.8, 'C': 48.3}

    Raises:
        ValueError: réponse manquante ou hors Likert [1-5]
    """
    items = charger_items()
    dims = ["R", "I", "A", "S", "E", "C"]
    scores_bruts: dict[str, float] = {d: 0.0 for d in dims}
    scores_max: dict[str, float] = {d: 0.0 for d in dims}

    for item in items:
        dim = item["dimension"]
        qid = item["id"]
        if qid not in reponses:
            raise ValueError(f"Réponse manquante pour {qid}")
        if dim == "VETO":
            continue
        rep = int(reponses[qid])
        if not (1 <= rep <= 5):
            raise ValueError(f"Réponse {rep} hors Likert [1-5] pour {qid}")
        if item.get("inverse", False):
            rep = 6 - rep
        w = float(item["w_i"])
        scores_bruts[dim] += w * rep
        scores_max[dim] += w * 5

    return {
        d: round((scores_bruts[d] / scores_max[d]) * 100, 1)
        if scores_max[d] > 0 else 0.0
        for d in dims
    }


def dimension_dominante(scores: dict[str, float]) -> str:
    return max(scores, key=scores.get)
