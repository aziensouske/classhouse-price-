"""
Pydantic schemas used for request validation and response serialization.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class OceanProximity(str, Enum):
    """Valid categories, taken directly from the trained LabelEncoder."""
    LESS_THAN_1H_OCEAN = "<1H OCEAN"
    INLAND = "INLAND"
    ISLAND = "ISLAND"
    NEAR_BAY = "NEAR BAY"
    NEAR_OCEAN = "NEAR OCEAN"


class HouseFeatures(BaseModel):
    """Request body for POST /predict"""

    housing_median_age: float = Field(..., ge=0, le=100, examples=[25])
    total_rooms: float = Field(..., gt=0, examples=[5])
    total_bedrooms: float = Field(..., gt=0, examples=[5])
    population: float = Field(..., gt=0, examples=[1200])
    households: float = Field(..., gt=0, examples=[5])
    median_income: float = Field(..., gt=0, examples=[4.5])
    ocean_proximity: OceanProximity = Field(..., examples=["NEAR BAY"])


class PredictionResponse(BaseModel):
    """Response returned by POST /predict"""

    predicted_price: float
    message: str = "Prediction generated successfully"


class PredictionRecord(BaseModel):
    """Response shape for a stored prediction (used in history endpoints)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: str
    predicted_price: float
    created_at: datetime


class PredictionCountResponse(BaseModel):
    total_predictions: int
