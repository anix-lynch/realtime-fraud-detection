"""FastAPI endpoints for real-time fraud detection."""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import time

from .streaming_features import RealTimeFeatureEngine
from .utils.validation_utils import validate_event, sanitize_event
from .utils.logging_utils import setup_logging


app = FastAPI(title="Real-Time Fraud Detection API", version="1.0.0")
engine = RealTimeFeatureEngine()
logger = setup_logging()


class TransactionEvent(BaseModel):
    """Transaction event model."""
    user_id: str = Field(..., description="Unique user identifier")
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., ge=0, description="Transaction amount")
    timestamp: str = Field(..., description="ISO timestamp")
    merchant: Optional[str] = Field(None, description="Merchant name")
    location: Optional[str] = Field(None, description="Transaction location")
    payment_method: Optional[str] = Field(None, description="Payment method")


class FraudScoreResponse(BaseModel):
    """Fraud score response model."""
    score: float = Field(..., ge=0, le=1, description="Fraud probability score")
    features: Dict[str, Any] = Field(..., description="Feature vector")
    model_version: str = Field(..., description="Model version")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    stats = engine.state_store.get_stats()
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "engine_stats": stats
    }


@app.post("/fraud_score", response_model=FraudScoreResponse)
async def calculate_fraud_score(event: TransactionEvent, request: Request):
    """Calculate fraud score for a transaction event."""
    start_time = time.time()

    try:
        # Convert to dict and validate
        event_dict = event.dict()
        is_valid, error_msg = validate_event(event_dict)

        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid event: {error_msg}")

        # Sanitize event
        sanitized_event = sanitize_event(event_dict)

        # Process event through engine
        success = engine.process_event(sanitized_event)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process event")

        # Get updated features
        user_id = sanitized_event['user_id']
        features = engine.get_features(user_id)

        # Calculate fraud score using weighted features
        score = _calculate_fraud_score(features)

        processing_time = (time.time() - start_time) * 1000

        logger.info(
            f"Fraud score calculated for user {user_id}: "
            f"score={score:.3f}, processing_time={processing_time:.2f}ms"
        )

        return FraudScoreResponse(
            score=score,
            features=features,
            model_version="v0",
            processing_time_ms=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing fraud score request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _calculate_fraud_score(features: Dict[str, Any]) -> float:
    """Calculate fraud score using weighted feature combination."""
    # Weights for different features (tuned for demo purposes)
    weights = {
        'transaction_velocity_1h': 0.2,      # High velocity is suspicious
        'amount_zscore': 0.25,               # Unusual amounts are suspicious
        'location_anomaly': 0.3,             # Location changes are suspicious
        'time_pattern_score': 0.15,          # Unusual timing is suspicious
        'merchant_diversity': -0.05,         # More diverse merchants = less suspicious
        'payment_method_consistency': -0.05  # Consistent payment methods = less suspicious
    }

    score = 0.0

    for feature, weight in weights.items():
        value = features.get(feature, 0.0)
        score += value * weight

    # Apply sigmoid transformation to bound between 0 and 1
    import math
    score = 1 / (1 + math.exp(-score))

    return min(max(score, 0.0), 1.0)


@app.get("/features/{user_id}")
async def get_user_features(user_id: str):
    """Get current feature vector for a user."""
    try:
        features = engine.get_features(user_id)
        return {
            "user_id": user_id,
            "features": features,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error retrieving features for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
