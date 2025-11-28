from typing import List, Dict
import re
import base64

class GuardrailPolicy:
    """Enhanced guardrail policies with comprehensive jailbreak protection."""
    
    # Strict Blocked Patterns (regex for flexibility)
    BLOCKED_PATTERNS = {
        "unauthorized_access": [
            r"access host machine", r"access hypervisor", r"ssh to host", r"root access", 
            r"escalate privileges", r"sudo su", r"switch to admin", r"gain admin",
            r"privilege escalation", r"become root", r"run as administrator"
        ],
        "security_bypass": [
            r"disable logging", r"turn off audit", r"bypass security", r"skip authentication", 
            r"remove monitoring", r"disable firewall", r"circumvent", r"workaround security",
            r"ignore security", r"disable protection"
        ],
        "prohibited_modifications": [
            r"edit /etc/hosts", r"modify hosts file", r"change DNS manually", r"edit system files", 
            r"kernel parameters", r"hypervisor settings", r"modify registry", r"change system config",
            r"alter boot", r"modify grub"
        ],
        "destructive_commands": [
            r"reset all environments", r"delete all users", r"drop database", r"drop table",
            r"rm -rf", r"wipe system", r"format drive", r"delete \*", r"truncate table",
            r"del /f /s /q", r"rmdir /s", r"format c:"
        ],
        "instruction_override": [
            r"ignore (all )?previous (instructions|prompts)", 
            r"disregard (all )?previous",
            r"forget (all )?(instructions|rules|guidelines)",
            r"new instructions?:", r"override (all )?instructions",
            r"you are (now |)a ", r"act as (a |an )",
            r"pretend (you are|to be)", r"roleplay",
            r"system prompt", r"jailbreak", r"dan mode"
        ],
        "command_injection": [
            r"&&\s*(?:cat|ls|pwd|whoami|id)", 
            r";\s*(?:cat|ls|pwd|whoami|id)",
            r"\|\s*(?:cat|ls|pwd|whoami|id)",
            r"`[^`]*`",  # Backtick command substitution
            r"\$\([^)]*\)",  # Command substitution
            r"</script>", r"<script", r"javascript:",
            r"eval\(", r"exec\(", r"system\(", r"shell_exec"
        ],
        "sql_injection": [
            r"'\s*OR\s*'", r"'\s*or\s*'", r"--\s", r";\s*DROP\s+TABLE",
            r"UNION\s+SELECT", r"' union select", r"'; drop table",
            r"1=1", r"' or 1=1", r"admin'--", r"' or 'a'='a"
        ],
        "data_exfiltration": [
            r"cat /etc/passwd", r"cat /etc/shadow", r"dump database",
            r"export all", r"download all", r"backup to external",
            r"send to http://", r"curl.*http", r"wget.*http"
        ],
        "social_engineering": [
            r"my manager (said|told|instructed)", r"boss said", r"emergency access",
            r"urgent: need access", r"CEO (requested|needs)", r"director approved",
            r"password is", r"just give me", r"just show me"
        ]
    }
    
    # Unicode obfuscation patterns (e.g., using special characters to bypass filters)
    UNICODE_PATTERNS = [
        r"ｓｕｄｏ", r"ａｄｍｉｎ", r"ｒｏｏｔ",  # Fullwidth characters
        r"sudo.*[\u200B-\u200D]",  # Zero-width characters
        r"[^\x00-\x7F]+(?:sudo|admin|root)"  # Non-ASCII mixed with commands
    ]
    
    SENSITIVE_TOPICS = [
        "politics", "religion", "hate speech", "sexual content", "self-harm",
        "violence", "discrimination", "harassment"
    ]

    ROLE_POLICIES = {
        "trainee": ["unauthorized_access", "security_bypass", "prohibited_modifications", "destructive_commands"],
        "operator": ["destructive_commands"],
        "admin": []  # Admins can still be blocked for security bypass attempts
    }

    @staticmethod
    def check_patterns(text: str) -> List[str]:
        """Check for blocked patterns including advanced jailbreak attempts."""
        violations = []
        text_lower = text.lower()
        
        # 1. Standard pattern matching
        for category, patterns in GuardrailPolicy.BLOCKED_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    violations.append(f"Blocked pattern detected in category '{category}': '{pattern}'")
        
        # 2. Check for base64 encoded attempts
        if GuardrailPolicy._check_base64_encoding(text):
            violations.append("Blocked pattern detected in category 'encoding_bypass': 'base64 encoded content'")
        
        # 3. Check for unicode obfuscation
        for pattern in GuardrailPolicy.UNICODE_PATTERNS:
            if re.search(pattern, text):
                violations.append("Blocked pattern detected in category 'unicode_obfuscation': 'non-standard characters'")
        
        # 4. Check for sensitive topics
        for topic in GuardrailPolicy.SENSITIVE_TOPICS:
            if topic in text_lower:
                violations.append(f"Blocked pattern detected in category 'sensitive_content': '{topic}'")
        
        return violations
    
    @staticmethod
    def _check_base64_encoding(text: str) -> bool:
        """Detect potential base64 encoded malicious commands."""
        # Look for base64-like strings (long alphanumeric with = padding)
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(base64_pattern, text)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore').lower()
                # Check if decoded content contains dangerous commands
                dangerous_terms = ['sudo', 'rm -rf', 'drop table', 'cat /etc', 'wget', 'curl']
                if any(term in decoded for term in dangerous_terms):
                    return True
            except:
                continue
        
        return False

    @staticmethod
    def get_role_restrictions(role: str) -> List[str]:
        """Get role-based restrictions."""
        restrictions = {
            "user": ["system_config", "user_management", "logs"],
            "support": ["admin_logs", "billing"],
            "admin": []
        }
        return restrictions.get(role, [])
