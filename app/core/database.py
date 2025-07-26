"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Create base class for models
Base = declarative_base()

# Global variables for lazy initialization
_engine = None
_SessionLocal = None


def get_engine():
    """Get database engine, creating it if it doesn't exist."""
    global _engine
    if _engine is None:
        from app.core.config import get_settings

        settings = get_settings()

        _engine = create_engine(
            settings.database_url,
            echo=settings.database_echo,
            connect_args={"check_same_thread": False}
            if "sqlite" in settings.database_url
            else {},
        )
    return _engine


def get_session_local():
    """Get SessionLocal, creating it if it doesn't exist."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    engine = get_engine()

    # Import all models here to ensure they're registered
    from app.models import user, agent

    Base.metadata.create_all(bind=engine)
