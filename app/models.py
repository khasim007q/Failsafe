from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class AnalysisStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class DecisionType(enum.Enum):
    APPROVE = "approve"
    CANARY = "canary"
    BLOCK = "block"
    MANUAL_REVIEW = "manual_review"

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_owner = Column(String, index=True)
    repo_name = Column(String, index=True)
    pr_number = Column(Integer, index=True)
    title = Column(String)
    author = Column(String)
    
    # Store raw webhook data just in case we need to debug later
    raw_payload = Column(JSON) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship: One PR can have multiple analyses (if they push new commits)
    analyses = relationship("AnalysisRun", back_populates="pr")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"))
    commit_sha = Column(String)
    
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # --- The 3 Pillars of FailSafe ---
    
    # 1. Static Analysis (JSON allows flexibility for different rule types)
    static_score = Column(Float) # 0-100 severity
    static_details = Column(JSON) # e.g. {"violations": ["no_rollback", "bad_env"]}
    
    # 2. ML Risk Model
    ml_score = Column(Float) # 0.0 to 1.0 probability of failure
    ml_version = Column(String) # Track which model version was used
    
    # 3. LLM Reasoning
    llm_explanation = Column(String)
    llm_confidence = Column(Float)
    
    # --- The Final Verdict ---
    final_decision = Column(Enum(DecisionType))
    reasoning_summary = Column(String)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    pr = relationship("PullRequest", back_populates="analyses")