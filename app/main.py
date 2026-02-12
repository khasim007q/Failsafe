import time
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database, tasks

# Wait for DB to be ready (Simple retry logic)
max_retries = 5
for i in range(max_retries):
    try:
        models.Base.metadata.create_all(bind=database.engine)
        print("Database connected and tables created.")
        break
    except Exception as e:
        print(f"Waiting for DB... ({i+1}/{max_retries})")
        time.sleep(2)

app = FastAPI(title="FailSafe Engine")

@app.get("/")
def read_root():
    return {"status": "active", "component": "api"}

@app.post("/analyze")
def trigger_analysis(pr_id: int, repo: str, db: Session = Depends(database.get_db)):
    """
    Endpoints that offloads work to Celery.
    """
    # 1. Store initial record in DB
    new_pr = models.PullRequest(
        repo_name=repo,
        pr_number=pr_id
    )
    db.add(new_pr)
    db.commit()
    db.refresh(new_pr)
    
    # 2. Send to Redis/Celery (Async)
    task = tasks.run_analysis_task.delay(pr_id, repo)
    
    return {
        "message": "Analysis queued", 
        "task_id": task.id, 
        "pr_db_id": new_pr.id
    }