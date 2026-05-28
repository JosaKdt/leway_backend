"""
LÉWAY — scoring/veto.py
Veto Factors — filtres éliminatoires (Tableau 7 du mémoire).
3 règles : budget, mobilité internationale, durée.
"""
from typing import Any


def appliquer_veto(
    top5: list[dict],
    contexte: dict[str, Any],
    filieres_db: dict[str, dict],
) -> dict[str, list]:
    budget = contexte.get("budget_mensuel_fcfa", 0)
    peut_partir = contexte.get("peut_quitter_pays", False)
    horizon = contexte.get("horizon_ans", 5)
    valides, eliminees = [], []

    for cand in top5:
        nom = cand["filiere"]
        if nom not in filieres_db:
            valides.append(cand)
            continue
        f = filieres_db[nom]
        raisons = []

        # VETO 1 — Budget insuffisant
        if budget < f.get("budget_min_fcfa", 0):
            raisons.append(
                f"Budget {budget:,} FCFA < minimum requis {f['budget_min_fcfa']:,} FCFA"
            )
        # VETO 2 — Mobilité internationale requise
        if f.get("mobilite_requise", False) and not peut_partir:
            raisons.append("Mobilité internationale requise mais non possible")
        # VETO 3 — Durée > horizon souhaité
        if f.get("duree_ans", 3) > horizon:
            raisons.append(
                f"Durée {f['duree_ans']} ans > horizon souhaité {horizon} ans"
            )

        if raisons:
            eliminees.append({
                "filiere": nom,
                "weighted_score": cand["weighted_score"],
                "raisons_veto": raisons,
            })
        else:
            valides.append(cand)

    return {"top5_valides": valides, "eliminees": eliminees}
