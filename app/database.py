import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Connection String
# Matches the service name "db" in docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://failsafe:failsafe_pass@db/failsafe_db")

# 2. The Engine
engine = create_engine(DATABASE_URL)

# 3. The Session Maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The Base Class (THIS WAS MISSING)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()