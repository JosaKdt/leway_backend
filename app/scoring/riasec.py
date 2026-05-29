"""
ORIAB — scoring/riasec.py
Calcul des 6 scores RIASEC normalisés 0-100 depuis les 28 réponses.

Poids w_i par item : estimés a priori depuis la littérature IRT
(Armstrong & Rounds 2008, Liao et al. 2008) — discrimination parameter a.
  a > 1.5  → w_i = 1.4  (très discriminant)
  a ∈ [1.0, 1.5] → w_i = 1.2  (discriminant)
  a ∈ [0.7, 1.0) → w_i = 1.0  (peu discriminant)
  a < 0.7  → w_i = 0.8  (peu informatif)

Statut : estimé_a_priori — calibration empirique v2.0 prévue (n≥200 bacheliers béninois).

Règle absolue : Section D (dimension=VETO) JAMAIS dans les scores RIASEC.
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
        reponses: {'Q01': 4, 'Q02': 2, ...} — Likert 1-5 pour les 28 items.
                  Items Section D (VETO) présents mais ignorés du calcul.

    Returns:
        {'R': 72.4, 'I': 85.1, 'A': 34.0, 'S': 61.2, 'E': 55.8, 'C': 48.3}
        Scores normalisés 0-100, arrondis à 1 décimale.

    Raises:
        ValueError: réponse manquante ou valeur hors Likert [1-5]
    """
    items = charger_items()
    dims = ["R", "I", "A", "S", "E", "C"]
    bruts = {d: 0.0 for d in dims}
    maxs  = {d: 0.0 for d in dims}

    for item in items:
        dim, qid = item["dimension"], item["id"]

        if qid not in reponses:
            raise ValueError(f"Réponse manquante pour l'item {qid}")

        # RÈGLE ABSOLUE — Section D = Veto Factors, jamais dans les scores RIASEC
        if dim == "VETO":
            continue

        rep = int(reponses[qid])
        if not (1 <= rep <= 5):
            raise ValueError(f"Réponse {rep} hors Likert [1-5] pour {qid}")

        # Items inversés — anti-biais d'acquiescement
        if item.get("inverse", False):
            rep = 6 - rep

        w = float(item["w_i"])
        bruts[dim] += w * rep
        maxs[dim]  += w * 5

    return {
        d: round((bruts[d] / maxs[d]) * 100, 1) if maxs[d] > 0 else 0.0
        for d in dims
    }


def dimension_dominante(scores: dict[str, float]) -> str:
    """Retourne la lettre RIASEC avec le score le plus élevé."""
    return max(scores, key=scores.get)


def top3_dimensions(scores: dict[str, float]) -> list[str]:
    """Retourne les 3 dimensions dominantes triées (ex: ['I', 'R', 'C'])."""
    return sorted(scores, key=scores.get, reverse=True)[:3]
