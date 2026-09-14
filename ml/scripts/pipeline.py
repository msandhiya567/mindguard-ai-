"""
MindGuard AI - Shared ML Pipeline Module
==========================================
This module is the SINGLE SOURCE OF TRUTH for how raw data becomes model-ready
features. It is imported by both the training script (train_and_compare.py)
and, later, the FastAPI backend's inference service.

Why this matters: if training and inference preprocess data differently
(train/serve skew), the model silently breaks in production. Keeping the
logic in one shared module prevents that class of bug entirely.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# ---------------------------------------------------------------------------
# Column definitions (single source of truth for feature names)
# ---------------------------------------------------------------------------

NUMERIC_FEATURES = [
    "Age",
    "Avg_Daily_Usage_Hours",
    "Sleep_Hours_Per_Night",
    "Mental_Health_Score",
    "Conflicts_Over_Social_Media",
]

CATEGORICAL_FEATURES = [
    "Gender",
    "Academic_Level",
    "Most_Used_Platform",
    "Affects_Academic_Performance",
    "Relationship_Status",
]

EXCLUDED_COLUMNS = ["Student_ID", "Country", "Addicted_Score"]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

TARGET_COLUMN = "Risk_Level"
RISK_ORDER = ["Low", "Medium", "High"]

RISK_BINS = {
    "Low": (2, 4),
    "Medium": (5, 6),
    "High": (7, 9),
}


def validate_schema(df: pd.DataFrame) -> None:
    expected_columns = {
        "Student_ID", "Age", "Gender", "Academic_Level", "Country",
        "Avg_Daily_Usage_Hours", "Most_Used_Platform",
        "Affects_Academic_Performance", "Sleep_Hours_Per_Night",
        "Mental_Health_Score", "Relationship_Status",
        "Conflicts_Over_Social_Media", "Addicted_Score",
    }
    missing = expected_columns - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {missing}")

    if df.isnull().any().any():
        null_cols = df.columns[df.isnull().any()].tolist()
        raise ValueError(
            f"Dataset contains null values in columns: {null_cols}. "
            "This pipeline assumes clean data (validated at ingestion)."
        )

    if not df["Addicted_Score"].between(1, 10).all():
        raise ValueError("Addicted_Score contains values outside the expected 1-10 range.")

    if df["Student_ID"].duplicated().any():
        raise ValueError("Duplicate Student_ID values found - expected one row per student.")


def construct_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def bin_score(score: int) -> str:
        for label, (low, high) in RISK_BINS.items():
            if low <= score <= high:
                return label
        raise ValueError(f"Addicted_Score {score} does not fall into any defined bin.")

    df[TARGET_COLUMN] = df["Addicted_Score"].apply(bin_score)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()

    required = ["Age", "Gender", "Academic_Level", "Avg_Daily_Usage_Hours",
                "Most_Used_Platform", "Affects_Academic_Performance",
                "Sleep_Hours_Per_Night", "Mental_Health_Score",
                "Relationship_Status", "Conflicts_Over_Social_Media",
                "Addicted_Score"]
    df = df.dropna(subset=required)

    df["Age"] = df["Age"].clip(lower=13, upper=100)
    df["Avg_Daily_Usage_Hours"] = df["Avg_Daily_Usage_Hours"].clip(lower=0, upper=24)
    df["Sleep_Hours_Per_Night"] = df["Sleep_Hours_Per_Night"].clip(lower=0, upper=24)

    return df


def get_feature_target_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    X = df[ALL_FEATURES].copy()
    y = df[TARGET_COLUMN].copy()
    return X, y


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def load_and_prepare(csv_path: str) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(csv_path)
    validate_schema(df)
    df = clean_data(df)
    df = construct_target(df)
    X, y = get_feature_target_split(df)
    return X, y