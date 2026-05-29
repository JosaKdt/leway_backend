"""
ORIAB — scoring/veto.py
Veto Factors — filtres éliminatoires appliqués AVANT le LLM (RD18).

Les données de veto viennent de deux sources :
  1. Le profil du bachelier (ProfilPsychometrique) — budget, mobilité, horizon
  2. La fiche filière (Filiere.veto_factors JSONB) — budget_min, série bac requise

Règles :
  VETO 1 — Durée filière > horizon temporel du bachelier
  VETO 2 — Budget insuffisant (filière.budget_min_fcfa > budget_bachelier)
  VETO 3 — Mobilité internationale requise mais bachelier non mobile
  VETO 4 — Série bac incompatible (si série connue et liste non vide)
"""
from typing import Optional

# Mapping horizon textuel → durée max en années
HORIZON_MAP = {"court": 3, "moyen": 5, "long": 99}

# Mapping tranche ressources_financieres → budget mensuel estimé en FCFA
# Tranche 1 : < 50 000   | Tranche 2 : 50k-150k | Tranche 3 : 150k-300k | Tranche 4 : > 300k
BUDGET_MAP = {1: 40_000, 2: 100_000, 3: 220_000, 4: 400_000}


def appliquer_veto(
    top5: list[dict],
    ressources_financieres: Optional[int],
    mobilite_geo: Optional[bool],
    horizon_temporel: Optional[str],
    serie_bac: Optional[str] = None,
) -> dict[str, list]:
    """
    Filtre les filières du Top 5 selon les contraintes du bachelier.

    Args:
        top5:                  sortie de top5_filieres() — liste de dicts enrichis
        ressources_financieres: tranche 1-4 (Section D du questionnaire)
        mobilite_geo:          peut quitter le Bénin (Section D)
        horizon_temporel:      'court' | 'moyen' | 'long' (Section C)
        serie_bac:             ex: 'C', 'D', 'A1' — depuis le profil bachelier

    Returns:
        {
          'top5_valides': [...],   — filières passant tous les veto
          'eliminees':    [{'nom': ..., 'weighted_score': ..., 'raisons_veto': [...]}]
        }
    """
    duree_max    = HORIZON_MAP.get(horizon_temporel or "moyen", 5)
    budget_fcfa  = BUDGET_MAP.get(ressources_financieres or 2, 100_000)
    peut_partir  = mobilite_geo if mobilite_geo is not None else False

    valides, eliminees = [], []

    for cand in top5:
        raisons = []

        # VETO 1 — Durée incompatible avec l'horizon
        duree = cand.get("duree_theorique") or 3
        if duree > duree_max:
            raisons.append(
                f"Durée {duree} ans dépasse ton horizon souhaité ({duree_max} ans)"
            )

        # VETO 2 — Budget insuffisant
        budget_min = cand.get("budget_min_fcfa") or 0
        if budget_min > 0 and budget_fcfa < budget_min:
            raisons.append(
                f"Budget estimé {budget_fcfa:,} FCFA/mois "
                f"< minimum requis {budget_min:,} FCFA/mois"
            )

        # VETO 3 — Mobilité internationale
        if cand.get("mobilite_requise", False) and not peut_partir:
            raisons.append(
                "Cette filière nécessite une mobilité internationale "
                "que tu n'as pas indiquée comme possible"
            )

        # VETO 4 — Série bac incompatible (si info disponible)
        series_requises = cand.get("serie_bac_requise", [])
        if serie_bac and series_requises and serie_bac not in series_requises:
            raisons.append(
                f"Ta série ({serie_bac}) n'est pas dans les séries recommandées "
                f"({', '.join(series_requises)})"
            )

        if raisons:
            eliminees.append({
                "id_filiere":     cand["id_filiere"],
                "nom":            cand["nom"],
                "weighted_score": cand["weighted_score"],
                "raisons_veto":   raisons,
            })
        else:
            valides.append(cand)

    return {"top5_valides": valides, "eliminees": eliminees}
