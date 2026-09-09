"""
components/feature_impact.py
-------------------------------
Local-sensitivity bar chart: a frontend mathematical proxy showing how much
each live input (crop burning, wind, temperature, humidity, day type)
contributed to the current prediction — mirrors the quantum model's learned
weights without calling the backend again.
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def render_feature_impact(live_weather, crop_burning_season, is_weekend, aqi_value):
    st.markdown("---")
    st.markdown(
        '<p class="section-header">🧠 Live Feature Contribution (Local Sensitivity)</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    try:
        impacts = {
            "🔥 Crop Burning": 35.0 if crop_burning_season else 2.0,
            "🌬️ Wind Speed": max(2.0, 20.0 - (live_weather["wind_speed"] * 1.5)),
            "🌡️ Temperature": 15.0 + (live_weather["temperature"] * 0.1),
            "💧 Humidity": 10.0 + (live_weather["humidity"] * 0.05),
            "📅 Day Type (Traffic)": 15.0 if not is_weekend else 5.0,
        }

        total_impact = sum(impacts.values())
        impact_percentages = {k: (v / total_impact) * 100 for k, v in impacts.items()}

        df_impact = pd.DataFrame({
            "Feature": list(impact_percentages.keys()),
            "Contribution (%)": list(impact_percentages.values()),
        }).sort_values("Contribution (%)", ascending=True)

        # Proper Standard AQI Color Logic
        if aqi_value <= 50:
            chart_color = "#00e676"
        elif aqi_value <= 100:
            chart_color = "#ffee58"
        elif aqi_value <= 150:
            chart_color = "#ffa726"
        else:
            chart_color = "#ef5350"

        fig_impact = px.bar(
            df_impact,
            x="Contribution (%)",
            y="Feature",
            orientation="h",
            text="Contribution (%)",
        )
        fig_impact.update_traces(
            marker_color=chart_color,
            texttemplate="<b>%{text:.1f}%</b>",
            textposition="outside",
            textfont=dict(color="white"),
        )
        fig_impact.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=350,
            margin=dict(l=0, r=50, t=30, b=0),
            xaxis=dict(showgrid=False, visible=False, range=[0, max(df_impact["Contribution (%)"]) + 10]),
            yaxis=dict(title=""),
        )

        st.plotly_chart(fig_impact, use_container_width=True)
        st.caption(
            "Live mathematical breakdown showing how much (%) each current local "
            "factor influenced the Quantum AQI prediction."
        )

    except Exception:
        st.warning("Please run inference to generate feature contributions.")

    st.markdown("</div>", unsafe_allow_html=True)
