"""
MindGuard AI - Database Models
==================================
Covers the core end-to-end flow: register -> assessment -> prediction ->
recommendations -> goals -> progress tracking.

NOT included yet (deferred to keep today's build focused on a working
end-to-end demo, added later): achievements, user_achievements,
notifications, feedback. These don't block the core product loop.

All tables use MySQL via SQLAlchemy. Column choices deliberately mirror
the ML feature names 1:1 in AssessmentAnswer, so a row can be fed
directly into the ML pipeline without renaming anything.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), default="user", nullable=False)  # "user" or "admin"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    daily_usage = relationship("DailyUsage", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    academic_level = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)  # metadata only, never fed to ML
    relationship_status = Column(String(50), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)  # "en" or "ta"
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="profile")


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    consent_type = Column(String(50), nullable=False)  # e.g. "data_processing", "analytics"
    granted = Column(Boolean, default=False, nullable=False)
    granted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="consents")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    submitted_at = Column(DateTime, default=utc_now, nullable=False)
    status = Column(String(20), default="completed", nullable=False)

    user = relationship("User", back_populates="assessments")
    answer = relationship("AssessmentAnswer", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    prediction = relationship("Prediction", back_populates="assessment", uselist=False, cascade="all, delete-orphan")


class AssessmentAnswer(Base):
    """
    Column names deliberately match the ML pipeline's ALL_FEATURES list
    exactly, so a row here can be converted straight into a DataFrame
    for the model without any renaming step.
    """
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), unique=True, nullable=False)

    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    academic_level = Column(String(50), nullable=False)
    avg_daily_usage_hours = Column(Float, nullable=False)
    most_used_platform = Column(String(50), nullable=False)
    affects_academic_performance = Column(String(10), nullable=False)  # "Yes" / "No"
    sleep_hours_per_night = Column(Float, nullable=False)
    mental_health_score = Column(Integer, nullable=False)
    relationship_status = Column(String(50), nullable=False)
    conflicts_over_social_media = Column(Integer, nullable=False)

    assessment = relationship("Assessment", back_populates="answer")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), unique=True, nullable=False)
    model_version = Column(String(50), nullable=False)  # e.g. "GradientBoosting_v1"
    risk_level = Column(String(10), nullable=False)  # "Low" / "Medium" / "High" - NEVER "diagnosis"
    prob_low = Column(Float, nullable=False)
    prob_medium = Column(Float, nullable=False)
    prob_high = Column(Float, nullable=False)
    top_factors = Column(JSON, nullable=True)  # list of {factor, direction, raw_feature}
    created_at = Column(DateTime, default=utc_now, nullable=False)

    assessment = relationship("Assessment", back_populates="prediction")
    recommendations = relationship("Recommendation", back_populates="prediction", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # e.g. "usage", "sleep", "academic"
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    prediction = relationship("Prediction", back_populates="recommendations")


class DailyUsage(Base):
    __tablename__ = "daily_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    usage_hours = Column(Float, nullable=False)
    platform = Column(String(50), nullable=True)

    user = relationship("User", back_populates="daily_usage")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    goal_type = Column(String(50), nullable=False)  # e.g. "reduce_daily_usage", "digital_curfew"
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active/completed/abandoned
    start_date = Column(DateTime, default=utc_now, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="goals")
    progress_entries = relationship("Progress", back_populates="goal", cascade="all, delete-orphan")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, index=True)
    date = Column(DateTime, default=utc_now, nullable=False)
    value = Column(Float, nullable=False)
    note = Column(Text, nullable=True)

    goal = relationship("Goal", back_populates="progress_entries")