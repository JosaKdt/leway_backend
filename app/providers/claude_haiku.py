"""
ORIAB — providers/claude_haiku.py
Provider Claude Haiku 4.5 (LLM_MODE=cloud).
Activer en mettant LLM_MODE=cloud + ANTHROPIC_API_KEY valide dans .env
"""
import os, json
import anthropic
from .base import LLMProvider

SYSTEM_PROMPT = (
    "Tu es un conseiller d'orientation expert en filières universitaires du Bénin. "
    "Tu reçois un profil RIASEC anonymisé et des données réelles du marché béninois. "
    "Tu génères des recommandations en français naturel, accessible à un bachelier de 18 ans. "
    "Réponds UNIQUEMENT avec un JSON valide — aucun texte avant/après, sans markdown. "
    'Format : {"rapport_synthese":"...","top3_justifiees":['
    '{"nom":"...","score":0.0,"justification":"...","points_forts":["..."],"points_attention":["..."]}]}'
)


class ClaudeHaikuProvider(LLMProvider):
    def __init__(self):
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key or "PLACEHOLDER" in key:
            raise ValueError(
                "ANTHROPIC_API_KEY non configurée. "
                "Définissez-la dans .env ou utilisez LLM_MODE=local."
            )
        self.client = anthropic.Anthropic(api_key=key)
        self.model  = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

    async def generer_rapport(self, prompt: str) -> dict:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
