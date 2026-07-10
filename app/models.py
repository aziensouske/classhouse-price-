"""
SQLAlchemy models.

Defines the `prediction_history` table used to store every prediction
made by the /predict endpoint.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    # Prediction ID
    id = Column(Integer, primary_key=True, index=True)

    # Input Features (stored individually for easy querying)
    housing_median_age = Column(Float, nullable=False)
    total_rooms = Column(Float, nullable=False)
    total_bedrooms = Column(Float, nullable=False)
    population = Column(Float, nullable=False)
    households = Column(Float, nullable=False)
    median_income = Column(Float, nullable=False)
    ocean_proximity = Column(String, nullable=False)

    # Predicted House Price
    predicted_price = Column(Float, nullable=False)

    # Prediction Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
