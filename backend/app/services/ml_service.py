"""
MindGuard AI - ML Service
=========================
Loads the trained model pipeline once at import time and exposes
predict_risk() for the API to call.

The model is never retrained during an API request.
"""

import os

import joblib
import pandas as pd


# ---------------------------------------------------------
# Locate ML artifacts
# ---------------------------------------------------------
# Current structure:
#
# mindguard-ai/
# ├── backend/
# │   └── app/
# │       └── services/
# │           └── ml_service.py
# │
# └── ml/
#     └── artifacts/
#         ├── mindguard_model.joblib
#         └── feature_info.joblib
#
# From services/:
# services -> app -> backend -> mindguard-ai
# Therefore we go up THREE levels.
# ---------------------------------------------------------

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

_PROJECT_ROOT = os.path.abspath(
    os.path.join(_THIS_DIR, "..", "..", "..")
)

ARTIFACTS_DIR = os.path.join(
    _PROJECT_ROOT,
    "ml",
    "artifacts"
)

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "feature_columns.pkl")


# ---------------------------------------------------------
# Model variables
# ---------------------------------------------------------

_pipeline = None
_feature_columns = None
_load_error = None


# ---------------------------------------------------------
# Load model ONCE when backend starts
# ---------------------------------------------------------

try:
    _pipeline = joblib.load(MODEL_PATH)
    _feature_columns = joblib.load(FEATURES_PATH)

except Exception as e:
    _load_error = str(e)


# ---------------------------------------------------------
# Check whether model loaded successfully
# ---------------------------------------------------------

def is_model_loaded() -> bool:
    return _pipeline is not None


# ---------------------------------------------------------
# Predict risk
# ---------------------------------------------------------

def predict_risk(answer: dict) -> dict:
    """
    Predict the user's digital well-being risk level.

    Returns:
        {
            "risk_level": "High",
            "probabilities": {
                "Low": 0.05,
                "Medium": 0.15,
                "High": 0.80
            },
            "confidence": 0.80
        }

    Raises:
        RuntimeError if the trained model could not be loaded.
    """

    if _pipeline is None:
        raise RuntimeError(
            f"ML model is not loaded: {_load_error}"
        )

    # Create one-row DataFrame using the exact feature order
    row = pd.DataFrame([
        {
            col: answer[col]
            for col in _feature_columns
        }
    ])

    # Predict risk level
    prediction = _pipeline.predict(row)[0]

    result = {
        "risk_level": str(prediction)
    }

    # Get prediction probabilities
    if hasattr(_pipeline, "predict_proba"):

        proba = _pipeline.predict_proba(row)[0]

        classes = _pipeline.classes_

        prob_map = {
            str(cls): round(float(probability), 4)
            for cls, probability in zip(classes, proba)
        }

        result["probabilities"] = prob_map

        result["confidence"] = round(
            float(max(proba)),
            4
        )

    else:
        result["probabilities"] = {}
        result["confidence"] = None

    return result