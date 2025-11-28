import requests
import json
import sys

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1/chat/"

# Test Cases
# Format: (Message, Role, Expected Tier, Expected Severity)
TEST_CASES = [
    (
        "I forgot my password and cannot login.",
        "user",
        "TIER_1",
        "low"
    ),
    (
        "My VPN connection is very slow and timing out.",
        "user",
        "TIER_2",
        "medium"
    ),
    (
        "The container failed to start with error: missing /opt/startup.sh",
        "user",
        "TIER_3",
        "high"
    ),
    (
        "We are experiencing a kernel panic on the production VM.",
        "user",
        "TIER_3",
        "critical"
    ),
    (
        "I think there is a security breach in the system.",
        "user",
        "TIER_3",
        "critical"
    ),
    (
        "The database server is responding slowly.",
        "admin",
        "TIER_2",
        "high" 
    )
]

def run_tests():
    print(f"Running Tier Routing Verification against {API_URL}...\n")
    passed = 0
    failed = 0

    for message, role, expected_tier, expected_severity in TEST_CASES:
        payload = {
            "session_id": "test-tier-verification",
            "message": message,
            "role": role
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            actual_tier = data.get("tier")
            actual_severity = data.get("severity")
            
            # Normalize for comparison
            if actual_severity:
                actual_severity = actual_severity.lower()
            
            print(f"Test Case: '{message}' (Role: {role})")
            print(f"  Expected: {expected_tier} / {expected_severity}")
            print(f"  Actual:   {actual_tier} / {actual_severity}")
            
            if actual_tier == expected_tier and actual_severity == expected_severity:
                print("  Result:   PASS")
                passed += 1
            else:
                print("  Result:   FAIL")
                failed += 1
            print("-" * 50)
            
        except Exception as e:
            print(f"Error running test case: {e}")
            failed += 1

    print(f"\nSummary: {passed} Passed, {failed} Failed")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
