from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models import Base
# create_engine sets up the connection pool to PostgreSQL
engine = create_engine(settings.DATABASE_URL,pool_pre_ping=True)

# Creates query_history table if it doesn't exist yet
# Safe to run every startup — won't drop existing data
Base.metadata.create_all(bind=engine)

# SessionLocal is a factory — call it to get a DB session
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """
    FastAPI dependency — yields a DB session per request,
    closes it automatically when the request finishes.
    Use this in route functions via: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
