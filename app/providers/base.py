"""LÉWAY — providers/base.py — Interface Strategy LLM."""
import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generer_rapport(self, prompt: str) -> dict:
        ...


def get_provider() -> LLMProvider:
    mode = os.getenv("LLM_MODE", "local")
    if mode == "cloud":
        from .claude_haiku import ClaudeHaikuProvider
        return ClaudeHaikuProvider()
    from .ollama import OllamaProvider
    return OllamaProvider()
