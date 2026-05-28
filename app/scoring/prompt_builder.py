"""
LÉWAY — scoring/prompt_builder.py
Construit les prompts LLM anonymisés.
PII jamais transmis au LLM — règle RGPD/APDP absolue.
"""


def construire_prompt(scores: dict[str, float], top5: list[dict]) -> str:
    """Prompt générique pour Claude Haiku (mode cloud)."""
    profil = " / ".join(f"{k}={v:.0f}" for k, v in scores.items())
    filieres = "\n".join(
        f"{i+1}. {f['filiere']} (Score={f['weighted_score']}, "
        f"RIASEC={f['sim_riasec']:.2f}, Durée={f['duree_ans']}ans)"
        for i, f in enumerate(top5)
    )
    return (
        f"Profil RIASEC anonymisé : {profil}\n\n"
        f"Top filières recommandées :\n{filieres}\n\n"
        "Génère le rapport JSON selon le format demandé. "
        "Français naturel, accessible à un lycéen béninois de 18 ans."
    )


def construire_prompt_mistral(scores: dict[str, float], top5: list[dict]) -> str:
    """Prompt optimisé Mistral 7B Instruct — forcé JSON, pas de markdown."""
    profil = " / ".join(f"{k}={v:.0f}" for k, v in scores.items())
    filieres = "\n".join(
        f"- {f['filiere']}: score={f['weighted_score']}, sim={f['sim_riasec']:.2f}"
        for f in top5
    )
    return (
        "[INST] Tu es un conseiller d'orientation pour bacheliers béninois.\n"
        f"Profil RIASEC : {profil}\n"
        f"Filières recommandées :\n{filieres}\n\n"
        "Réponds UNIQUEMENT avec un JSON valide, sans texte avant ou après, sans markdown.\n"
        'Format exact : {"rapport_synthese":"3 phrases max","top5_justifiees":['
        '{"filiere":"nom","score":0.0,"justification":"2 phrases",'
        '"points_forts":["p1"],"points_attention":["a1"]}]} [/INST]'
    )
