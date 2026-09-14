"""
MindGuard AI - Model Training & Comparison
=============================================
Trains Logistic Regression, Decision Tree, Random Forest, and Gradient
Boosting on the digital well-being dataset, compares them with
cross-validation, evaluates the best one on a held-out test set, and
serializes the winning pipeline for backend inference.

Run from the ml/scripts/ directory:
    python train_and_compare.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.class_weight import compute_sample_weight

from pipeline import (
    RISK_BINS,
    RISK_ORDER,
    build_preprocessor,
    load_and_prepare,
)

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR.parent / "data" / "Students_Social_Media_Addiction.csv"
ARTIFACTS_DIR = SCRIPT_DIR.parent / "artifacts"
REPORTS_DIR = SCRIPT_DIR.parent / "reports"
RANDOM_STATE = 42

ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)
REPORTS_DIR.mkdir(exist_ok=True, parents=True)


def build_candidate_models() -> dict:
    """
    Returns the candidate models. Class imbalance (High is the majority
    class at 408/705 rows) is handled via class_weight='balanced' where
    supported natively. GradientBoostingClassifier does not support
    class_weight, so it gets sample_weight computed manually at fit time.
    """
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "DecisionTree": DecisionTreeClassifier(
            class_weight="balanced",
            max_depth=6,
            min_samples_leaf=10,
            random_state=RANDOM_STATE,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            max_depth=8,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200,
            max_depth=3,
            learning_rate=0.05,
            random_state=RANDOM_STATE,
        ),
    }


def cross_validate_model(name: str, model, X_train, y_train) -> dict:
    """
    5-fold stratified cross-validation on the TRAINING split only.
    The test set is never touched here - it stays fully held out until
    final evaluation of the single selected model.
    """
    preprocessor = build_preprocessor()
    pipe = Pipeline([("preprocess", preprocessor), ("model", model)])
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    fit_params = {}
    if name == "GradientBoosting":
        sample_weight = compute_sample_weight("balanced", y_train)
        fit_params = {"model__sample_weight": sample_weight}

    scores = cross_val_score(
        pipe, X_train, y_train, cv=skf, scoring="f1_macro",
        params=fit_params if fit_params else None,
    )
    return {"mean_f1_macro": float(scores.mean()), "std_f1_macro": float(scores.std()), "folds": scores.tolist()}


def evaluate_on_test(name: str, model, X_train, y_train, X_test, y_test) -> dict:
    """
    Fits the pipeline on the full training set and evaluates ONCE on the
    held-out test set. This happens only for the model selected by
    cross-validation, to avoid test-set leakage from repeated peeking.
    """
    preprocessor = build_preprocessor()
    pipe = Pipeline([("preprocess", preprocessor), ("model", model)])

    if name == "GradientBoosting":
        sample_weight = compute_sample_weight("balanced", y_train)
        pipe.fit(X_train, y_train, model__sample_weight=sample_weight)
    else:
        pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)

    # Ensure class ordering is consistent for ROC-AUC (one-vs-rest)
    class_order = pipe.classes_.tolist()

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=RISK_ORDER)

    try:
        roc_auc = roc_auc_score(
            y_test, y_proba, multi_class="ovr", average="macro", labels=class_order
        )
    except ValueError as e:
        roc_auc = None
        print(f"  Warning: ROC-AUC could not be computed ({e})")

    return {
        "pipeline": pipe,
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_labels": RISK_ORDER,
        "roc_auc_macro_ovr": roc_auc,
        "class_order": class_order,
    }


def main():
    print("=" * 70)
    print("MindGuard AI - ML Pipeline: Training & Model Comparison")
    print("=" * 70)

    print(f"\n[1/6] Loading and validating data from {DATA_PATH.name}...")
    X, y = load_and_prepare(str(DATA_PATH))
    print(f"      Loaded {len(X)} rows after cleaning.")
    print(f"      Class distribution:\n{y.value_counts().reindex(RISK_ORDER)}")

    print("\n[2/6] Splitting into train/test (80/20, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    print(f"      Train: {len(X_train)} rows | Test: {len(X_test)} rows")
    print(f"      NOTE: test set is held out and untouched until final evaluation.")

    print("\n[3/6] Cross-validating candidate models on TRAINING data only...")
    candidates = build_candidate_models()
    cv_results = {}
    for name, model in candidates.items():
        result = cross_validate_model(name, model, X_train, y_train)
        cv_results[name] = result
        print(f"      {name:20s} mean f1_macro = {result['mean_f1_macro']:.4f} "
              f"(+/- {result['std_f1_macro']:.4f})")

    best_name = max(cv_results, key=lambda n: cv_results[n]["mean_f1_macro"])
    print(f"\n[4/6] Best model by cross-validated f1_macro: {best_name}")

    print(f"\n[5/6] Fitting {best_name} on full training set, evaluating on held-out test set...")
    best_model = candidates[best_name]
    final_result = evaluate_on_test(best_name, best_model, X_train, y_train, X_test, y_test)

    print(f"\n      Test Accuracy:      {final_result['accuracy']:.4f}")
    print(f"      Test F1 (macro):    {final_result['f1_macro']:.4f}")
    if final_result["roc_auc_macro_ovr"] is not None:
        print(f"      Test ROC-AUC (ovr): {final_result['roc_auc_macro_ovr']:.4f}")
    print(f"\n      Per-class report:")
    for label in RISK_ORDER:
        if label in final_result["classification_report"]:
            r = final_result["classification_report"][label]
            print(f"        {label:8s} precision={r['precision']:.3f} "
                  f"recall={r['recall']:.3f} f1={r['f1-score']:.3f} "
                  f"support={int(r['support'])}")
    print(f"\n      Confusion matrix (rows=actual, cols=predicted, order={RISK_ORDER}):")
    for row_label, row in zip(RISK_ORDER, final_result["confusion_matrix"]):
        print(f"        {row_label:8s} {row}")

    print(f"\n[6/6] Saving artifact and report...")

    # Save confusion matrix plot
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    disp = ConfusionMatrixDisplay(
        confusion_matrix=np.array(final_result["confusion_matrix"]),
        display_labels=RISK_ORDER,
    )
    disp.plot(cmap="Blues", values_format="d")
    plt.title(f"Confusion Matrix - {best_name} (test set)")
    plt.tight_layout()
    cm_path = REPORTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"      Saved confusion matrix plot to {cm_path}")

    # Save the winning pipeline
    artifact_path = ARTIFACTS_DIR / "risk_model.joblib"
    joblib.dump(final_result["pipeline"], artifact_path)
    print(f"      Saved model artifact to {artifact_path}")

    # Save full metrics + metadata report (this is the audit trail -
    # nothing in here is invented; it's exactly what was measured above)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_rows_used": len(X),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "risk_bin_thresholds": RISK_BINS,
        "class_order": final_result["class_order"],
        "cross_validation_results": {
            name: {k: v for k, v in r.items() if k != "folds"} | {"folds_f1_macro": r["folds"]}
            for name, r in cv_results.items()
        },
        "selected_model": best_name,
        "selection_criterion": "highest mean cross-validated f1_macro on training set",
        "test_set_evaluation": {
            "accuracy": final_result["accuracy"],
            "f1_macro": final_result["f1_macro"],
            "roc_auc_macro_ovr": final_result["roc_auc_macro_ovr"],
            "classification_report": final_result["classification_report"],
            "confusion_matrix": final_result["confusion_matrix"],
            "confusion_matrix_labels": final_result["confusion_matrix_labels"],
        },
    }
    report_path = REPORTS_DIR / "training_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"      Saved full metrics report to {report_path}")

    print("\n" + "=" * 70)
    print(f"DONE. Selected model: {best_name}")
    print("=" * 70)


if __name__ == "__main__":
    sys.exit(main())