# FailSafe: Autonomous AI Deployment Risk Engine
FailSafe is a distributed fault-tolerance system designed to analyze, score, and gatekeep software deployments. Unlike standard CI/CD linters that only check syntax, FailSafe utilizes a hybrid AI approach—combining deterministic static analysis, probabilistic machine learning, and generative LLM reasoning—to predict deployment risks and prevent production failures before they occur.

This project demonstrates the implementation of a production-grade distributed system using asynchronous task queues, durable persistence, and local Large Language Model (LLM) integration.

## System Architecture
FailSafe operates as a decoupled, event-driven microservices architecture containerized via Docker.

**High-Level Data Flow:**
1.  **Ingestion:** The **FastAPI** service receives a deployment event (simulating a GitHub Webhook).
2.  **Queuing:** The request is serialized and pushed to a **Redis** message broker for asynchronous processing.
3.  **Execution:** A **Celery** worker consumes the task and runs a parallel analysis pipeline:
    * **Static Analysis Engine:** Scans code diffs for security violations (e.g., hardcoded secrets) and operational risks.
    * **ML Risk Engine:** A Logistic Regression model predicts failure probability based on historical metadata.
    * **LLM Reasoner:** A raw HTTP client connects to a local **Ollama (Llama3)** instance to generate human-readable explanations.
4.  **Decision:** The **Decision Engine** aggregates all signals to render a final verdict.
5.  **Persistence:** All events, scores, and decisions are stored in **PostgreSQL** for audit trails.

## Project Structure
The project follows a modular service-oriented structure designed for scalability.

```text
failsafe/
├── app/
│   ├── main.py                  # API Entrypoint (FastAPI)
│   ├── tasks.py                 # Celery Worker Definition & Orchestration
│   ├── models.py                # SQLAlchemy Database Models
│   ├── database.py              # DB Connection & Session Management
│   ├── services/
│   │   ├── static_analyzer.py   # Rule-based AST/Regex engine
│   │   ├── decision_engine.py   # Logic for aggregating risk scores
│   │   └── llm_reasoner.py      # HTTP Client for Local LLM (Ollama)
│   └── ml/
│       ├── train_model.py       # Script to generate synthetic data & train model
│       └── risk_model.pkl       # Serialized ML Model (Generated artifact)
├── docker-compose.yml           # Orchestration for API, Worker, Redis, DB
├── Dockerfile                   # Container definition
└── requirements.txt             # Python dependencies
```

## The Hybrid AI Approach

FailSafe moves beyond simple linting by layering three distinct types of intelligence. This multi-modal strategy ensures robust error detection where single methods typically fail.

1. **Deterministic Static Analysis (The "Law")**
   * **Role**: Enforces hard rules and security policies.
   * **Why**: Certain errors (e.g., hardcoded AWS keys, missing migration rollbacks) are non-negotiable and easy to detect via pattern matching.
   * **Tradeoff**: It has zero tolerance for context. It cannot detect "risky but valid" code (e.g., a massive refactor on a Friday).

2. **Probabilistic Machine Learning (The "Intuition")**
    * **Role**: Predicts risk based on metadata and historical patterns.
    * **Why**: Static analysis misses context. The ML engine learns that Deploying 50 files + Database Migration + Friday Afternoon = 98% Failure Rate.
    * **Tradeoff**: It is probabilistic, not guaranteed. It requires high-quality historical data to train effectively and can suffer from bias if the training data is skewed.

3. **Generative LLM Reasoning (The "Voice")**
   * **Role**: Explains the "Why" behind the decision.
   * **Why**: A risk score of "0.98" provides no actionable feedback to a developer. The LLM synthesizes the static violations and ML context into a human-readable explanation, acting as an automated Senior Engineer.
   * **Tradeoff**: LLMs are computationally expensive and non-deterministic (they can hallucinate). FailSafe mitigates this by using the LLM only for explanation, never for the blocking decision itself.

## Technology Stack
**Orchestration**: Docker & Docker Compose

**API Framework**: FastAPI (Python)

**Asynchronous Workers**: Celery

**Message Broker**: Redis

**Database**: PostgreSQL

**Machine Learning**: Scikit-Learn, Pandas, NumPy, Joblib

**Generative AI**: Ollama (Llama3) via *raw HTTP requests* (No external API wrappers used)

## Prerequisites
Docker Desktop (Linux/Windows/Mac)

Ollama installed on the host machine

Git

## Installation & Setup
1. **Clone the Repository**

```Bash
git clone https://github.com/yourusername/failsafe.git
cd failsafe
```

2. **Prepare the Local LLM**
Ensure Ollama is running on your host machine and pull the required model:

```Bash
ollama pull llama3
```

3. **Build and Run Services**

```Bash
docker-compose up --build -d
```

4. **Train the ML Model**
* Initialize the synthetic dataset and train the risk prediction model inside the worker container:

```Bash
docker-compose exec worker python app/ml/train_model.py
```

**Usage**
* To simulate a deployment event (Pull Request), send a POST request to the API.

* Example: Triggering a Risky Analysis

```Bash
curl -X POST "http://localhost:8000/analyze?repo=failsafe-test&pr_id=107"
```

* Check Worker Logs for Analysis:

```Bash
docker-compose logs -f worker
```

* Sample Output:

```Plaintext
[INFO] Task received
[WARNING] Starting analysis for PR #107...
[INFO] Static Analysis: Found 1 violation (Missing Rollback).
[INFO] ML Risk Score: 0.98 (High Risk).
[INFO]  Sending request to Ollama...
[INFO]  LLM Explanation: This deployment carries a high risk of failure due to a database migration on a Friday without a fallback strategy.
[INFO] Final Decision: BLOCK
```

## Future Roadmap

The project is evolving from a deployment gatekeeper to a full lifecycle reliability platform.

* **Phase 1 (Current)**: Pre-deployment analysis and gating (Completed).

* **Phase 2**: Human-in-the-Loop Dashboard. Integrating a UI to allow senior engineers to review "Marginal" risk decisions manually.

* **Phase 3**: Continuous Monitoring. Connecting to Prometheus to monitor error rates immediately after a deployment is approved.

* **Phase 4**: Automated Mitigation. Implementing webhooks to trigger automatic rollbacks if post-deployment metrics degrade.

* **Phase 5**: GitHub App Integration. Replacing the mock data ingestion with real-time GitHub Webhook event listeners.
