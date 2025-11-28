"""
Unit Tests for Tier Classifier
Tests deterministic tier classification logic
"""
import pytest
from app.services.routing.tier_classifier import TierClassifier
from app.models.schemas import TicketPriority, Role


class TestTierClassifier:
    """Test suite for tier classification logic."""
    
    def test_tier_0_password_reset(self):
        """Test Tier 0 classification for password reset."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "I forgot my password", 
            Role.USER
        )
        assert tier == "TIER_0"
        assert severity == TicketPriority.LOW
    
    def test_tier_0_mfa_reset(self):
        """Test Tier 0 classification for MFA reset."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "Need to reset my 2FA authenticator", 
            Role.USER
        )
        assert tier == "TIER_0"
        assert severity == TicketPriority.LOW
    
    def test_tier_1_vpn_issue(self):
        """Test Tier 1 classification for VPN issues."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "Can't connect to VPN", 
            Role.USER
        )
        assert tier == "TIER_1"
        assert severity == TicketPriority.LOW
    
    def test_tier_1_lab_slow(self):
        """Test Tier 1 classification for performance issues."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "My lab is running very slow", 
            Role.USER
        )
        assert tier == "TIER_1"
        assert severity == TicketPriority.LOW
    
    def test_tier_2_docker_issue(self):
        """Test Tier 2 classification for Docker issues."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "Docker container won't start", 
            Role.USER
        )
        assert tier == "TIER_2"
        assert severity == TicketPriority.MEDIUM
    
    def test_tier_2_vm_crash(self):
        """Test Tier 2 classification for VM crashes."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "VM crashed and I lost my work", 
            Role.USER
        )
        assert tier == "TIER_2"
        assert severity == TicketPriority.HIGH  # Has high priority phrase "lost my work"
    
    def test_tier_3_kernel_panic(self):
        """Test Tier 3 classification for kernel panic (critical)."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "Kernel panic in my lab VM", 
            Role.USER
        )
        assert tier == "TIER_3"
        assert severity == TicketPriority.CRITICAL
    
    def test_tier_3_security_breach(self):
        """Test Tier 3 classification for security issues (critical)."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "I think there's a security breach", 
            Role.USER
        )
        assert tier == "TIER_3"
        assert severity == TicketPriority.CRITICAL
    
    def test_tier_3_data_loss(self):
        """Test Tier 3 classification for data loss."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "Data loss in the environment", 
            Role.USER
        )
        assert tier == "TIER_3"
        assert severity == TicketPriority.CRITICAL
    
    def test_deterministic_classification(self):
        """Test that same input always produces same output (determinism)."""
        message = "I need to reset my password"
        role = Role.USER
        
        # Run classification 5 times
        results = [
            TierClassifier.classify_tier_and_severity(message, role)
            for _ in range(5)
        ]
        
        # All results should be identical
        assert all(r == results[0] for r in results)
        assert results[0] == ("TIER_0", TicketPriority.LOW)
    
    def test_admin_role_escalation(self):
        """Test that admin role escalates infrastructure issues."""
        tier, severity = TierClassifier.classify_tier_and_severity(
            "Database server is down", 
            Role.ADMIN
        )
        # "down" keyword triggers Tier 3 with HIGH severity
        assert tier == "TIER_3"
        assert severity == TicketPriority.HIGH
    
    def test_case_insensitivity(self):
        """Test that classification is case-insensitive."""
        tier1, sev1 = TierClassifier.classify_tier_and_severity(
            "KERNEL PANIC", 
            Role.USER
        )
        tier2, sev2 = TierClassifier.classify_tier_and_severity(
            "kernel panic", 
            Role.USER
        )
        tier3, sev3 = TierClassifier.classify_tier_and_severity(
            "KerNeL PaNiC", 
            Role.USER
        )
        
        assert tier1 == tier2 == tier3 == "TIER_3"
        assert sev1 == sev2 == sev3 == TicketPriority.CRITICAL
