import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# URL of the deployed FastAPI backend (set this in a .env file locally,
# or as an environment variable on Render for the frontend service).
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.title("🏠 House Price Prediction")
st.write("Enter the house details below.")

OCEAN_PROXIMITY_OPTIONS = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]

# ---- User Inputs ----
housing_median_age = st.number_input("Housing Median Age", value=25)
total_rooms = st.number_input("Total Rooms", value=5)
total_bedrooms = st.number_input("Total Bedrooms", value=5)
population = st.number_input("Population", value=1200)
households = st.number_input("Households", value=5)
median_income = st.number_input("Median Income", value=4.5)
ocean_proximity = st.selectbox("Ocean Proximity", OCEAN_PROXIMITY_OPTIONS)

# ---- Prediction ----
if st.button("Predict House Price"):
    payload = {
        "housing_median_age": housing_median_age,
        "total_rooms": total_rooms,
        "total_bedrooms": total_bedrooms,
        "population": population,
        "households": households,
        "median_income": median_income,
        "ocean_proximity": ocean_proximity,
    }

    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=15)
        response.raise_for_status()
        prediction = response.json()["predicted_price"]
        st.success(f"Estimated House Price : ${prediction:,.2f}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the prediction API: {e}")

st.divider()

# ---- Bonus: show last 5 predictions from the backend ----
if st.checkbox("Show last 5 predictions"):
    try:
        history_response = requests.get(f"{API_URL}/predictions/recent", timeout=15)
        history_response.raise_for_status()
        history = history_response.json()

        if history:
            st.table(
                [
                    {
                        "Predicted Price": f"${h['predicted_price']:,.2f}",
                        "Ocean Proximity": h["ocean_proximity"],
                        "Median Income": h["median_income"],
                        "Timestamp": h["created_at"],
                    }
                    for h in history
                ]
            )
        else:
            st.info("No predictions stored yet.")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the prediction API: {e}")
