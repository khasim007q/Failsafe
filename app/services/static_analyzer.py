from typing import List, Dict, Any

class RiskRule:
    """Base class for all risk detection rules."""
    def check(self, files: List[Dict]) -> List[str]:
        return []

# --- Rule 1: Dangerous Migrations ---
class NoRollbackMigrationRule(RiskRule):
    def check(self, files: List[Dict]) -> List[str]:
        violations = []
        for file in files:
            if "migrations/" in file["path"] and file["status"] == "added":
                # Rough check: does the file content contain a "down" method?
                # In a real app, we'd parse the AST, but string search works for MVP.
                content = file.get("patch", "").lower()
                if "def downgrade" not in content and "def down" not in content:
                    violations.append(f"Migration file '{file['path']}' missing rollback logic.")
        return violations

# --- Rule 2: Hardcoded Secrets ---
class HardcodedSecretRule(RiskRule):
    def check(self, files: List[Dict]) -> List[str]:
        violations = []
        dangerous_patterns = ["AWS_ACCESS_KEY", "sk_live_", "private_key"]
        
        for file in files:
            patch = file.get("patch", "")
            for pattern in dangerous_patterns:
                if pattern in patch:
                    violations.append(f"Potential hardcoded secret detected: {pattern}")
        return violations

# --- The Main Engine ---
class StaticAnalyzer:
    def __init__(self):
        self.rules = [
            NoRollbackMigrationRule(),
            HardcodedSecretRule()
        ]

    def analyze(self, diff_data: List[Dict]) -> Dict[str, Any]:
        """
        Input: List of file objects from GitHub API
        Output: Risk Score + List of Violations
        """
        all_violations = []
        
        for rule in self.rules:
            violations = rule.check(diff_data)
            all_violations.extend(violations)
            
        # simple scoring logic: 10 points per violation
        risk_score = min(len(all_violations) * 10, 100)
        
        return {
            "static_score": risk_score,
            "violations": all_violations
        }