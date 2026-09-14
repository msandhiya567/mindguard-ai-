"""
MindGuard AI - Model Training Script
======================================
Run from the mindguard-ai/ root folder:
    python ml/train_model.py
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
DATASET_PATH = os.path.join("..","dataset", "clean_dataset.csv")
ARTIFACTS_DIR = os.path.join("ml", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------
df = pd.read_csv(DATASET_PATH)
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print("Raw columns:", list(df.columns))

# Real dataset columns are Title_Case with underscores, e.g. 'Age', 'Academic_Level'.
# Rename to match AssessmentAnswer model field names exactly (lowercase snake_case).
df = df.rename(columns={
    "Age": "age",
    "Gender": "gender",
    "Academic_Level": "academic_level",
    "Avg_Daily_Usage_Hours": "avg_daily_usage_hours",
    "Most_Used_Platform": "most_used_platform",
    "Affects_Academic_Performance": "affects_academic_performance",
    "Sleep_Hours_Per_Night": "sleep_hours_per_night",
    "Mental_Health_Score": "mental_health_score",
    "Relationship_Status": "relationship_status",
    "Conflicts_Over_Social_Media": "conflicts_over_social_media",
    "Addicted_Score": "addicted_score",
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
# ---------------------------------------------------------------------
joblib.dump(pipeline, os.path.join(ARTIFACTS_DIR, "model.pkl"))
joblib.dump(FEATURE_COLUMNS, os.path.join(ARTIFACTS_DIR, "feature_columns.pkl"))

print(f"\nSaved model pipeline -> {ARTIFACTS_DIR}/model.pkl")
print(f"Saved feature columns -> {ARTIFACTS_DIR}/feature_columns.pkl")
print("\nDone. This is a risk-SCREENING signal only, not a medical diagnosis.")