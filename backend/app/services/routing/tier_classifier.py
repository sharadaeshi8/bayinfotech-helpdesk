from typing import Tuple
from app.models.schemas import TicketPriority, Role

class TierClassifier:
    """Enhanced tier classification with comprehensive keyword matching."""
    
    # Tier 0: Self-service items (implicit - not listed, falls through to default)
    TIER_0_KEYWORDS = [
        "password", "reset", "forgot", "login", "username", 
        "mfa", "2fa", "two factor", "authenticator",
        "access training", "lab setup", "getting started"
    ]
    
    # Tier 1: Common technical issues
    TIER_1_KEYWORDS = [
        "email", "wifi", "vpn", "slow", "latency", "performance",
        "session timeout", "disconnected", "can't connect",
        "network", "dns", "browser", "firefox", "chrome", "safari",
        "lab access", "lab not loading", "environment"
    ]
    
    # Tier 2: Platform/infrastructure issues
    TIER_2_KEYWORDS = [
        "docker", "container", "kubernetes", "pod", "deployment",
        "error", "timeout", "failed", "crash", "freeze",
        "kernel", "vm", "virtual machine", "snapshot",
        "data recovery", "backup", "restore",
        "module", "course", "lab vm", "environment mapping"
    ]
    
    # Tier 3: Critical/security issues  
    TIER_3_KEYWORDS = [
        "kernel panic", "security breach", "data loss", "corruption",
        "outage", "down", "unavailable", "init failed",
        "missing /opt/startup.sh", "platform down",
        "multiple users affected", "widespread", "critical",
        "unauthorized access", "compromised", "injection"
    ]
    
    # Multi-word phrases for better accuracy (checked first)
    CRITICAL_PHRASES = [
        "kernel panic", "security breach", "data loss", "platform down",
        "system outage", "multiple users affected", "unauthorized access",
        "production down", "init failed"
    ]
    
    HIGH_PRIORITY_PHRASES = [
        "can't access", "unable to", "not working", "keeps crashing",
        "lost my work", "vm crashed", "environment reset"
    ]

    @staticmethod
    def classify_tier_and_severity(text: str, role: Role) -> Tuple[str, TicketPriority]:
        """
        Classify tier and severity deterministically using keyword matching.
        Same input always produces same output (deterministic).
        """
        text_lower = text.lower()
        
        # Default (Tier 0)
        tier = "TIER_0"
        severity = TicketPriority.LOW
        
        # 1. Check critical phrases first (highest priority)
        for phrase in TierClassifier.CRITICAL_PHRASES:
            if phrase in text_lower:
                tier = "TIER_3"
                severity = TicketPriority.CRITICAL
                return tier, severity
        
        # 2. Check high priority phrases
        has_high_priority_phrase = any(phrase in text_lower for phrase in TierClassifier.HIGH_PRIORITY_PHRASES)
        
        # 3. Check Tier 3 keywords
        for keyword in TierClassifier.TIER_3_KEYWORDS:
            if keyword in text_lower:
                tier = "TIER_3"
                severity = TicketPriority.HIGH
                # Upgrade to CRITICAL if it's a critical keyword
                if keyword in ["kernel panic", "security breach", "data loss", "outage", "unauthorized access"]:
                    severity = TicketPriority.CRITICAL
                return tier, severity
        
        # 4. Check Tier 2 keywords
        for keyword in TierClassifier.TIER_2_KEYWORDS:
            if keyword in text_lower:
                tier = "TIER_2"
                # Upgrade severity if high priority phrase present
                severity = TicketPriority.HIGH if has_high_priority_phrase else TicketPriority.MEDIUM
                return tier, severity
        
        # 5. Check Tier 1 keywords
        for keyword in TierClassifier.TIER_1_KEYWORDS:
            if keyword in text_lower:
                tier = "TIER_1"
                severity = TicketPriority.MEDIUM if has_high_priority_phrase else TicketPriority.LOW
                return tier, severity
        
        # 6. Check Tier 0 keywords
        for keyword in TierClassifier.TIER_0_KEYWORDS:
            if keyword in text_lower:
                tier = "TIER_0"
                severity = TicketPriority.LOW
                return tier, severity
        
        # 7. Role-based adjustments
        if role == Role.ADMIN:
            # Admins reporting issues are likely infrastructure problems
            if any(word in text_lower for word in ["server", "database", "production", "staging"]):
                tier = "TIER_2"
                severity = TicketPriority.HIGH
        
        return tier, severity
