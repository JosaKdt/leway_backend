"""
ORIAB — scoring/riasec.py
Calcul des 6 scores RIASEC normalisés 0-100.

Banque de questions (v2) : items_bank.json
  - 48 items RIASEC (8 par dimension) + 5 VETO
  - Chaque session tire 4 items par dimension → 24 RIASEC + 5 VETO = 29 items
  - Résultat fiable quelle que soit la combinaison tirée (normalisation par session)

Poids w_i estimés a priori (Armstrong & Rounds 2008, Liao et al. 2008) :
  w_i = 1.4 → discrimination élevée (a > 1.5)
  w_i = 1.2 → bonne discrimination (a ∈ [1.0, 1.5])
  w_i = 1.0 → discrimination modérée (a < 1.0)

Statut : calibration empirique v2.0 prévue dès n ≥ 200 bacheliers béninois.

Règle absolue : Section D (dimension=VETO) JAMAIS dans les scores RIASEC.
"""
import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DIMS = ["R", "I", "A", "S", "E", "C"]
ITEMS_PER_DIM = 5   # nombre d'items tirés par dimension à chaque session


def charger_banque() -> list[dict]:
    """Charge la banque complète de 53 items (48 RIASEC + 5 VETO)."""
    path = DATA_DIR / "items_bank.json"
    if not path.exists():
        # Fallback vers items.json pour compatibilité ascendante
        path = DATA_DIR / "items.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tirer_session(seed: int | None = None) -> list[dict]:
    """
    Tire aléatoirement ITEMS_PER_DIM items par dimension RIASEC + tous les VETO.
    Retourne 29 items ordonnés : section A → B → C → D → E.

    Args:
        seed: graine aléatoire pour reproductibilité (tests) ou None (aléatoire)

    Returns:
        Liste de 29 dicts-items prêts à être envoyés au frontend.
    """
    if seed is not None:
        random.seed(seed)

    banque = charger_banque()
    par_dim: dict[str, list] = {d: [] for d in DIMS}
    veto_items = []

    for item in banque:
        if item["dimension"] == "VETO":
            veto_items.append(item)
        elif item["dimension"] in DIMS:
            par_dim[item["dimension"]].append(item)

    session = []
    for d in DIMS:
        candidats = par_dim[d]
        k = min(ITEMS_PER_DIM, len(candidats))
        session.extend(random.sample(candidats, k))

    session.extend(veto_items)  # VETO toujours présents, jamais aléatoires

    # Réordonner par section A → B → C → D → E pour affichage cohérent
    order = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}
    session.sort(key=lambda x: order.get(x.get("section", "B"), 5))
    return session


def calculer_scores_riasec(reponses: dict[str, int]) -> dict[str, float]:
    """
    Calcule les 6 scores RIASEC normalisés 0-100.

    Fonctionne avec n'importe quel sous-ensemble d'items de la banque
    (normalisation automatique par rapport aux items soumis).

    Args:
        reponses: {'B_R_01': 4, 'B_I_03': 2, ...} ou {'Q01': 4, ...} (compat. ascendante)
                  Items Section D (VETO) présents mais ignorés du calcul.

    Returns:
        {'R': 72.4, 'I': 85.1, 'A': 34.0, 'S': 61.2, 'E': 55.8, 'C': 48.3}

    Raises:
        ValueError: réponse manquante ou valeur hors Likert [1-5]
    """
    banque = charger_banque()

    # Index banque par id pour lookup O(1)
    index_banque = {item["id"]: item for item in banque}

    bruts: dict[str, float] = {d: 0.0 for d in DIMS}
    maxs:  dict[str, float] = {d: 0.0 for d in DIMS}

    for qid, rep_raw in reponses.items():
        item = index_banque.get(qid)
        if item is None:
            raise ValueError(
                f"Item {qid!r} inconnu dans la banque. "
                f"Vérifiez que les réponses correspondent aux items retournés par /api/profil/items."
            )

        dim = item["dimension"]

        # RÈGLE ABSOLUE — Section D = Veto Factors, jamais dans les scores RIASEC
        if dim == "VETO":
            continue

        if dim not in DIMS:
            continue  # dimension inconnue, skip

        rep = int(rep_raw)
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
        for d in DIMS
    }


def dimension_dominante(scores: dict[str, float]) -> str:
    """Retourne la lettre RIASEC avec le score le plus élevé."""
    return max(scores, key=scores.get)


def top3_dimensions(scores: dict[str, float]) -> list[str]:
    """Retourne les 3 dimensions dominantes triées (ex: ['I', 'R', 'C'])."""
    return sorted(scores, key=scores.get, reverse=True)[:3]
