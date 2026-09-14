"""
MindGuard AI - Prediction helper
===================================
Loads the trained pipeline once and exposes a predict_risk() function.
Used by the backend's ml_service.py - not meant to be run directly,
though you can test it standalone with: python ml/predict.py
"""

import os

import joblib
import pandas as pd

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "feature_columns.pkl")

_pipeline = None
_feature_columns = None


def _load_artifacts():
    global _pipeline, _feature_columns
    if _pipeline is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run 'python ml/train_model.py' first."
            )
        _pipeline = joblib.load(MODEL_PATH)
        _feature_columns = joblib.load(FEATURES_PATH)
    return _pipeline, _feature_columns


def predict_risk(answer: dict) -> dict:
    """
    answer: dict with keys matching AssessmentAnswer fields, e.g.
        {
            "age": 20,
            "gender": "Male",
            "academic_level": "Undergraduate",
            "avg_daily_usage_hours": 5.5,
            "most_used_platform": "Instagram",
            "affects_academic_performance": "Yes",
            "sleep_hours_per_night": 6,
            "mental_health_score": 6,
            "relationship_status": "Single",
            "conflicts_over_social_media": 2,
        }

    Returns:
        {
            "risk_level": "High",
            "probabilities": {"Low": 0.05, "Medium": 0.15, "High": 0.80},
            "confidence": 0.80,
        }
    """
    pipeline, feature_columns = _load_artifacts()

    row = pd.DataFrame([{col: answer[col] for col in feature_columns}])
    prediction = pipeline.predict(row)[0]

    result = {"risk_level": prediction}

    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(row)[0]
        classes = pipeline.classes_
        prob_map = {cls: float(p) for cls, p in zip(classes, proba)}
        result["probabilities"] = prob_map
        result["confidence"] = float(max(proba))
    else:
        result["probabilities"] = {}
        result["confidence"] = None

    return result


if __name__ == "__main__":
    # Quick manual test
    sample = {
        "age": 20,
        "gender": "Male",
        "academic_level": "Undergraduate",
        "avg_daily_usage_hours": 5.5,
        "most_used_platform": "Instagram",
        "affects_academic_performance": "Yes",
        "sleep_hours_per_night": 6,
        "mental_health_score": 6,
        "relationship_status": "Single",
        "conflicts_over_social_media": 2,
    }
    print(predict_risk(sample))