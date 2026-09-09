# python -m streamlit run app.py

"""
Quantum AQI Predictor — Streamlit Frontend (orchestrator)
============================================================
A futuristic client for a FastAPI backend serving a Hybrid Quantum-Classical
Neural Network (PyTorch + PennyLane, 7-qubit variational circuit) that
predicts Air Quality Index (AQI).

This file only wires the app together — all styling lives in style.css, all
backend/helper logic lives in utils.py, and every UI piece (sidebar, weather
banner, prediction result, circuit diagram, Bloch sphere) lives under
components/.

Run with:  streamlit run app.py
Requires:  streamlit, requests, pennylane, matplotlib, plotly, numpy,
           folium, streamlit_folium, pandas
Voice feedback uses the browser's built-in Web Speech API — no extra
Python TTS dependency (e.g. gTTS) is required, and it works fully offline.
"""

import streamlit as st

from utils import load_css, call_predict_api, API_URL
from components.sidebar import render_sidebar
from components.weather import render_weather_banner
from components.mobile_ui import close_sidebar_on_mobile
from components.prediction import render_prediction_result
from components.circuit_diagram import render_circuit_section
from components.bloch_sphere import render_bloch_section

# ----------------------------------------------------------------------------
# PAGE CONFIG — must be the first Streamlit call
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Quantum AQI Predictor",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css("style.css")

# ----------------------------------------------------------------------------
# SESSION STATE — keeps the last prediction across reruns (e.g. when just
# tweaking the Bloch sphere sliders)
# ----------------------------------------------------------------------------
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None
if "voice_run_id" not in st.session_state:
    st.session_state.voice_run_id = 0

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
sidebar = render_sidebar()

# ----------------------------------------------------------------------------
# MAIN HEADER
# ----------------------------------------------------------------------------
st.markdown('<p class="quantum-title">⚛️ Quantum AQI Predictor</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="quantum-subtitle">Hybrid Quantum-Classical Neural Network · '
    "Air Quality Inference Engine</p>",
    unsafe_allow_html=True,
)
st.write("")

render_weather_banner(sidebar["live_weather"])

# ----------------------------------------------------------------------------
# RUN INFERENCE
# ----------------------------------------------------------------------------
if sidebar["predict_clicked"]:
    payload = {
        "latitude": sidebar["latitude"],
        "longitude": sidebar["longitude"],
        "is_weekend": sidebar["is_weekend"],
        "crop_burning_season": sidebar["crop_burning_season"],
        "season_name": sidebar["season_name"],
    }
    with st.spinner("Encoding features into quantum states and running the circuit…"):
        close_sidebar_on_mobile()
        result, error = call_predict_api(payload)

    st.session_state.last_result = result
    st.session_state.last_error = error
    st.session_state.voice_run_id += 1  # forces the voice component to re-fire

# ----------------------------------------------------------------------------
# TOP ROW — AQI Result + Request Summary
# ----------------------------------------------------------------------------
col_result, col_summary = st.columns([1.1, 1.4], gap="large")

with col_result:
    render_prediction_result(
        {
            "result": st.session_state.last_result,
            "error": st.session_state.last_error,
            "latitude": sidebar["latitude"],
            "longitude": sidebar["longitude"],
            "live_weather": sidebar["live_weather"],
            "crop_burning_season": sidebar["crop_burning_season"],
            "is_weekend": sidebar["is_weekend"],
            "voice_enabled": sidebar["voice_enabled"],
            "predict_clicked": sidebar["predict_clicked"],
        },
        st.session_state.voice_run_id,
    )

with col_summary:
    st.markdown('<p class="section-header">🧾 Request Payload</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.json({
        "latitude": round(sidebar["latitude"], 4),
        "longitude": round(sidebar["longitude"], 4),
        "is_weekend": sidebar["is_weekend"],
        "crop_burning_season": sidebar["crop_burning_season"],
        "season_name": sidebar["season_name"],
    })
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption(f"Target endpoint: `{API_URL}`")

st.write("")
st.markdown("---")

# ----------------------------------------------------------------------------
# BOTTOM ROW — Quantum Visualizations
# ----------------------------------------------------------------------------
col_circuit, col_bloch = st.columns([1.3, 1], gap="large")

with col_circuit:
    render_circuit_section(
        sidebar["latitude"], sidebar["longitude"], sidebar["is_weekend"], sidebar["crop_burning_season"]
    )

with col_bloch:
    render_bloch_section()

st.markdown(
    """
    <div class="footer-note">
    Built for demonstration purposes · Connects to a locally-hosted FastAPI + PennyLane backend
    </div>
    """,
    unsafe_allow_html=True,
)
