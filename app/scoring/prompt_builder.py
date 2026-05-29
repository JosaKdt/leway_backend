"""
ORIAB — scoring/prompt_builder.py
Construction des prompts LLM — données enrichies, zéro PII (RD16).

Le prompt transmet au LLM :
  - Le vecteur RIASEC anonymisé du bachelier
  - Le Top 3 des filières validées AVEC leurs données marché béninoises
    (salaire médian, taux d'insertion, tendance IA, durée, saturation)
  - Le contexte RAG : les données marché sont tirées directement de la DB
    et injectées dans le prompt — c'est notre implémentation RAG légère.

PII jamais transmises : pas de nom, email, téléphone, ville.
"""
from typing import Optional


# ─── Mapping labels RIASEC ────────────────────────────────────────────────────
RIASEC_LABELS = {
    "R": "Réaliste (activités concrètes, manuel, technique)",
    "I": "Investigateur (analyse, recherche, sciences)",
    "A": "Artistique (créativité, expression, design)",
    "S": "Social (aide, enseignement, soins)",
    "E": "Entrepreneur (leadership, commerce, persuasion)",
    "C": "Conventionnel (ordre, chiffres, organisation)",
}

IA_TREND_LABELS = {
    0: "secteur en forte croissance grâce à l'IA",
    1: "secteur stable face à l'IA",
    2: "secteur en transformation par l'IA",
    3: "secteur fortement automatisable — risque élevé",
}


def _formater_filiere_rag(i: int, f: dict) -> str:
    """Formate une filière avec toutes ses données marché pour le contexte RAG."""
    tendance = IA_TREND_LABELS.get(f.get("tendance_ia") or 1, "")
    salaire = f.get("salaire_median_p50")
    taux = f.get("taux_insertion")
    saturation = f.get("indice_saturation")
    curricula = f.get("tendance_curricula_marche")
    duree = f.get("duree_theorique")

    lignes = [
        f"{i}. {f['nom']} (domaine : {f.get('domaine','N/D')})",
        f"   Score global : {f['weighted_score']}/100 "
        f"(RIASEC={round(f['sim_riasec']*100,0):.0f}%, "
        f"marché={round(f['score_marche']*100,0):.0f}%, "
        f"IA={round(f['score_ia']*100,0):.0f}%)",
        f"   Durée : {duree} ans",
    ]
    if salaire:
        lignes.append(f"   Salaire médian béninois : {salaire:,} FCFA/mois")
    if taux is not None:
        lignes.append(f"   Taux d'insertion : {taux:.0f}%")
    if saturation is not None:
        lignes.append(f"   Saturation du marché : {saturation:.0f}/1 "
                      f"({'marché saturé' if saturation > 0.6 else 'marché porteur'})")
    if tendance:
        lignes.append(f"   Impact IA : {tendance}")
    if curricula is not None:
        lignes.append(f"   Alignement curricula/marché : {curricula:.0f}/1")
    return "\n".join(lignes)


def construire_prompt_llm(
    scores: dict[str, float],
    top3: list[dict],
    dim_dominante: str,
    serie_bac: Optional[str] = None,
) -> str:
    """
    Prompt pour Claude Haiku 4.5 (mode cloud).
    Contexte RAG : données marché béninoises injectées directement.
    """
    profil = " | ".join(f"{k}={v:.0f}" for k, v in scores.items())
    label_dom = RIASEC_LABELS.get(dim_dominante, dim_dominante)
    serie_info = f"Série bac : {serie_bac}" if serie_bac else ""

    filieres_str = "\n\n".join(
        _formater_filiere_rag(i + 1, f)
        for i, f in enumerate(top3[:3])
    )

    return f"""Tu es un conseiller d'orientation expert pour les bacheliers béninois.

PROFIL PSYCHOMÉTRIQUE ANONYMISÉ
Scores RIASEC : {profil}
Dimension dominante : {label_dom}
{serie_info}

TOP 3 FILIÈRES RECOMMANDÉES (données réelles marché béninois 2025)
{filieres_str}

INSTRUCTIONS
Génère un rapport JSON valide en français naturel, accessible à un bachelier de 18 ans au Bénin.
Appuie-toi sur les données marché réelles fournies ci-dessus.
Sois encourageant mais honnête — mentionne les défis concrets (saturation, durée, salaire réel).
Aucun texte avant ou après le JSON. Aucun markdown.

FORMAT EXACT :
{{"rapport_synthese":"3 phrases max expliquant le profil et pourquoi ces filières","top3_justifiees":[{{"nom":"nom exact","score":0.0,"justification":"2 phrases avec données réelles","points_forts":["point 1","point 2"],"points_attention":["attention 1"]}}]}}"""


def construire_prompt_mistral(
    scores: dict[str, float],
    top3: list[dict],
    dim_dominante: str,
    serie_bac: Optional[str] = None,
) -> str:
    """
    Prompt optimisé pour Mistral 7B Instruct via Ollama.
    Format [INST]...[/INST] obligatoire pour Mistral.
    Plus direct et contraint que le prompt Haiku — Mistral suit mieux
    les instructions avec des exemples explicites.
    """
    profil = " | ".join(f"{k}={v:.0f}" for k, v in scores.items())
    serie_info = f" | Série bac: {serie_bac}" if serie_bac else ""

    filieres_str = "\n".join(
        f"- {f['nom']}: score={f['weighted_score']}, "
        f"salaire={f.get('salaire_median_p50', 'N/D')} FCFA/mois, "
        f"insertion={f.get('taux_insertion', 'N/D')}%, "
        f"durée={f.get('duree_theorique', '?')}ans, "
        f"IA={'croissance' if f.get('tendance_ia',1)==0 else 'stable' if f.get('tendance_ia',1)==1 else 'attention'}"
        for f in top3[:3]
    )

    return (
        f"[INST] Tu es conseiller d'orientation au Bénin.\n"
        f"Profil RIASEC : {profil}{serie_info}\n"
        f"Filières recommandées (données marché béninoises) :\n{filieres_str}\n\n"
        f"Réponds UNIQUEMENT avec ce JSON valide, sans texte avant/après :\n"
        f'{{"rapport_synthese":"explication 3 phrases max en français simple",'
        f'"top3_justifiees":[{{"nom":"filière","score":0.0,'
        f'"justification":"2 phrases avec les vrais chiffres",'
        f'"points_forts":["point"],"points_attention":["attention"]}}]}} [/INST]'
    )
