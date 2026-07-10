"""
Loads the trained RandomForestRegressor model and the LabelEncoder used
for the `ocean_proximity` feature. Both are loaded once at import time
so every request reuses the same in-memory objects instead of hitting
disk repeatedly.
"""

import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "ml", "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# Order matters: must match the column order the model was trained on.
FEATURE_ORDER = [
    "housing_median_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "median_income",
    "ocean_proximity",
]


def predict_price(features: dict) -> float:
    """
    Takes a dict of raw (human-readable) feature values, encodes
    ocean_proximity, and returns the predicted house price as a float.
    """
    encoded_ocean = label_encoder.transform([features["ocean_proximity"]])[0]

    input_df = pd.DataFrame(
        [
            {
                "housing_median_age": features["housing_median_age"],
                "total_rooms": features["total_rooms"],
                "total_bedrooms": features["total_bedrooms"],
                "population": features["population"],
                "households": features["households"],
                "median_income": features["median_income"],
                "ocean_proximity": encoded_ocean,
            }
        ],
        columns=FEATURE_ORDER,
    )

    prediction = model.predict(input_df)[0]
    return float(prediction)
