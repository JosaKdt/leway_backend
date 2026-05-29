"""
ORIAB — providers/ollama.py
Provider Mistral 7B Instruct via Ollama (LLM_MODE=local).
Fallback structurel avec données marché si Ollama non disponible.
"""
import os, json
import httpx
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model    = os.getenv("OLLAMA_MODEL", "mistral")

    async def generer_rapport(self, prompt: str) -> dict:
        """Appelle Ollama avec format=json pour forcer la sortie JSON."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model":  self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.3,   # Bas = plus cohérent pour JSON
                        "top_p": 0.9,
                        "num_predict": 1500,
                    },
                },
            )
            resp.raise_for_status()
            raw = resp.json().get("response", "{}")
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)

    async def generer_avec_fallback(
        self,
        scores: dict,
        top3: list,
        dim_dominante: str,
        serie_bac: str | None = None,
    ) -> dict:
        """Tente Ollama, retourne un rapport structurel si indisponible."""
        try:
            from app.scoring.prompt_builder import construire_prompt_mistral
            prompt = construire_prompt_mistral(scores, top3, dim_dominante, serie_bac)
            return await self.generer_rapport(prompt)
        except Exception as e:
            return self._fallback(scores, top3, dim_dominante, str(e))

    def _fallback(
        self, scores: dict, top3: list, dim: str, err: str
    ) -> dict:
        """
        Rapport de secours sans LLM — utilise directement les données marché
        de la DB pour produire un rapport structuré mais non généré.
        """
        labels = {
            "R": "Réaliste — tu es attiré par les activités concrètes et techniques",
            "I": "Investigateur — tu aimes analyser, comprendre et résoudre des problèmes",
            "A": "Artistique — la créativité et l'expression sont au cœur de ta personnalité",
            "S": "Social — aider, enseigner et accompagner les autres te motive",
            "E": "Entrepreneur — leadership et commerce correspondent à tes ambitions",
            "C": "Conventionnel — tu excelles dans l'organisation et le travail structuré",
        }
        top3_dims = sorted(scores, key=scores.get, reverse=True)[:3]
        profil_desc = ", ".join(
            f"{d} ({scores[d]:.0f}/100)" for d in top3_dims
        )

        justifications = []
        for f in top3[:3]:
            salaire = f.get("salaire_median_p50")
            taux    = f.get("taux_insertion")
            duree   = f.get("duree_theorique", "?")
            justif  = f"Compatibilité RIASEC : {f['sim_riasec']:.0%}. "
            if salaire and taux:
                justif += (
                    f"Données marché béninoises : salaire médian {salaire:,} FCFA/mois, "
                    f"taux d'insertion {taux:.0f}%, durée {duree} ans."
                )
            justifications.append({
                "nom":   f["nom"],
                "score": f["weighted_score"],
                "justification": justif,
                "points_forts": [
                    f"Score de compatibilité : {f['weighted_score']:.1f}/100",
                    f"Taux d'insertion : {taux:.0f}%" if taux else "Filière reconnue",
                ],
                "points_attention": [
                    "Consulte un conseiller pour plus de détails",
                    f"Durée estimée : {duree} ans",
                ],
            })

        return {
            "rapport_synthese": (
                f"Ton profil dominant est {labels.get(dim, dim)} ({profil_desc}). "
                f"Les filières recommandées correspondent à ta configuration psychologique "
                f"et aux réalités du marché du travail béninois. "
                f"(Rapport généré hors-ligne — LLM non disponible)"
            ),
            "top3_justifiees": justifications,
            "mode": "fallback_hors_llm",
        }
