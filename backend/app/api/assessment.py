from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.models import (
    Assessment,
    AssessmentAnswer,
    Prediction,
    Recommendation,
    User,
)
from app.schemas.assessment import (
    AssessmentAnswerIn,
    AssessmentOut,
    AssessmentWithPredictionOut,
)
from app.services.ml_service import predict_risk
from app.services.recommendation_service import generate_recommendations

router = APIRouter()


def build_prediction_response(prediction):
    """
    Convert the database Prediction model into the format
    expected by PredictionOut.
    """
    probabilities = {
        "Low": prediction.prob_low,
        "Medium": prediction.prob_medium,
        "High": prediction.prob_high,
    }

    confidence = max(probabilities.values())

    return {
        "risk_level": prediction.risk_level,
        "confidence": confidence,
        "probabilities": probabilities,
        "recommendations": prediction.recommendations,
    }


def build_assessment_response(assessment):
    """
    Convert an Assessment SQLAlchemy object into the
    response format expected by FastAPI.
    """
    response = {
        "id": assessment.id,
        "user_id": assessment.user_id,
        "submitted_at": assessment.submitted_at,
        "status": assessment.status,
        "answer": assessment.answer,
        "prediction": None,
    }

    if assessment.prediction:
        response["prediction"] = build_prediction_response(
            assessment.prediction
        )

    return response


@router.post(
    "/assessments",
    response_model=AssessmentOut,
    status_code=status.HTTP_201_CREATED,
    tags=["assessments"],
)
def submit_assessment(
    payload: AssessmentAnswerIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_assessment = Assessment(
        user_id=current_user.id,
        status="completed",
    )

    db.add(new_assessment)
    db.flush()

    new_answer = AssessmentAnswer(
        assessment_id=new_assessment.id,
        age=payload.age,
        gender=payload.gender,
        academic_level=payload.academic_level,
        avg_daily_usage_hours=payload.avg_daily_usage_hours,
        most_used_platform=payload.most_used_platform,
        affects_academic_performance=payload.affects_academic_performance,
        sleep_hours_per_night=payload.sleep_hours_per_night,
        mental_health_score=payload.mental_health_score,
        relationship_status=payload.relationship_status,
        conflicts_over_social_media=payload.conflicts_over_social_media,
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_assessment)

    return new_assessment


@router.post(
    "/assessments/{assessment_id}/predict",
    response_model=AssessmentWithPredictionOut,
    tags=["assessments"],
)
def predict_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    if (
        assessment.user_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this assessment.",
        )

    if not assessment.answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This assessment has no answers yet.",
        )

    # If prediction already exists, return it.
    if assessment.prediction:
        return build_assessment_response(assessment)

    answer_dict = {
        "age": assessment.answer.age,
        "gender": assessment.answer.gender,
        "academic_level": assessment.answer.academic_level,
        "avg_daily_usage_hours": assessment.answer.avg_daily_usage_hours,
        "most_used_platform": assessment.answer.most_used_platform,
        "affects_academic_performance": assessment.answer.affects_academic_performance,
        "sleep_hours_per_night": assessment.answer.sleep_hours_per_night,
        "mental_health_score": assessment.answer.mental_health_score,
        "relationship_status": assessment.answer.relationship_status,
        "conflicts_over_social_media": assessment.answer.conflicts_over_social_media,
    }

    try:
        ml_result = predict_risk(answer_dict)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )

    probs = ml_result["probabilities"]

    new_prediction = Prediction(
        assessment_id=assessment.id,
        model_version="GradientBoosting_v1",
        risk_level=ml_result["risk_level"],
        prob_low=probs.get("Low", 0.0),
        prob_medium=probs.get("Medium", 0.0),
        prob_high=probs.get("High", 0.0),
        top_factors=None,
    )

    db.add(new_prediction)
    db.flush()

    rec_dicts = generate_recommendations(
        answer_dict,
        ml_result["risk_level"],
    )

    for rec in rec_dicts:
        db.add(
            Recommendation(
                prediction_id=new_prediction.id,
                category=rec["category"],
                text=rec["text"],
            )
        )

    db.commit()
    db.refresh(assessment)

    return build_assessment_response(assessment)


@router.get(
    "/assessments/{assessment_id}",
    response_model=AssessmentWithPredictionOut,
    tags=["assessments"],
)
def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    if (
        assessment.user_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this assessment.",
        )

    return build_assessment_response(assessment)


@router.get(
    "/assessments",
    response_model=list[AssessmentWithPredictionOut],
    tags=["assessments"],
)
def list_my_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessments = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.submitted_at.desc())
        .all()
    )

    return [
        build_assessment_response(assessment)
        for assessment in assessments
    ]

