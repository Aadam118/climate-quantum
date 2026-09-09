"""
utils.py
--------
Shared constants, backend API calls, and small helper functions used across
the Quantum AQI Predictor app. Nothing UI-specific lives here — that's what
components/ is for.
"""

import json
import requests
import streamlit as st

# ----------------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------------
# API_URL = "http://127.0.0.1:8000/predict_aqi"   # local FastAPI backend
API_URL = "https://qai-climate-analysis.onrender.com/predict_aqi"
N_QUBITS = 7
DISTRICT_JSON_PATH = "District.json"


# ----------------------------------------------------------------------------
# STYLING
# ----------------------------------------------------------------------------
def load_css(path: str = "style.css"):
    """Inject the external stylesheet into the Streamlit app."""
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# WEATHER
# ----------------------------------------------------------------------------
def get_live_weather(lat: float, lon: float):
    """Fetch live weather (temp, humidity, wind speed) from OpenWeather.
    Returns a dict, or None on failure (and shows a sidebar error)."""
    api_key = st.secrets["OPENWEATHER_API_KEY"]
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    )
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if response.status_code == 200:
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
            }
        st.sidebar.error(f"Weather API Error: {data.get('message', 'Unknown Error')}")
        return None
    except Exception as e:
        st.sidebar.error(f"Failed to fetch weather: {e}")
        return None


# ----------------------------------------------------------------------------
# DISTRICT / STATE DATA  (cascading dropdown source — logic unchanged)
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_district_data(path: str = DISTRICT_JSON_PATH) -> dict:
    """Load the State -> District -> (lat, lon) lookup table."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        st.error("District.json file not found!")
        return {}


# ----------------------------------------------------------------------------
# AQI CATEGORY
# ----------------------------------------------------------------------------
def get_aqi_category(aqi: float):
    """Map a numeric AQI value to (label, color, glow-color) per standard bands."""
    if aqi <= 50:
        return "Good", "#00e676", "rgba(0, 230, 118, 0.35)"
    elif aqi <= 100:
        return "Moderate", "#ffee58", "rgba(255, 238, 88, 0.35)"
    elif aqi <= 150:
        return "Unhealthy (Sensitive)", "#ffa726", "rgba(255, 167, 38, 0.35)"
    elif aqi <= 200:
        return "Unhealthy", "#ef5350", "rgba(239, 83, 80, 0.4)"
    elif aqi <= 300:
        return "Very Unhealthy", "#ab47bc", "rgba(171, 71, 188, 0.4)"
    else:
        return "Hazardous", "#8d0000", "rgba(141, 0, 0, 0.45)"


# ----------------------------------------------------------------------------
# BACKEND PREDICTION CALL
# ----------------------------------------------------------------------------
def call_predict_api(payload: dict, timeout: float = 120.0):
    """
    Call the FastAPI backend. Returns (result_dict_or_None, error_message_or_None).
    Handles connection failure, timeouts, and bad HTTP status codes gracefully.
    """
    try:
        response = requests.post(API_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, (
            "🔌 **Can't reach the backend.** The FastAPI server doesn't seem to be "
            f"running at `{API_URL}`. Start it locally (e.g. `uvicorn main:app --reload`) "
            "and try again."
        )
    except requests.exceptions.Timeout:
        return None, "⏱️ The backend took too long to respond. Please try again."
    except requests.exceptions.HTTPError as e:
        return None, f"⚠️ Backend returned an error: `{e}`"
    except requests.exceptions.RequestException as e:
        return None, f"⚠️ Unexpected request error: `{e}`"
    except ValueError:
        return None, "⚠️ Backend returned a response that wasn't valid JSON."
