"""
MindGuard AI - Database Connection
=====================================
Sets up the SQLAlchemy engine and session factory. Every request gets
its own database session via the get_db() dependency, which is closed
automatically when the request finishes - this prevents connection
leaks under load.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# pool_pre_ping=True checks the connection is alive before using it,
# which prevents "MySQL server has gone away" errors after the
# connection sits idle for a while (a common MySQL gotcha).
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and guarantees it's closed afterward, even if an error occurs.

    Usage in a route:
        @router.get("/something")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()