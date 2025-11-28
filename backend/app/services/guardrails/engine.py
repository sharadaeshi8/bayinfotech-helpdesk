from typing import List, Tuple
from app.services.llm.base import LLMProvider
from app.services.guardrails.policies import GuardrailPolicy

class GuardrailEngine:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def check_safety(self, text: str, role: str) -> Tuple[bool, str]:
        # 1. Pattern-based checks (Fast)
        violations = GuardrailPolicy.check_patterns(text)
        if violations:
            # Extract category from the first violation message
            # Format: "Blocked pattern detected in category '{category}': '{pattern}'"
            import re
            first_violation = violations[0]
            category_match = re.search(r"category '([^']+)':", first_violation)
            category = category_match.group(1) if category_match else "unknown"
            
            # Determine severity and template
            high_severity_categories = ["security_bypass", "unauthorized_access", "destructive_commands"]
            
            if category in high_severity_categories:
                response = (
                    "This request cannot be fulfilled as it involves bypassing security controls. "
                    "This incident has been logged and flagged for review.\n\n"
                    "If you have a legitimate business need for this action, please submit a formal request "
                    "through your team lead with appropriate justification.\n\n"
                    "For immediate assistance with your current task within policy guidelines, please describe your underlying goal."
                )
            else:
                response = (
                    f"I cannot provide assistance with this action as it violates system security policies. "
                    "This request has been logged.\n\n"
                    "For legitimate system administration needs, please contact your supervisor or submit a support ticket "
                    "through the proper channels.\n\n"
                    "Is there something else I can help you with within my allowed scope?"
                )
                
            return False, response

        # 2. Role-based checks (if applicable to the prompt content - simplified here)
        # In a real system, we'd classify the intent first, then check against role restrictions.
        
        # 3. Semantic Safety Check (LLM-based - Slower but smarter)
        # We skip this for now to save tokens/time in this demo, but here's how it would look:
        # prompt = f"Is the following text safe and appropriate for a workplace helpdesk? Text: {text}"
        # safety_response = await self.llm.generate_answer(prompt, "", [])
        # if "unsafe" in safety_response.lower():
        #     return False, "Request blocked by semantic safety filter."

        return True, ""
