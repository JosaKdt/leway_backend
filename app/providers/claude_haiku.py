"""
LÉWAY — providers/claude_haiku.py
Activer : LLM_MODE=cloud + ANTHROPIC_API_KEY valide dans .env
"""
import os, json
import anthropic
from .base import LLMProvider

SYSTEM = (
    "Tu es un conseiller d'orientation expert en filières universitaires du Bénin. "
    "Réponds UNIQUEMENT avec un JSON valide — aucun texte avant/après, sans markdown. "
    'Format : {"rapport_synthese":"...","top5_justifiees":['
    '{"filiere":"...","score":0.0,"justification":"...","points_forts":["..."],"points_attention":["..."]}]}'
)


class ClaudeHaikuProvider(LLMProvider):
    def __init__(self):
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key or "PLACEHOLDER" in key:
            raise ValueError(
                "ANTHROPIC_API_KEY non configurée. "
                "Remplissez .env ou utilisez LLM_MODE=local."
            )
        self.client = anthropic.Anthropic(api_key=key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

    async def generer_rapport(self, prompt: str) -> dict:
        resp = self.client.messages.create(
            model=self.model, max_tokens=1500,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
