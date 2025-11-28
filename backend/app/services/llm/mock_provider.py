from typing import List, Dict, Any
from app.services.llm.base import LLMProvider

class MockLLMProvider(LLMProvider):
    async def generate_answer(self, prompt: str, context: str, history: List[Dict[str, str]]) -> str:
        return f"Mock Answer to: {prompt}"

    async def get_embeddings(self, text: str) -> List[float]:
        return [0.1] * 1536

    async def estimate_tokens(self, text: str) -> int:
        return len(text.split())
