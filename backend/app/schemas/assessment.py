from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssessmentAnswerIn(BaseModel):
    age: int = Field(ge=10, le=100)
    gender: str
    academic_level: str
    avg_daily_usage_hours: float = Field(ge=0, le=24)
    most_used_platform: str
    affects_academic_performance: str  # "Yes" or "No"
    sleep_hours_per_night: float = Field(ge=0, le=24)
    mental_health_score: int = Field(ge=0, le=10)
    relationship_status: str
    conflicts_over_social_media: int = Field(ge=0, le=50)



class AssessmentAnswerOut(AssessmentAnswerIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    category: str
    text: str


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    risk_level: str
    confidence: float | None
    probabilities: dict
    recommendations: list[RecommendationOut] = []


class AssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    submitted_at: datetime
    status: str
    answer: AssessmentAnswerOut | None = None


class AssessmentWithPredictionOut(AssessmentOut):
    prediction: PredictionOut | None = None
