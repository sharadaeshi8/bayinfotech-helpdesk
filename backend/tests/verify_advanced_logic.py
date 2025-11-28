import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

def calculate_confidence(retrieval, coverage, recency, llm=0.8):
    return (retrieval * 0.4) + (coverage * 0.3) + (llm * 0.2) + (recency * 0.1)

def test_confidence_calculation():
    print("Testing Confidence Calculation...")
    
    # Case 1: Perfect match
    score = calculate_confidence(1.0, 1.0, 1.0)
    print(f"Perfect match (1.0, 1.0, 1.0): {score:.4f} (Expected ~0.98)")
    
    # Case 2: Poor match
    score = calculate_confidence(0.2, 0.1, 0.5)
    print(f"Poor match (0.2, 0.1, 0.5): {score:.4f} (Expected ~0.32)")
    
    # Case 3: Average match
    score = calculate_confidence(0.7, 0.5, 0.8)
    print(f"Average match (0.7, 0.5, 0.8): {score:.4f} (Expected ~0.67)")

def test_recency_decay():
    print("\nTesting Recency Decay...")
    now = datetime.now()
    
    # 0 days old
    days_diff = 0
    score = 1.0 / (1.0 + days_diff/365.0)
    print(f"0 days old: {score:.4f}")
    
    # 1 year old
    days_diff = 365
    score = 1.0 / (1.0 + days_diff/365.0)
    print(f"1 year old: {score:.4f} (Expected 0.5)")
    
    # 2 years old
    days_diff = 730
    score = 1.0 / (1.0 + days_diff/365.0)
    print(f"2 years old: {score:.4f} (Expected 0.33)")

if __name__ == "__main__":
    test_confidence_calculation()
    test_recency_decay()
