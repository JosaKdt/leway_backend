"""
LÉWAY — providers/ollama.py
Provider Mistral 7B local via Ollama (LLM_MODE=local).
Inclut fallback structurel si Ollama non démarré.
"""
import os, json
import httpx
from .base import LLMProvider
from scoring.prompt_builder import construire_prompt_mistral


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")

    async def generer_rapport(self, prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model, "prompt": prompt,
                    "stream": False, "format": "json",
                    "options": {"temperature": 0.3, "top_p": 0.9},
                },
            )
            resp.raise_for_status()
            raw = resp.json().get("response", "{}")
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)

    async def generer_avec_fallback(self, scores: dict, top5: list) -> dict:
        try:
            prompt = construire_prompt_mistral(scores, top5)
            return await self.generer_rapport(prompt)
        except Exception as e:
            return self._fallback(scores, top5, str(e))

    def _fallback(self, scores: dict, top5: list, err: str) -> dict:
        labels = {
            "R": "Réaliste — activités concrètes et techniques",
            "I": "Investigateur — recherche et analyse",
            "A": "Artistique — créativité et expression",
            "S": "Social — aide et enseignement",
            "E": "Entrepreneur — leadership et commerce",
            "C": "Conventionnel — ordre et structure",
        }
        dom = max(scores, key=scores.get)
        return {
            "rapport_synthese": (
                f"Ton profil dominant est {labels.get(dom, dom)}. "
                "Les filières recommandées correspondent à tes intérêts principaux. "
                f"(Rapport hors-ligne — LLM non disponible)"
            ),
            "top5_justifiees": [
                {
                    "filiere": f["filiere"], "score": f["weighted_score"],
                    "justification": (
                        f"Compatible à {f['sim_riasec']:.0%} avec ton profil RIASEC. "
                        f"Durée estimée : {f['duree_ans']} ans."
                    ),
                    "points_forts": ["Bonne compatibilité de profil"],
                    "points_attention": ["Consulte un conseiller pour plus de détails"],
                }
                for f in top5[:5]
            ],
            "mode": "fallback_hors_llm",
        }
