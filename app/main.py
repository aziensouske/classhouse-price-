"""
FastAPI backend for the House Price Prediction platform.

Endpoints
---------
GET  /                    -> Home / health check
POST /predict              -> Predict house price and store the result
GET  /predictions          -> List stored predictions (most recent first)
GET  /predictions/recent   -> Last 5 predictions (bonus)
GET  /predictions/count    -> Total number of predictions stored (bonus)
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import engine, get_db, Base
from app import models
from app.schemas import (
    HouseFeatures,
    PredictionResponse,
    PredictionRecord,
    PredictionCountResponse,
)
from app.ml_model import predict_price

# Create tables on startup if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="House Price Prediction API",
    description="Serves a trained ML model to predict California house prices "
    "and logs every prediction to a Neon PostgreSQL database.",
    version="1.0.0",
)

# Allow the Streamlit frontend (running on a different origin/host) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Home"])
def home():
    """Simple health-check / home endpoint."""
    return {
        "message": "House Price Prediction API is running.",
        "docs": "/docs",
        "predict_endpoint": "/predict",
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(features: HouseFeatures, db: Session = Depends(get_db)):
    """
    Accepts house features, runs the trained model, stores the
    prediction in prediction_history, and returns the predicted price.
    """
    try:
        predicted_price = predict_price(features.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    record = models.PredictionHistory(
        housing_median_age=features.housing_median_age,
        total_rooms=features.total_rooms,
        total_bedrooms=features.total_bedrooms,
        population=features.population,
        households=features.households,
        median_income=features.median_income,
        ocean_proximity=features.ocean_proximity.value,
        predicted_price=predicted_price,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResponse(predicted_price=predicted_price)


@app.get("/predictions", response_model=List[PredictionRecord], tags=["History"])
def get_all_predictions(db: Session = Depends(get_db)):
    """Bonus: retrieve every stored prediction, most recent first."""
    records = (
        db.query(models.PredictionHistory)
        .order_by(models.PredictionHistory.id.desc())
        .all()
    )
    return records


@app.get(
    "/predictions/recent", response_model=List[PredictionRecord], tags=["History"]
)
def get_recent_predictions(db: Session = Depends(get_db)):
    """Bonus: retrieve the last 5 predictions."""
    records = (
        db.query(models.PredictionHistory)
        .order_by(models.PredictionHistory.id.desc())
        .limit(5)
        .all()
    )
    return records


@app.get(
    "/predictions/count", response_model=PredictionCountResponse, tags=["History"]
)
def get_prediction_count(db: Session = Depends(get_db)):
    """Bonus: total number of predictions stored in the database."""
    total = db.query(func.count(models.PredictionHistory.id)).scalar()
    return PredictionCountResponse(total_predictions=total)
