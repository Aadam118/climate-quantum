"""
components/prediction.py
---------------------------
Renders the "Prediction Result" column: the AQI readout, gauge chart, voice
alert trigger, map, health advisory banners, and the feature-impact chart.
This is the busiest section of the original app, pulled out into one place
so app.py stays a thin orchestrator.
"""

import plotly.graph_objects as go
import streamlit as st

from utils import get_aqi_category
from components.voice_alert import speak_announcement, build_voice_text
from components.map_view import render_map
from components.feature_impact import render_feature_impact


def render_aqi_display(aqi: float):
    """Render a large, color-coded AQI readout as custom HTML."""
    label, color, glow = get_aqi_category(aqi)
    st.markdown(
        f"""
        <div class="aqi-display" style="background: {glow};">
            <div class="aqi-label" style="color:{color};">Predicted AQI</div>
            <p class="aqi-number" style="color:{color};">{aqi:.2f}</p>
            <div class="aqi-category" style="color:{color};">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_gauge(aqi_value: float):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_value,
        title={"text": "AQI Status", "font": {"size": 18, "color": "#FFD700"}},
        gauge={
            "axis": {"range": [0, 500], "tickwidth": 1, "tickcolor": "white"},
            "bar": {"color": "rgba(255,255,255,0.9)"},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 1,
            "bordercolor": "#FFD700",
            "steps": [
                {"range": [0, 50], "color": "#00ff00"},      # Good
                {"range": [50, 100], "color": "#ffff00"},    # Moderate
                {"range": [100, 150], "color": "#ffa500"},   # Unhealthy (Sensitive)
                {"range": [150, 200], "color": "#ff0000"},   # Unhealthy
                {"range": [200, 300], "color": "#800080"},   # Very Unhealthy
                {"range": [300, 500], "color": "#800000"},   # Hazardous
            ],
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, height=250)
    st.plotly_chart(fig, use_container_width=True)


def render_prediction_result(inputs: dict, voice_run_id: int):
    """
    inputs: dict with keys result, error, latitude, longitude, live_weather,
    crop_burning_season, is_weekend, voice_enabled, predict_clicked.
    """
    st.markdown('<p class="section-header">🌫️ Prediction Result</p>', unsafe_allow_html=True)

    if inputs["error"]:
        st.error(inputs["error"])
        return

    result = inputs["result"]
    if not (result and result.get("status") == "success"):
        st.markdown(
            """
            <div class="glass-card" style="text-align:center; opacity:0.85;">
                Configure your inputs in the sidebar, then hit
                <b>“Run Quantum Inference”</b> to get a live AQI prediction.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    aqi_value = result["predicted_aqi"]
    render_aqi_display(aqi_value)
    _render_gauge(aqi_value)
    st.caption(f"📡 {result.get('message', '')}")

    # 🔊 Voice feedback — only fires right after a fresh prediction, driven
    # off `voice_run_id` so it doesn't replay on unrelated reruns (e.g.
    # dragging the Bloch sphere sliders).
    if inputs["voice_enabled"] and inputs["predict_clicked"]:
        speak_announcement(build_voice_text(aqi_value), voice_run_id)

    render_map(inputs["latitude"], inputs["longitude"], aqi_value)

    # Smart Health Advisory Alerts
    if aqi_value > 150:
        st.error(
            "🚨 **CRITICAL HEALTH ALERT:** High pollution levels detected. "
            "Local authorities should trigger emergency smog mitigation protocols."
        )
    elif aqi_value > 100:
        st.warning(
            "⚠️ **HEALTH ADVISORY:** Sensitive groups (children, elderly, "
            "asthma patients) must stay indoors."
        )
    else:
        st.success("🟢 **AIR QUALITY NORMAL:** Safe for all regular outdoor operations.")

    if inputs["live_weather"]:
        render_feature_impact(
            inputs["live_weather"], inputs["crop_burning_season"], inputs["is_weekend"], aqi_value
        )
