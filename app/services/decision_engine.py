from enum import Enum
from typing import List, Dict

class Decision(Enum):
    APPROVE = "approve"
    MANUAL_REVIEW = "manual_review"
    BLOCK = "block"

class DecisionEngine:
    def __init__(self):
        # Thresholds (Configurable in real life)
        self.ml_high_risk_threshold = 0.8  # 80% chance of failure
        self.ml_medium_risk_threshold = 0.5 # 50% chance of failure
        self.static_violation_limit = 0     # Zero tolerance for secrets

    def decide(self, ml_score: float, static_results: Dict) -> Dict:
        """
        Combines ML and Static Analysis to make a final call.
        """
        reasons = []
        decision = Decision.APPROVE
        
        # 1. CHECK STATIC VIOLATIONS (Hard Rules)
        violation_count = len(static_results.get("violations", []))
        if violation_count > self.static_violation_limit:
            decision = Decision.BLOCK
            reasons.append(f"Found {violation_count} critical code violations.")
            
        # 2. CHECK ML RISK (Probabilistic)
        elif ml_score > self.ml_high_risk_threshold:
            decision = Decision.BLOCK
            reasons.append(f"ML Model predicts high failure risk ({ml_score:.2f}).")
            
        elif ml_score > self.ml_medium_risk_threshold:
            decision = Decision.MANUAL_REVIEW
            reasons.append(f"Moderate risk detected ({ml_score:.2f}). Human review required.")
            
        # 3. DEFAULT
        else:
            reasons.append("Risk levels are within acceptable limits.")

        return {
            "decision": decision.value,
            "reasons": reasons
        }