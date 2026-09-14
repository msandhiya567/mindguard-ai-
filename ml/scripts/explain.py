"""
MindGuard AI - Model Explainability (SHAP)
=============================================
Generates:
  1. A global feature-importance report (which factors matter most
     across all predictions) - saved to reports/shap_global_importance.png
  2. A reusable explainer + explain_prediction() function that the
     FastAPI backend will use to generate a per-user, human-readable
     explanation alongside every prediction.

NOTE ON SHAP VERSION: newer versions of the `shap` library (0.5x) dropped
native TreeExplainer support for multiclass GradientBoostingClassifier.
This script uses shap's model-agnostic Explainer (permutation-based)
instead, which works regardless of model type or class count. It's
slower than TreeExplainer, which is why the global report only samples
a subset of rows rather than running on all 705.

Run from the ml/scripts/ directory:
    python explain.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from pipeline import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    load_and_prepare,
)

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR.parent / "data" / "Students_Social_Media_Addiction.csv"
ARTIFACT_PATH = SCRIPT_DIR.parent / "artifacts" / "risk_model.joblib"
REPORTS_DIR = SCRIPT_DIR.parent / "reports"

BACKGROUND_SIZE = 50
GLOBAL_REPORT_SAMPLE_SIZE = 100

FACTOR_DESCRIPTIONS = {
    "Avg_Daily_Usage_Hours": "your average daily social media usage",
    "Conflicts_Over_Social_Media": "how often social media causes conflict for you",
    "Mental_Health_Score": "your self-reported mental well-being score",
    "Sleep_Hours_Per_Night": "your average nightly sleep",
    "Age": "your age",
    "Gender": "gender",
    "Academic_Level": "your academic level",
    "Most_Used_Platform": "your most-used platform",
    "Affects_Academic_Performance": "whether social media affects your academic performance",
    "Relationship_Status": "your relationship status",
}


def get_onehot_feature_names(preprocessor) -> list[str]:
    num_names = NUMERIC_FEATURES
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    return num_names + cat_names


def map_encoded_name_to_raw_feature(encoded_name: str) -> str:
    if encoded_name in NUMERIC_FEATURES:
        return encoded_name
    for raw_feature in CATEGORICAL_FEATURES:
        if encoded_name.startswith(raw_feature + "_"):
            return raw_feature
    return encoded_name


def build_explainer(pipe, X_transformed_background: np.ndarray, feature_names: list[str]):
    """
    Model-agnostic SHAP explainer built around predict_proba. Works for
    ANY sklearn classifier regardless of class count - unlike
    TreeExplainer, which currently only supports binary
    GradientBoostingClassifier.

    In the backend, build this ONCE at app startup and reuse it for
    every prediction request - do not rebuild it per-request.
    """
    model = pipe.named_steps["model"]
    masker = shap.maskers.Independent(X_transformed_background)
    explainer = shap.Explainer(
        model.predict_proba, masker, feature_names=feature_names
    )
    return explainer


def build_global_report():
    print("[1/2] Loading model artifact and data...")
    pipe = joblib.load(ARTIFACT_PATH)
    preprocessor = pipe.named_steps["preprocess"]

    X, y = load_and_prepare(str(DATA_PATH))
    X_transformed = preprocessor.transform(X)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()

    feature_names = get_onehot_feature_names(preprocessor)

    rng = np.random.default_rng(42)
    n_rows = X_transformed.shape[0]

    background_idx = rng.choice(n_rows, size=min(BACKGROUND_SIZE, n_rows), replace=False)
    background = X_transformed[background_idx]

    sample_idx = rng.choice(n_rows, size=min(GLOBAL_REPORT_SAMPLE_SIZE, n_rows), replace=False)
    sample = X_transformed[sample_idx]

    print(f"[2/2] Computing SHAP values on a sample of {len(sample)} rows "
          f"(background={len(background)} rows). This can take a minute...")

    explainer = build_explainer(pipe, background, feature_names)
    explanation = explainer(sample)

    values = explanation.values
    if values.ndim == 3:
        mean_abs = np.abs(values).mean(axis=(0, 2))
    else:
        mean_abs = np.abs(values).mean(axis=0)

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "raw_feature": [map_encoded_name_to_raw_feature(f) for f in feature_names],
        "mean_abs_shap": mean_abs,
    })

    raw_importance = (
        importance_df.groupby("raw_feature")["mean_abs_shap"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\nGlobal feature importance (raw features, summed across categories):")
    print(raw_importance.to_string())

    fig, ax = plt.subplots(figsize=(8, 5))
    raw_importance.plot(kind="barh", ax=ax)
    ax.set_xlabel("Mean |SHAP value| (avg across sampled rows and classes)")
    ax.set_title("MindGuard AI - Global Feature Importance")
    ax.invert_yaxis()
    plt.tight_layout()
    out_path = REPORTS_DIR / "shap_global_importance.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"\nSaved plot to {out_path}")

    raw_importance.to_csv(REPORTS_DIR / "shap_global_importance.csv")
    print(f"Saved CSV to {REPORTS_DIR / 'shap_global_importance.csv'}")


def explain_prediction(pipe, explainer, user_input_df: pd.DataFrame, top_n: int = 4) -> dict:
    """
    Human-readable explanation for ONE user's prediction. This is what
    the FastAPI backend calls at inference time. `explainer` should be
    built ONCE at app startup via build_explainer() and reused.
    """
    preprocessor = pipe.named_steps["preprocess"]

    predicted_class = pipe.predict(user_input_df)[0]
    proba = pipe.predict_proba(user_input_df)[0]
    class_labels = pipe.classes_.tolist()
    probabilities = {label: float(p) for label, p in zip(class_labels, proba)}

    X_transformed = preprocessor.transform(user_input_df)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()

    feature_names = get_onehot_feature_names(preprocessor)
    predicted_class_idx = class_labels.index(predicted_class)

    explanation = explainer(X_transformed)
    values = explanation.values
    if values.ndim == 3:
        row_shap = values[0, :, predicted_class_idx]
    else:
        row_shap = values[0]

    contrib_df = pd.DataFrame({
        "feature": feature_names,
        "raw_feature": [map_encoded_name_to_raw_feature(f) for f in feature_names],
        "shap_value": row_shap,
    })
    raw_contrib = contrib_df.groupby("raw_feature")["shap_value"].sum()
    raw_contrib = raw_contrib.reindex(raw_contrib.abs().sort_values(ascending=False).index)

    top_factors = []
    for raw_feature, value in raw_contrib.head(top_n).items():
        top_factors.append({
            "factor": FACTOR_DESCRIPTIONS.get(raw_feature, raw_feature),
            "direction": "increases" if value > 0 else "decreases",
            "raw_feature": raw_feature,
        })

    return {
        "predicted_class": predicted_class,
        "probabilities": probabilities,
        "top_factors": top_factors,
    }


if __name__ == "__main__":
    build_global_report()