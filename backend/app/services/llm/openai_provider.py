from typing import List, Dict, Any
import openai
from app.core.config import settings
from app.services.llm.base import LLMProvider
import tiktoken

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4-turbo-preview"
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")

    async def generate_answer(self, prompt: str, context: str, history: List[Dict[str, str]]) -> str:
        system_prompt = """You are an AI Help Desk assistant for a technical training platform. You MUST follow these rules STRICTLY:

1. ONLY use information from the provided knowledge base (KB) chunks below
2. If information is not in the KB chunks, you MUST say "This is not covered in our knowledge base"
3. NEVER make up commands, procedures, URLs, or configuration values
4. DO NOT cite the KB document ID or filename in your response text. This information is displayed separately.
5. Keep responses concise and actionable
6. Use step-by-step format for procedures

7. ASK CLARIFYING QUESTIONS when needed. You MUST ask for:
   - **Module/Lab**: "Which specific lab or module are you working on?" when user mentions:
     * "the lab", "my lab", "this exercise", "the course"
   - **Environment**: "Which environment (staging/production/dev) are you accessing?" when user mentions:
     * "can't access", "login issues", "environment", "wrong page"
   - **Browser/OS**: "What browser and operating system are you using?" when user mentions:
     * "not loading", "page issue", "display problem", "won't open", "error message"
   - **Error Details**: "What exact error message are you seeing?" when user mentions:
     * "error", "failed", "not working", "broken"
   
8. If multiple KB articles could apply, ask which scenario matches before providing solution
9. For vague issues, gather details before attempting diagnosis
10. If user's issue is ambiguous, clarify scope before escalating

KNOWLEDGE BASE CHUNKS:
{context}

Provide a helpful response following all rules above."""

        # Manage context window
        messages = await self.manage_context_window(system_prompt, context, history, prompt)

        response = await self.client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=0.1, # Lower temperature for strictness
        )
        return response.choices[0].message.content

    async def manage_context_window(self, system_template: str, context: str, history: List[Dict[str, str]], current_prompt: str) -> List[Dict[str, str]]:
        """
        Manages the context window to stay within limits (e.g., 8000 tokens).
        Strategies:
        1. Reduce history (5 -> 3 turns)
        2. Reduce KB chunks (truncate context)
        """
        MAX_TOKENS = 8000
        
        # Helper to construct messages
        def construct_messages(ctx, hist):
            msgs = [{"role": "system", "content": system_template.replace("{context}", ctx)}]
            for msg in hist:
                msgs.append({"role": msg["role"], "content": msg["content"]})
            msgs.append({"role": "user", "content": f"USER MESSAGE: {current_prompt}"})
            return msgs

        # 1. Try with full context and history
        messages = construct_messages(context, history)
        total_tokens = 0
        for msg in messages:
            total_tokens += await self.estimate_tokens(msg["content"])
            
        if total_tokens <= MAX_TOKENS:
            return messages
            
        print(f"Token limit exceeded ({total_tokens} > {MAX_TOKENS}). Applying reduction strategies...")
        
        # 2. Reduce history to last 3 turns
        reduced_history = history[-3:] if len(history) > 3 else history
        messages = construct_messages(context, reduced_history)
        
        total_tokens = 0
        for msg in messages:
            total_tokens += await self.estimate_tokens(msg["content"])
            
        if total_tokens <= MAX_TOKENS:
            print("Reduced history to fit context window.")
            return messages
            
        # 3. Reduce context (KB chunks)
        # Assuming context is separated by "\n\n" or "---"
        # We'll aggressively truncate to top 3 chunks (approx half size if we assume 5 chunks originally)
        chunks = context.split("---")
        if len(chunks) > 3:
            reduced_context = "---".join(chunks[:3])
            messages = construct_messages(reduced_context, reduced_history)
            
            total_tokens = 0
            for msg in messages:
                total_tokens += await self.estimate_tokens(msg["content"])
                
            if total_tokens <= MAX_TOKENS:
                print("Reduced KB chunks to fit context window.")
                return messages
        
        # 4. Emergency truncation (if still too big)
        # Just return minimal context
        print("Emergency truncation applied.")
        return construct_messages(context[:2000] + "... [TRUNCATED]", [])

    async def get_embeddings(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        response = await self.client.embeddings.create(
            input=[text],
            model=self.embedding_model
        )
        return response.data[0].embedding

    async def estimate_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
