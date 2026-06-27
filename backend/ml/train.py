"""
LeadPredict v2 — Training Pipeline (Enhanced).

Improvements over v1:
  - Engineered ratio features (meeting_completion_ratio, call_connection_rate,
    email_click_rate, avg_call_duration, engagement_score)
  - call_duration_minutes now properly included as a signal
  - Extensive hyperparameter tuning (7D grid, 432 combos)
  - 5-fold stratified cross-validation
  - Class-weighted sample weights for imbalance
  - Early stopping to prevent overfitting
  - Detailed evaluation with confusion matrix & feature importance
"""

import os
import json
import warnings
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    roc_auc_score,
    f1_score,
)

import xgboost as xgb

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "lead_data.csv")
MODEL_DIR = os.path.join(BASE_DIR)

MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor.pkl")
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, "feature_names.pkl")
ONNX_PATH = os.path.join(MODEL_DIR, "model.onnx")
METRICS_PATH = os.path.join(MODEL_DIR, "training_metrics.json")

# ---------------------------------------------------------------------------
# Columns
# ---------------------------------------------------------------------------
CATEGORICAL_FEATURES = ["lead_source", "industry"]

NUMERICAL_FEATURES = [
    "company_size",
    "website_visits",
    "emails_opened",
    "emails_clicked",
    "calls_made",
    "calls_connected",
    "call_duration_minutes",
    "meetings_scheduled",
    "meetings_done",
    "days_since_first_contact",
    "follow_ups_total",
    "demo_requested",
    "budget_available",
    "decision_maker_contacted",
    "competitor_considering",
    "employee_tenure_days",
    "employee_prev_conversion_rate",
]

ENGINEERED_FEATURES = [
    "meeting_completion_ratio",
    "call_connection_rate",
    "email_click_rate",
    "avg_call_duration",
    "engagement_score",
]

TARGET = "outcome"
CLASS_NAMES = ["cold", "rejected", "successful"]  # 0, 1, 2


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------

def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add ratio-based engineered features to the DataFrame (in-place copy).

    Features added:
        - meeting_completion_ratio: meetings_done / max(meetings_scheduled, 1)
        - call_connection_rate: calls_connected / max(calls_made, 1)
        - email_click_rate: emails_clicked / max(emails_opened, 1)
        - avg_call_duration: call_duration_minutes / max(calls_made, 1)
        - engagement_score: weighted composite of key engagement signals
    """
    df = df.copy()

    # Ratio features
    df["meeting_completion_ratio"] = (
        df["meetings_done"] / np.maximum(df["meetings_scheduled"], 1)
    )
    df["call_connection_rate"] = (
        df["calls_connected"] / np.maximum(df["calls_made"], 1)
    )
    df["email_click_rate"] = (
        df["emails_clicked"] / np.maximum(df["emails_opened"], 1)
    )
    df["avg_call_duration"] = (
        df["call_duration_minutes"] / np.maximum(df["calls_made"], 1)
    ).clip(upper=60)  # cap at 60 min avg per call — outliers happen

    # Engagement score — weighted combination of signals
    # Weights are based on domain knowledge of what drives conversions
    df["engagement_score"] = (
        (df["website_visits"] / 50.0) * 0.08
        + (df["emails_opened"] / 20.0) * 0.07
        + (df["emails_clicked"] / 10.0) * 0.12
        + (df["calls_connected"] / 10.0) * 0.15
        + (df["call_duration_minutes"] / 300.0) * 0.18
        + (df["meetings_done"] / 5.0) * 0.20
        + df["demo_requested"] * 0.10
        + df["budget_available"] * 0.05
        + df["decision_maker_contacted"] * 0.05
    ).clip(0, 1)  # keep in [0, 1] range

    return df


def build_preprocessor():
    """Build a column transformer for categorical OHE + numerical scaling.

    The engineered features are treated as numerical and standard-scaled.
    """
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    numerical_transformer = StandardScaler()

    all_numerical = NUMERICAL_FEATURES + ENGINEERED_FEATURES

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("num", numerical_transformer, all_numerical),
        ]
    )
    return preprocessor


def get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """Extract final feature names from the fitted preprocessor."""
    cat_features = []
    cat_transformer = preprocessor.named_transformers_["cat"]
    if hasattr(cat_transformer, "get_feature_names_out"):
        cat_features = cat_transformer.get_feature_names_out(
            CATEGORICAL_FEATURES
        ).tolist()
    else:
        categories = cat_transformer.categories_
        for col, cats in zip(CATEGORICAL_FEATURES, categories):
            cat_features.extend(f"{col}_{cat}" for cat in cats)

    num_features = NUMERICAL_FEATURES + ENGINEERED_FEATURES
    return cat_features + num_features


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load lead CSV data and add engineered features."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found at {path}")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} records from {path}")
    return df


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> xgb.XGBClassifier:
    """Train XGBoost classifier with hyperparameter tuning via GridSearchCV.

    Uses 5-fold stratified CV, class-weighted sample weights, and early stopping
    for the final model.

    Parameters
    ----------
    X_train : np.ndarray
        Preprocessed training features.
    y_train : np.ndarray
        Training labels (0, 1, 2).

    Returns
    -------
    Best XGBClassifier found by grid search, retrained with early stopping.
    """
    # ---- Compute class weights for imbalance ----
    classes, counts = np.unique(y_train, return_counts=True)
    n_samples = len(y_train)
    n_classes = len(classes)
    weight_map = {c: n_samples / (n_classes * cnt) for c, cnt in zip(classes, counts)}
    sample_weight = np.array([weight_map[y] for y in y_train])

    print(f"\nClass weights: { {CLASS_NAMES[c]: f'{weight_map[c]:.3f}' for c in range(3)} }")

    # ---- Hold out a validation set for early stopping ----
    X_train_sub, X_val, y_train_sub, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
    )

    # Split sample weights accordingly
    sub_indices = np.arange(len(y_train))
    _, val_indices = train_test_split(
        sub_indices, test_size=0.15, random_state=42, stratify=y_train
    )
    train_mask = np.ones(len(y_train), dtype=bool)
    train_mask[val_indices] = False
    sw_train = sample_weight[train_mask]
    sw_val = sample_weight[val_indices]

    # ---- Base model ----
    base_model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )

    # ---- Extensive Hyperparameter Search (Randomized) ----
    # Full grid has 4860 combos; we sample 500 efficiently via RandomizedSearchCV
    param_distributions = {
        "n_estimators": [100, 200, 300],
        "max_depth": [3, 4, 5, 6, 7],
        "learning_rate": [0.01, 0.03, 0.05, 0.1],
        "subsample": [0.6, 0.8, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
        "min_child_weight": [1, 3, 5],
        "gamma": [0, 0.1, 0.2],
    }

    n_iter = 400
    total_combos = int(np.prod([len(v) for v in param_distributions.values()]))
    print(f"\nHyperparameter space: {total_combos} combos, sampling {n_iter} with 5-fold CV = {n_iter * 5} fits")

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        scoring="f1_macro",
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        verbose=1,
        n_jobs=-1,
        random_state=42,
    )

    search.fit(X_train_sub, y_train_sub, sample_weight=sw_train)

    print(f"\nBest parameters: {search.best_params_}")
    print(f"Best cross-val F1 (macro): {search.best_score_:.4f}")

    # ---- Retrain with early stopping on the full training set ----
    best_params = search.best_params_
    best_params["early_stopping_rounds"] = 25
    best_params["eval_metric"] = "mlogloss"
    best_params["random_state"] = 42
    best_params["n_jobs"] = -1
    best_params["verbosity"] = 0

    final_model = xgb.XGBClassifier(**best_params)
    final_model.fit(
        X_train, y_train,
        sample_weight=sample_weight,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    print(f"Final model trained with early stopping (best iteration: {final_model.best_iteration if hasattr(final_model, 'best_iteration') else 'N/A'})")

    return final_model


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_model(
    model: xgb.XGBClassifier,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: list[str],
) -> dict:
    """Print and return evaluation metrics."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    # ---- Per-class metrics ----
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=[0, 1, 2]
    )

    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    print(f"{'Class':<15} {'Precision':<10} {'Recall':<10} {'F1':<10} {'Support':<10}")
    print("-" * 55)
    for i, cls_name in enumerate(CLASS_NAMES):
        print(
            f"{cls_name:<15} {precision[i]:<10.4f} {recall[i]:<10.4f} "
            f"{f1[i]:<10.4f} {support[i]:<10}"
        )

    accuracy = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    print(f"\nAccuracy:  {accuracy:.4f}")
    print(f"F1 Macro:  {f1_macro:.4f}")
    print(f"F1 Weighted: {f1_weighted:.4f}")

    # ---- Confusion matrix ----
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(f"{'':>15} {'Predicted':>30}")
    print(f"{'':>15} ", end="")
    for cls_name in CLASS_NAMES:
        print(f"{cls_name:>10}", end="")
    print()
    for i, cls_name in enumerate(CLASS_NAMES):
        print(f"{'Actual ' + cls_name:<15}", end="")
        for j in range(3):
            print(f"{cm[i, j]:>10}", end="")
        print()

    # ---- ROC AUC (one-vs-rest) ----
    try:
        roc_auc = roc_auc_score(y_test, y_proba, multi_class="ovr")
        print(f"\nROC AUC (one-vs-rest): {roc_auc:.4f}")
    except Exception as e:
        print(f"\nROC AUC could not be computed: {e}")
        roc_auc = None

    # ---- Feature importance (top 20) ----
    importance = model.feature_importances_
    sorted_idx = np.argsort(importance)[::-1][:20]

    print("\n" + "=" * 60)
    print("TOP 20 FEATURE IMPORTANCE")
    print("=" * 60)
    print(f"{'Feature':<40} {'Importance':<10}")
    print("-" * 50)
    top_features = []
    for idx in sorted_idx:
        print(f"{feature_names[idx]:<40} {importance[idx]:<10.6f}")
        top_features.append((feature_names[idx], float(importance[idx])))

    metrics = {
        "accuracy": float(accuracy),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "precision_per_class": {CLASS_NAMES[i]: float(precision[i]) for i in range(3)},
        "recall_per_class": {CLASS_NAMES[i]: float(recall[i]) for i in range(3)},
        "f1_per_class": {CLASS_NAMES[i]: float(f1[i]) for i in range(3)},
        "support_per_class": {CLASS_NAMES[i]: int(support[i]) for i in range(3)},
        "roc_auc_ovr": float(roc_auc) if roc_auc is not None else None,
        "confusion_matrix": cm.tolist(),
        "top_features": top_features,
        "best_params": model.get_params(),
    }
    return metrics


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def save_model_artifacts(
    model: xgb.XGBClassifier,
    preprocessor: ColumnTransformer,
    feature_names: list[str],
    metrics: dict,
) -> None:
    """Persist model, preprocessor, feature names, and metrics to disk."""
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    print(f"Preprocessor saved to {PREPROCESSOR_PATH}")

    joblib.dump(feature_names, FEATURE_NAMES_PATH)
    print(f"Feature names saved to {FEATURE_NAMES_PATH}")

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"Metrics saved to {METRICS_PATH}")


def save_onnx(model: xgb.XGBClassifier, feature_names: list[str]) -> None:
    """Convert the trained XGBoost model to ONNX format (optional)."""
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType

        n_features = len(feature_names)
        initial_type = [("float_input", FloatTensorType([None, n_features]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type)
        with open(ONNX_PATH, "wb") as f:
            f.write(onnx_model.SerializeToString())
        print(f"ONNX model saved to {ONNX_PATH}")
    except ImportError:
        print("skl2onnx not installed — skipping ONNX export.")
    except Exception as e:
        print(f"ONNX export failed: {e} — skipping.")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main(data_path: str = DATA_PATH) -> dict:
    """Run the full training pipeline."""
    print("=" * 60)
    print("LeadPredict v2 — Training Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")

    # 1. Load data
    df = load_data(data_path)
    print(f"Columns: {list(df.columns)}")
    print(f"Class distribution:\n{df[TARGET].value_counts().sort_index()}")

    # 2. Add engineered features
    print("\n--- Engineering features ---")
    df = add_engineered_features(df)
    all_feature_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + ENGINEERED_FEATURES
    print(f"Feature columns ({len(all_feature_cols)}): {all_feature_cols}")

    X = df[all_feature_cols]
    y = df[TARGET].values

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\nTrain size: {len(X_train)} | Test size: {len(X_test)}")

    # 4. Build & fit preprocessor
    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    feature_names = get_feature_names(preprocessor)
    print(f"Feature count (after encoding): {len(feature_names)}")
    print(f"Feature names: {feature_names}")

    # 5. Train model
    model = train_model(X_train_processed, y_train)

    # 6. Evaluate
    metrics = evaluate_model(model, X_test_processed, y_test, feature_names)

    # 7. Save artifacts
    save_model_artifacts(model, preprocessor, feature_names, metrics)

    # 8. ONNX (bonus)
    save_onnx(model, feature_names)

    print(f"\nFinished at: {datetime.now().isoformat()}")
    print("=" * 60)

    return metrics


if __name__ == "__main__":
    main()
