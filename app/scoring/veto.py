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

Normalisation des séries bac (Guide MESRS 2024-2025) :
  A1, A2     → A   (Lettres variantes)
  G1, G2, G3 → G   (Gestion variantes)
  F1, F2, F3 → F   (Technique variantes)
  EA, TI, DT, DEAT → conservés tels quels
"""
from typing import Optional

# Mapping horizon textuel → durée max en années
HORIZON_MAP = {"court": 3, "moyen": 5, "long": 99}

# Mapping tranche ressources_financieres → budget annuel estimé en FCFA
# Tranche 1 : < 100k/an | 2 : 100k-250k/an | 3 : 250k-500k/an | 4 : > 500k/an
BUDGET_MAP = {1: 80_000, 2: 180_000, 3: 380_000, 4: 600_000}

# Séries multi-caractères à conserver INTACTES (pas de troncature sur le 1er char)
SERIES_INTACTES = {"EA", "TI", "DT", "DEAT", "STI"}


def normaliser_serie(serie: str) -> str:
    """
    Normalise la série bac du bachelier pour la comparaison.

    Guide MESRS 2024-2025 : A1/A2 → A, G1/G2/G3 → G, F1/F2/F3 → F
    Les séries multi-lettres (EA, TI, DT, DEAT) sont conservées.

    Exemples :
        "A2"  → "A"    # littéraire devient A → match avec ["A","B","C","D"]
        "G3"  → "G"    # gestion variante → match avec ["G","B","C","D"]
        "EA"  → "EA"   # agriculture conservé
        "C"   → "C"    # inchangé
    """
    if not serie:
        return serie
    s = serie.strip().upper()
    # Conserver les séries multi-lettres connues
    if s in SERIES_INTACTES:
        return s
    # Tronquer si: 2 chars, 2ème char est un chiffre (A1→A, G2→G, F3→F)
    if len(s) == 2 and s[1].isdigit():
        return s[0]
    return s


def appliquer_veto(
    top5: list[dict],
    ressources_financieres: Optional[int],
    mobilite_geo: Optional[bool],
    horizon_temporel: Optional[str],
    serie_bac: Optional[str] = None,
) -> dict[str, list]:
    """
    Filtre les filières selon les contraintes du bachelier.

    Args:
        top5:                  sortie de toutes_filieres_scorees() — liste triée par WS
        ressources_financieres: tranche 1-4 (Section D du questionnaire)
        mobilite_geo:          peut quitter le Bénin (Section D)
        horizon_temporel:      'court' | 'moyen' | 'long' (Section C)
        serie_bac:             ex: 'C', 'D', 'A1', 'A2' — depuis le profil bachelier

    Returns:
        {
          'top5_valides': [...],   — filières passant tous les veto (triées par WS)
          'eliminees':    [{'nom': ..., 'weighted_score': ..., 'raisons_veto': [...]}]
        }
    """
    duree_max   = HORIZON_MAP.get(horizon_temporel or "moyen", 5)
    budget_fcfa = BUDGET_MAP.get(ressources_financieres or 2, 180_000)
    peut_partir = mobilite_geo if mobilite_geo is not None else False

    # Normaliser la série bac une seule fois pour toutes les comparaisons
    serie_norm = normaliser_serie(serie_bac) if serie_bac else None

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
                f"Budget estimé {budget_fcfa:,} FCFA/an "
                f"< minimum requis {budget_min:,} FCFA/an"
            )

        # VETO 3 — Mobilité internationale
        if cand.get("mobilite_requise", False) and not peut_partir:
            raisons.append(
                "Cette filière nécessite une mobilité internationale "
                "que tu n'as pas indiquée comme possible"
            )

        # VETO 4 — Série bac incompatible
        # Comparaison avec série normalisée (A2→A, G1→G, etc.)
        series_requises = cand.get("serie_bac_requise", [])
        if serie_norm and series_requises:
            # Normaliser aussi les séries de la filière pour comparaison équitable
            series_norm_filiere = [normaliser_serie(s) for s in series_requises]
            if serie_norm not in series_norm_filiere:
                raisons.append(
                    f"Ta série ({serie_bac}) n'est pas compatible avec les séries "
                    f"recommandées pour cette filière ({', '.join(series_requises)})"
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
