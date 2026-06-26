"""
ORIAB — providers/groq_provider.py
Provider Groq (LLM_MODE=groq) — inférence ultra-rapide, gratuite,
modèles open-source (Llama, Mistral) hébergés sur matériel LPU dédié.
Aucun téléchargement local nécessaire, contrairement à Ollama.
"""
import json
from groq import Groq
from app.core.config import settings
from .base import LLMProvider

SYSTEM_PROMPT = (
    "Tu es un conseiller d'orientation expert en filières universitaires du Bénin. "
    "Tu reçois un profil RIASEC anonymisé et des données réelles du marché béninois. "
    "Tu génères des recommandations en français naturel, accessible à un bachelier de 18 ans. "
    "Réponds UNIQUEMENT avec un JSON valide — aucun texte avant/après, sans markdown. "
    'Format : {"rapport_synthese":"...","top3_justifiees":['
    '{"nom":"...","score":0.0,"justification":"...","points_forts":["..."],"points_attention":["..."]}]}'
)


class GroqProvider(LLMProvider):
    def __init__(self):
        # IMPORTANT : on lit via pydantic_settings (settings.GROQ_API_KEY),
        # PAS via os.getenv() directement — voir le même bug corrigé
        # pour LLM_MODE dans recommandations.py.
        key = settings.GROQ_API_KEY
        if not key:
            raise ValueError(
                "GROQ_API_KEY non configurée. "
                "Créez un compte gratuit sur console.groq.com et définissez la clé dans .env."
            )
        self.client = Groq(api_key=key)
        self.model = settings.GROQ_MODEL

    async def generer_rapport(self, prompt: str) -> dict:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        raw = resp.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)