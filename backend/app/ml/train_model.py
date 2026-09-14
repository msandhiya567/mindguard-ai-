"""
MindGuard AI - Model Training Script
======================================
Run from the mindguard-ai/ root folder:
    python ml/train_model.py

Trains a classifier to predict digital well-being risk_level (Low/Medium/High)
from the cleaned dataset, using a proper sklearn Pipeline (ColumnTransformer +
OneHotEncoder for categoricals, passthrough for numerics) to avoid leakage
and avoid treating categories as ordered numbers.
"""

import os

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ---------------------------------------------------------------------
# Paths (script runs from mindguard-ai/ root)
# ---------------------------------------------------------------------
DATASET_PATH = os.path.join("..", "dataset", "clean_dataset.csv")
ARTIFACTS_DIR = os.path.join("ml", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------
df = pd.read_csv(DATASET_PATH)
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print("Raw columns:", list(df.columns))

# Normalize column names -> match AssessmentAnswer model field names exactly
df = df.rename(columns={
    "academic": "academic_level",
    "avgdailyusagehours": "avg_daily_usage_hours",
    "avgdailyuasgehours": "avg_daily_usage_hours",  # handles either spelling
    "most used platform": "most_used_platform",
    "affects academic performance": "affects_academic_performance",
    "sleephourpernight": "sleep_hours_per_night",
    "mentalhealthscore": "mental_health_score",
    "relationshipstatus": "relationship_status",
    "conflicts oversocialmedia": "conflicts_over_social_media",
    "coflicts oversocialmedia": "conflicts_over_social_media",  # handles either spelling
    "addicted score": "addicted_score",
})

FEATURE_COLUMNS = [
    "age",
    "gender",
    "academic_level",
    "avg_daily_usage_hours",
    "most_used_platform",
    "affects_academic_performance",
    "sleep_hours_per_night",
    "mental_health_score",
    "relationship_status",
    "conflicts_over_social_media",
]

CATEGORICAL_COLUMNS = [
    "gender",
    "academic_level",
    "most_used_platform",
    "affects_academic_performance",
    "relationship_status",
]

NUMERIC_COLUMNS = [c for c in FEATURE_COLUMNS if c not in CATEGORICAL_COLUMNS]

missing = [c for c in FEATURE_COLUMNS + ["addicted_score"] if c not in df.columns]
if missing:
    raise ValueError(f"Dataset is missing expected columns after rename: {missing}")

# ---------------------------------------------------------------------
# 2. Build target: bucket addicted_score into Low/Medium/High
# ---------------------------------------------------------------------
print("\naddicted_score range:", df["addicted_score"].min(), "-", df["addicted_score"].max())


def bucket_risk(score):
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    else:
        return "High"


df["risk_level"] = df["addicted_score"].apply(bucket_risk)
print("\nTarget distribution:")
print(df["risk_level"].value_counts())

# ---------------------------------------------------------------------
# 3. Train/test split (stratified, before any fitting -> no leakage)
# ---------------------------------------------------------------------
X = df[FEATURE_COLUMNS]
y = df["risk_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

# ---------------------------------------------------------------------
# 4. Preprocessing + model pipeline
#    OneHotEncoder for categoricals -> no false ordering assumed.
#    handle_unknown="ignore" so a category unseen in training (e.g. a
#    platform not in the dataset) doesn't crash prediction later.
# ---------------------------------------------------------------------
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
        ("num", "passthrough", NUMERIC_COLUMNS),
    ]
)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", GradientBoostingClassifier(random_state=42)),
])

pipeline.fit(X_train, y_train)

# ---------------------------------------------------------------------
# 5. Evaluate
# ---------------------------------------------------------------------
y_pred = pipeline.predict(X_test)

acc = accuracy_score(y_test, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)

print(f"\nAccuracy:  {acc:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 score:  {f1:.3f}")
print("\nClassification report:")
print(classification_report(y_test, y_pred, zero_division=0))

# ---------------------------------------------------------------------
# 6. Save artifacts
#    The whole pipeline (preprocessing + model) is saved as ONE object,
#    so predict.py doesn't need to redo encoding manually.
# ---------------------------------------------------------------------
joblib.dump(pipeline, os.path.join(ARTIFACTS_DIR, "model.pkl"))
joblib.dump(FEATURE_COLUMNS, os.path.join(ARTIFACTS_DIR, "feature_columns.pkl"))

print(f"\nSaved model pipeline -> {ARTIFACTS_DIR}/model.pkl")
print(f"Saved feature columns -> {ARTIFACTS_DIR}/feature_columns.pkl")
print("\nDone. This is a risk-SCREENING signal only, not a medical diagnosis.")