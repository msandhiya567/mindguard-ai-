"""
MindGuard AI - Create Database Tables
=========================================
Run this ONCE to create all tables in MySQL based on models.py.

    python create_tables.py

Safe to run again later - it won't touch or delete tables that already
exist, it only creates missing ones.

NOTE: for a real production app you'd use Alembic migrations instead of
this (so schema changes are tracked and reversible). This script is a
fast path to get a working database today; Alembic gets added later.
"""

from app.core.database import Base, engine
from app.models.models import (  # noqa: F401 - imported so Base knows about them
    User, Profile, Consent, Assessment, AssessmentAnswer,
    Prediction, Recommendation, DailyUsage, Goal, Progress,
)

print("Creating tables in the database...")
Base.metadata.create_all(bind=engine)
print("Done. Tables created (or already existed):")
for table_name in Base.metadata.tables:
    print(f"  - {table_name}")