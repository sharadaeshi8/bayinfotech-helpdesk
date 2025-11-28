from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    async def generate_answer(self, prompt: str, context: str, history: List[Dict[str, str]]) -> str:
        """Generate an answer based on prompt, context, and history."""
        pass

    @abstractmethod
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for a given text."""
        pass

    @abstractmethod
    async def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the text."""
        pass
