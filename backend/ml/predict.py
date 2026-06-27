"""
LeadPredict v2 — Prediction Interface.

Loads the trained model and preprocessor, then provides:

- ``predict_single``: predict one lead (dict -> dict).
- ``predict_batch``: predict many leads (list[dict] -> list[dict]).
- ``get_feature_importance``: return global feature importance.

Key change from v1: automatically computes engineered ratio features
if they are not present in the input data, so both old-format (raw 19 features)
and new-format (with pre-computed engineered features) inputs are supported.
"""

import os
from typing import Any

import numpy as np
import pandas as pd
import joblib

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "preprocessor.pkl")
FEATURE_NAMES_PATH = os.path.join(BASE_DIR, "feature_names.pkl")

CLASS_NAMES = ["cold", "rejected", "successful"]

# Features expected by the preprocessor
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

ALL_RAW_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

# ---------------------------------------------------------------------------
# Lazy-loaded singletons
# ---------------------------------------------------------------------------
_model = None
_preprocessor = None
_feature_names = None


def _load_artifacts() -> None:
    """Load model, preprocessor, and feature names from disk (once)."""
    global _model, _preprocessor, _feature_names
    if _model is not None:
        return

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. Run train.py first."
        )
    if not os.path.exists(PREPROCESSOR_PATH):
        raise FileNotFoundError(
            f"Preprocessor file not found at {PREPROCESSOR_PATH}. Run train.py first."
        )

    _model = joblib.load(MODEL_PATH)
    _preprocessor = joblib.load(PREPROCESSOR_PATH)
    _feature_names = (
        joblib.load(FEATURE_NAMES_PATH)
        if os.path.exists(FEATURE_NAMES_PATH)
        else None
    )
    if _feature_names is None:
        _feature_names = _derive_feature_names()
    print(f"Model loaded from {MODEL_PATH}")


def _derive_feature_names() -> list[str]:
    """Try to reconstruct feature names from the preprocessor."""
    try:
        cat_transformer = _preprocessor.named_transformers_["cat"]
        cat_feats = cat_transformer.get_feature_names_out().tolist()
    except Exception:
        cat_feats = []
    try:
        num_transformer = _preprocessor.named_transformers_["num"]
        # Extract numerical feature names from the transformer's feature_names_in if available
        if hasattr(num_transformer, "feature_names_in_"):
            num_feats = list(num_transformer.feature_names_in_)
        else:
            num_feats = _get_numerical_feature_names()
    except Exception:
        num_feats = []
    return cat_feats + num_feats


def _get_numerical_feature_names() -> list[str]:
    """Return numerical feature column names from the preprocessor."""
    try:
        for name, _transformer, columns in _preprocessor.transformers:
            if name == "num" and columns not in ("drop", "passthrough"):
                if isinstance(columns, list):
                    return columns
                if hasattr(columns, "tolist"):
                    return columns.tolist()
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------------
# Feature Engineering (mirrors train.py's add_engineered_features)
# ---------------------------------------------------------------------------

def _compute_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered ratio features to the DataFrame.

    Only adds features that are not already present (so old-format inputs
    that lack them are handled automatically).
    """
    df = df.copy()

    if "meeting_completion_ratio" not in df.columns:
        df["meeting_completion_ratio"] = (
            df["meetings_done"] / np.maximum(df["meetings_scheduled"], 1)
        )

    if "call_connection_rate" not in df.columns:
        df["call_connection_rate"] = (
            df["calls_connected"] / np.maximum(df["calls_made"], 1)
        )

    if "email_click_rate" not in df.columns:
        df["email_click_rate"] = (
            df["emails_clicked"] / np.maximum(df["emails_opened"], 1)
        )

    if "avg_call_duration" not in df.columns:
        df["avg_call_duration"] = (
            df["call_duration_minutes"] / np.maximum(df["calls_made"], 1)
        ).clip(upper=60)

    if "engagement_score" not in df.columns:
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
        ).clip(0, 1)

    return df


# ---------------------------------------------------------------------------
# Prediction helpers
# ---------------------------------------------------------------------------

def _prepare_input(lead_data: dict) -> pd.DataFrame:
    """Convert a single lead dict to a DataFrame with all features.

    Handles both:
      - Old format: raw 19 features (no engineered features) — computes them.
      - New format: all features pre-computed — uses as-is.
    """
    df = pd.DataFrame([lead_data])

    # If engineered features are missing, compute them
    has_engineered = all(f in df.columns for f in ENGINEERED_FEATURES)
    if not has_engineered:
        df = _compute_engineered_features(df)

    # Ensure all required columns exist in the right order
    required = ALL_RAW_FEATURES + ENGINEERED_FEATURES
    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"Missing required feature '{col}' in input data. "
                f"Got columns: {list(df.columns)}"
            )

    return df[required]


def _get_top_factors(
    lead_data: dict,
    probabilities: dict[str, float],
    top_n: int = 5,
) -> list[tuple[str, float]]:
    """Return the top *top_n* feature contributions for this prediction.

    Uses a SHAP-inspired heuristic: scale each feature value by its global
    feature importance, normalised by reasonable max values.

    Returns a list of (feature_name, contribution_score) tuples.
    """
    importances = get_feature_importance()
    importance_dict = dict(importances)

    # Approximate max reasonable values for normalisation
    _MAX_VALS = {
        "company_size": 5000,
        "website_visits": 50,
        "emails_opened": 20,
        "emails_clicked": 10,
        "calls_made": 15,
        "calls_connected": 10,
        "call_duration_minutes": 300,
        "meetings_scheduled": 5,
        "meetings_done": 5,
        "days_since_first_contact": 365,
        "follow_ups_total": 30,
        "demo_requested": 1,
        "budget_available": 1,
        "decision_maker_contacted": 1,
        "competitor_considering": 1,
        "employee_tenure_days": 1000,
        "employee_prev_conversion_rate": 1.0,
        # Engineered features
        "meeting_completion_ratio": 1.0,
        "call_connection_rate": 1.0,
        "email_click_rate": 1.0,
        "avg_call_duration": 60.0,
        "engagement_score": 1.0,
    }

    contributions: list[tuple[str, float]] = []
    for key, value in lead_data.items():
        if key in importance_dict:
            imp = importance_dict[key]
            if isinstance(value, (int, float)):
                max_val = _MAX_VALS.get(key, max(abs(value), 1))
                normalised = abs(value) / max_val
                contrib = normalised * imp
            else:
                # Categorical / one-hot: use importance as-is
                contrib = imp
            contributions.append((key, round(contrib, 6)))

    contributions.sort(key=lambda x: x[1], reverse=True)
    return contributions[:top_n]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def predict_single(lead_data: dict) -> dict:
    """Predict the outcome for a single lead.

    Parameters
    ----------
    lead_data : dict
        Dictionary of lead features. Can be either:
          - Raw format (19 features without engineered ratios), or
          - Full format (with engineered features pre-computed).

    Returns
    -------
    dict with keys:
        - probabilities: {"cold": float, "rejected": float, "successful": float}
        - predicted_class: str ("cold", "rejected", or "successful")
        - predicted_class_code: int (0, 1, or 2)
        - confidence: float (max probability)
        - top_factors: list of (feature_name, contribution)
    """
    _load_artifacts()

    df = _prepare_input(lead_data)
    X_processed = _preprocessor.transform(df)

    proba = _model.predict_proba(X_processed)[0]
    pred_class_idx = int(np.argmax(proba))
    confidence = float(proba[pred_class_idx])

    probabilities = {
        CLASS_NAMES[i]: float(proba[i]) for i in range(len(CLASS_NAMES))
    }

    top_factors = _get_top_factors(lead_data, probabilities)

    return {
        "probabilities": probabilities,
        "predicted_class": CLASS_NAMES[pred_class_idx],
        "predicted_class_code": pred_class_idx,
        "confidence": round(confidence, 4),
        "top_factors": top_factors,
    }


def predict_batch(leads: list[dict]) -> list[dict]:
    """Predict outcomes for a batch of leads.

    Parameters
    ----------
    leads : list[dict]
        Each dict must have the same structure as ``predict_single`` input.

    Returns
    -------
    list[dict] — one result per input lead.
    """
    _load_artifacts()

    df = pd.DataFrame(leads)

    # Check if engineered features are present
    has_engineered = all(f in df.columns for f in ENGINEERED_FEATURES)
    if not has_engineered:
        df = _compute_engineered_features(df)

    required = ALL_RAW_FEATURES + ENGINEERED_FEATURES
    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"Missing required feature '{col}' in batch input data. "
                f"Got columns: {list(df.columns)}"
            )

    df = df[required]
    X_processed = _preprocessor.transform(df)
    proba_all = _model.predict_proba(X_processed)
    pred_classes = np.argmax(proba_all, axis=1)

    results = []
    for i in range(len(leads)):
        proba = proba_all[i]
        pred_idx = int(pred_classes[i])
        confidence = float(proba[pred_idx])
        probabilities = {
            CLASS_NAMES[j]: float(proba[j]) for j in range(len(CLASS_NAMES))
        }
        top_factors = _get_top_factors(leads[i], probabilities)

        results.append(
            {
                "probabilities": probabilities,
                "predicted_class": CLASS_NAMES[pred_idx],
                "predicted_class_code": pred_idx,
                "confidence": round(confidence, 4),
                "top_factors": top_factors,
            }
        )

    return results


def get_feature_importance() -> list[tuple[str, float]]:
    """Return global feature importance from the trained model.

    Returns
    -------
    list of (feature_name, importance_score) sorted descending by importance.
    """
    _load_artifacts()
    importances = _model.feature_importances_
    names = (
        _feature_names
        if _feature_names
        else [f"f{i}" for i in range(len(importances))]
    )

    paired = list(zip(names, importances))
    paired.sort(key=lambda x: x[1], reverse=True)
    return [(name, float(score)) for name, score in paired]


# ---------------------------------------------------------------------------
# Quick test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Test 1: HOT lead (should predict "successful" with >85% confidence)
    hot_lead = {
        "lead_source": "Referral",
        "industry": "Technology",
        "company_size": 1200,
        "website_visits": 40,
        "emails_opened": 18,
        "emails_clicked": 8,
        "calls_made": 12,
        "calls_connected": 9,
        "call_duration_minutes": 180,
        "meetings_scheduled": 5,
        "meetings_done": 5,
        "days_since_first_contact": 150,
        "follow_ups_total": 25,
        "demo_requested": 1,
        "budget_available": 1,
        "decision_maker_contacted": 1,
        "competitor_considering": 0,
        "employee_tenure_days": 800,
        "employee_prev_conversion_rate": 0.55,
    }

    # Test 2: COLD lead (should predict "cold" with >80% confidence)
    cold_lead = {
        "lead_source": "Cold Call",
        "industry": "Manufacturing",
        "company_size": 50,
        "website_visits": 2,
        "emails_opened": 1,
        "emails_clicked": 0,
        "calls_made": 1,
        "calls_connected": 0,
        "call_duration_minutes": 0,
        "meetings_scheduled": 0,
        "meetings_done": 0,
        "days_since_first_contact": 5,
        "follow_ups_total": 1,
        "demo_requested": 0,
        "budget_available": 0,
        "decision_maker_contacted": 0,
        "competitor_considering": 1,
        "employee_tenure_days": 45,
        "employee_prev_conversion_rate": 0.08,
    }

    import json

    print("\n" + "=" * 60)
    print("LEADPREDICT v2 — Inference Tests")
    print("=" * 60)

    result_hot = predict_single(hot_lead)
    print("\n--- HOT LEAD (should be successful) ---")
    print(json.dumps(result_hot, indent=2))

    result_cold = predict_single(cold_lead)
    print("\n--- COLD LEAD (should be cold) ---")
    print(json.dumps(result_cold, indent=2))

    # Assertions
    hot_pred = result_hot["predicted_class"]
    cold_pred = result_cold["predicted_class"]
    hot_conf = result_hot["confidence"]
    cold_conf = result_cold["confidence"]

    print(f"\n{'='*60}")
    print("VALIDATION CHECKS")
    print(f"{'='*60}")
    print(f"Hot lead  -> {hot_pred} (confidence: {hot_conf:.2%}) {'✓' if hot_pred == 'successful' and hot_conf > 0.85 else '✗ FAIL'}")
    print(f"Cold lead -> {cold_pred} (confidence: {cold_conf:.2%}) {'✓' if cold_pred == 'cold' and cold_conf > 0.80 else '✗ FAIL'}")

    # Also test old-format input (without engineered features)
    print(f"\n--- Testing old-format input (no engineered features) ---")
    old_format = {k: v for k, v in hot_lead.items()}  # Same dict, no engineered feats
    result_old = predict_single(old_format)
    print(f"Old-format hot lead -> {result_old['predicted_class']} (confidence: {result_old['confidence']:.2%})")
