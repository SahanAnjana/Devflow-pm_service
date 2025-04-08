# hr-service/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database engine with settings for remote database
engine = create_engine(
    settings.PMYSQL_URL,
    pool_pre_ping=True,     # Verify connection before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_size=10,           # Maximum number of connections in the pool
    max_overflow=20,        # Allow 20 connections beyond pool_size
    connect_args={
        "connect_timeout": 30  # Connection timeout in seconds
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()