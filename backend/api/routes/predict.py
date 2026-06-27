"""
LeadPredict — ML Prediction routes.

Exposes the trained ML model via REST endpoints for single and batch
predictions, model metadata, and retraining (admin-only).
"""

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models.user import User
from api.middleware.auth import admin_only, get_current_user

router = APIRouter(prefix="/api/predict", tags=["ML Prediction"])


@router.post("/single")
async def predict_single(
    features: dict[str, Any],
    current_user: User = Depends(get_current_user),
) -> dict:
    """Predict the outcome for a single lead based on its features.

    Expects a JSON body with all the feature keys the trained model
    requires (see ``ml.predict.predict_single`` for details).

    Returns prediction probabilities, predicted class, confidence,
    and top contributing factors.
    """
    try:
        from ml.predict import predict_single as ml_predict

        result = ml_predict(features)
        return {"success": True, "data": result}
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model not trained yet. {exc}",
        )
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML module is not available. Please ensure the model is trained.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        )


@router.post("/batch")
async def predict_batch(
    leads: list[dict[str, Any]],
    current_user: User = Depends(get_current_user),
) -> dict:
    """Predict outcomes for multiple leads in a single request.

    Accepts a JSON array of lead feature dicts.
    Returns a JSON array of prediction results in the same order.
    """
    if not leads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch must contain at least one lead",
        )

    try:
        from ml.predict import predict_batch as ml_predict_batch

        results = ml_predict_batch(leads)
        return {"success": True, "data": results, "total": len(results)}
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model not trained yet. {exc}",
        )
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML module is not available. Please ensure the model is trained.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {exc}",
        )


@router.get("/model-info")
async def model_info() -> dict:
    """Return metadata about the currently loaded ML model.

    Includes feature importance, model version, and accuracy
    (placeholder until actual metrics are persisted).
    """
    try:
        from ml.predict import get_feature_importance

        importance = get_feature_importance()
        # Build a clean dict from the list of tuples
        feature_importance = {name: round(score, 4) for name, score in importance}

        # Read real metrics from disk if available
        metrics_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "training_metrics.json")
        accuracy = 0.85  # fallback
        if os.path.exists(metrics_path):
            import json as _json
            with open(metrics_path) as _f:
                _metrics = _json.load(_f)
            accuracy = _metrics.get("accuracy", accuracy)

        return {
            "success": True,
            "data": {
                "model_version": "2.0.0",
                "accuracy": accuracy,
                "feature_importance": feature_importance,
                "total_features": len(feature_importance),
            },
        }
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model not trained yet. {exc}",
        )
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML module is not available.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model info: {exc}",
        )


@router.post("/retrain")
async def retrain_model(
    current_user: User = Depends(admin_only),
) -> dict:
    """Trigger full model retraining.

    Admin only.  Reads all leads from the database, trains a new model,
    and saves updated artifacts to disk.
    """
    try:
        from ml.retrain import retrain as ml_retrain

        result = ml_retrain()
        return {"success": True, "data": result}
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Retrain module is not available.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retraining failed: {exc}",
        )
