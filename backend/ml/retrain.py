"""
LeadPredict — Retraining Script.

Can be called:
  - On a schedule (cron / CI) to keep the model fresh with new data.
  - Manually after data corrections or feature changes.

Workflow:
  1. Loads the existing model & preprocessor from disk.
  2. Loads new training data (CSV or other source).
  3. Retrains a new model with the same hyperparameters found previously.
  4. Evaluates both old and new models on a held-out test set.
  5. Compares performance — replaces artifacts only if the new model is better.
  6. Logs all metrics for monitoring.
"""

import os
import json
import sys
import warnings
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.compose import ColumnTransformer

import xgboost as xgb

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "lead_data.csv")  # default

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "preprocessor.pkl")
FEATURE_NAMES_PATH = os.path.join(BASE_DIR, "feature_names.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "training_metrics.json")
RETRAIN_LOG_PATH = os.path.join(BASE_DIR, "retrain_log.json")

CLASS_NAMES = ["cold", "rejected", "successful"]
TARGET = "outcome"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_existing_artifacts() -> tuple[Optional[object], Optional[object], Optional[list[str]]]:
    """Load the current model, preprocessor and feature names."""
    model = None
    preprocessor = None
    feature_names = None
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("Existing model loaded.")
    if os.path.exists(PREPROCESSOR_PATH):
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("Existing preprocessor loaded.")
    if os.path.exists(FEATURE_NAMES_PATH):
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        print("Existing feature names loaded.")
    return model, preprocessor, feature_names


def load_training_data(data_path: str) -> pd.DataFrame:
    """Load and validate the training dataset."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training data not found at {data_path}")
    df = pd.read_csv(data_path)
    if df.empty:
        raise ValueError("Training data is empty.")
    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' not found in data.")
    print(f"Loaded {len(df)} records from {data_path}")
    return df


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute standard classification metrics."""
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1, 2]
    )
    f1_macro = f1_score(y_true, y_pred, average="macro")
    f1_weighted = f1_score(y_true, y_pred, average="weighted")

    return {
        "accuracy": float(accuracy),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "precision_per_class": {CLASS_NAMES[i]: float(precision[i]) for i in range(3)},
        "recall_per_class": {CLASS_NAMES[i]: float(recall[i]) for i in range(3)},
        "f1_per_class": {CLASS_NAMES[i]: float(f1[i]) for i in range(3)},
        "support_per_class": {CLASS_NAMES[i]: int(support[i]) for i in range(3)},
    }


def save_artifacts(
    model: xgb.XGBClassifier,
    preprocessor: ColumnTransformer,
    feature_names: list[str],
) -> None:
    """Overwrite the production model artifacts."""
    joblib.dump(model, MODEL_PATH)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    joblib.dump(feature_names, FEATURE_NAMES_PATH)
    print("\nNew model artifacts saved.")


def log_retraining(result: dict) -> None:
    """Append a retraining event to the retrain log (JSON array)."""
    existing = []
    if os.path.exists(RETRAIN_LOG_PATH):
        try:
            with open(RETRAIN_LOG_PATH, "r") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, Exception):
            existing = []
    existing.append(result)
    with open(RETRAIN_LOG_PATH, "w") as f:
        json.dump(existing, f, indent=2, default=str)
    print(f"Retraining event logged to {RETRAIN_LOG_PATH}")


# ---------------------------------------------------------------------------
# Main retrain function
# ---------------------------------------------------------------------------


def retrain(
    data_path: str = DATA_PATH,
    force_replace: bool = False,
) -> dict:
    """Execute the retraining workflow.

    Parameters
    ----------
    data_path : str
        Path to the new training data CSV.
    force_replace : bool
        If True, replace existing model even if metrics are worse.

    Returns
    -------
    dict with comparison results.
    """
    print("=" * 60)
    print("LeadPredict — Retraining Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")

    # 1. Load existing artifacts
    old_model, preprocessor, feature_names = load_existing_artifacts()

    # 2. Load new data
    df = load_training_data(data_path)

    X = df.drop(columns=[TARGET])
    y = df[TARGET].values

    # 3. Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Train: {len(X_train)} | Test: {len(X_test)}")

    # 4. Preprocess
    #    If we have a preprocessor, we reuse it. Otherwise build a new one.
    if preprocessor is not None:
        print("Reusing existing preprocessor.")
        cat_features_original = []
        num_features_original = []
        for name, _, cols in preprocessor.transformers:
            if name == "cat":
                cat_features_original = (
                    cols if isinstance(cols, list) else list(cols)
                )
            elif name == "num":
                num_features_original = (
                    cols if isinstance(cols, list) else list(cols)
                )
        # Ensure columns exist
        missing = [c for c in cat_features_original + num_features_original if c not in X.columns]
        if missing:
            print(f"WARNING: Columns missing from new data: {missing}. Building new preprocessor.")

            # Build fresh preprocessor from train.py's logic
            from train import build_preprocessor, get_feature_names

            preprocessor = build_preprocessor()
            X_train_processed = preprocessor.fit_transform(X_train)
            X_test_processed = preprocessor.transform(X_test)
            feature_names = get_feature_names(preprocessor)
        else:
            X_train_processed = preprocessor.transform(X_train)
            X_test_processed = preprocessor.transform(X_test)
            # feature_names remain the same
    else:
        print("No existing preprocessor — building from scratch.")
        from train import build_preprocessor, get_feature_names

        preprocessor = build_preprocessor()
        X_train_processed = preprocessor.fit_transform(X_train)
        X_test_processed = preprocessor.transform(X_test)
        feature_names = get_feature_names(preprocessor)

    print(f"Feature count: {len(feature_names)}")

    # 5. Retrain new model
    #    Use the same best hyperparameters if available from old model
    if old_model is not None:
        best_params = old_model.get_params()
        # Remove internal / non-constructor params
        best_params.pop("_Booster", None)
        best_params.pop("classes_", None)
        best_params.pop("n_classes_", None)
        best_params.pop("feature_names_in_", None)
    else:
        best_params = {
            "objective": "multi:softprob",
            "num_class": 3,
            "eval_metric": "mlogloss",
            "random_state": 42,
            "n_jobs": -1,
            "verbosity": 0,
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 1,
        }

    new_model = xgb.XGBClassifier(**best_params)
    new_model.fit(X_train_processed, y_train)
    print("New model trained.")

    # 6. Evaluate new model
    y_pred_new = new_model.predict(X_test_processed)
    new_metrics = compute_metrics(y_test, y_pred_new)
    new_accuracy = new_metrics["accuracy"]
    new_f1_macro = new_metrics["f1_macro"]

    print(f"\nNew model — Accuracy: {new_accuracy:.4f} | F1 (macro): {new_f1_macro:.4f}")

    # 7. Evaluate old model (if it exists)
    old_metrics = None
    replaced = False
    if old_model is not None:
        try:
            y_pred_old = old_model.predict(X_test_processed)
            old_metrics = compute_metrics(y_test, y_pred_old)
            old_accuracy = old_metrics["accuracy"]
            old_f1_macro = old_metrics["f1_macro"]

            print(f"Old model — Accuracy: {old_accuracy:.4f} | F1 (macro): {old_f1_macro:.4f}")

            # Compare
            if new_f1_macro > old_f1_macro or force_replace:
                print(f"\n>>> New model is {'better' if new_f1_macro > old_f1_macro else 'forced to replace'} — replacing artifacts.")
                save_artifacts(new_model, preprocessor, feature_names)
                replaced = True
            else:
                print("\n>>> Old model performs better or equivalently — keeping existing artifacts.")
                replaced = False
        except Exception as e:
            print(f"Could not evaluate old model: {e}")
            print("Saving new model as fallback.")
            save_artifacts(new_model, preprocessor, feature_names)
            replaced = True
    else:
        print("No existing model to compare — saving new model.")
        save_artifacts(new_model, preprocessor, feature_names)
        replaced = True

    # 8. Build result record
    result = {
        "timestamp": datetime.now().isoformat(),
        "data_path": data_path,
        "n_samples": len(df),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "class_distribution": df[TARGET].value_counts().to_dict(),
        "replaced": replaced,
        "new_model_params": best_params,
        "new_model_metrics": new_metrics,
        "old_model_metrics": old_metrics,
    }

    # 9. Log
    log_retraining(result)

    # 10. Also update training_metrics.json
    with open(METRICS_PATH, "w") as f:
        json.dump(new_metrics, f, indent=2, default=str)

    print(f"\nFinished at: {datetime.now().isoformat()}")
    print("=" * 60)

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LeadPredict — Retrain Model")
    parser.add_argument(
        "--data", type=str, default=DATA_PATH,
        help="Path to training data CSV (default: %(default)s)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force replace existing model even if metrics are worse"
    )
    args = parser.parse_args()

    result = retrain(data_path=args.data, force_replace=args.force)
    print("\nRetraining summary:")
    print(json.dumps(result, indent=2, default=str))
