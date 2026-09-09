"""
components/weather.py
-----------------------
Renders the live weather context banner (temperature, humidity, wind speed)
at the top of the main screen.
"""

import streamlit as st


def render_weather_banner(live_weather):
    if not live_weather:
        return
    st.markdown(
        '<p class="section-header" style="margin-top: 10px;">🌤️ LIVE WEATHER CONTEXT</p>',
        unsafe_allow_html=True,
    )
    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("Temperature", f"{live_weather['temperature']} °C")
    wc2.metric("Humidity", f"{live_weather['humidity']} %")
    wc3.metric("Wind Speed", f"{live_weather['wind_speed']} m/s")
    st.markdown("---")
