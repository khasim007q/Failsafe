import os
import joblib
import pandas as pd
from celery import Celery
from .services.static_analyzer import StaticAnalyzer
from .services.decision_engine import DecisionEngine

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

# LOAD THE BRAIN (Global Variable so we load it once)
MODEL_PATH = "app/ml/risk_model.pkl"
risk_model = None

if os.path.exists(MODEL_PATH):
    risk_model = joblib.load(MODEL_PATH)
    print("AI Model loaded successfully.")
else:
    print("Warning: AI Model not found. Using dummy scores.")

@celery.task
def run_analysis_task(pr_id: int, repo_url: str):
    print(f"Starting analysis for PR #{pr_id}...")
    
    # 1. MOCK INPUT DATA (In real life, we extract this from GitHub API)
    # Let's pretend this PR deletes a lot of code on a Friday (Risky!)
    features = pd.DataFrame([{
        "num_files": 12,
        "has_migration": 1,
        "lines_deleted": 80,
        "is_friday": 1
    }])
    
    # 2. RUN ML PREDICTION
    ml_score = 0.0
    if risk_model:
        # Predict probability of failure (Class 1)
        # result is [[prob_success, prob_failure]]
        ml_score = risk_model.predict_proba(features)[0][1]
    
    # 3. RUN STATIC ANALYSIS
    analyzer = StaticAnalyzer()
    # Mocking diff data for the static analyzer
    mock_diff = [
        {"path": "migrations/bad_migration.py", "status": "added", "patch": "def up(): pass"},
        {"path": "config.py", "status": "modified", "patch": "AWS_KEY=123"}
    ]
    static_result = analyzer.analyze(mock_diff)
    
    print(f"Analysis Complete. ML Risk: {ml_score:.2f}, Violations: {len(static_result['violations'])}")

    # 4. MAKE THE DECISION
    judge = DecisionEngine()
    verdict = judge.decide(ml_score, static_result)
    
    print(f"Final Decision: {verdict['decision'].upper()}")
    print(f"Reason: {verdict['reasons'][0]}")
    
    return {
        "status": "success", 
        "ml_risk_score": float(ml_score),
        "static_violations": static_result["violations"],
        "final_decision": verdict["decision"],
        "decision_reason": verdict["reasons"]
    }