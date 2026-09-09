"""
components/sidebar.py
----------------------
Renders the sidebar: location (State -> District cascading dropdown, logic
kept exactly as in the original app), season/day-type/crop-burning inputs,
the voice toggle, and the "Run Quantum Inference" button.

Returns everything app.py needs as a single dict, so app.py never has to
reach into st.session_state or re-derive these values itself.
"""

import streamlit as st

from utils import load_district_data, get_live_weather


def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown('<p class="section-header">📍 Location & Context</p>', unsafe_allow_html=True)

        district_data = load_district_data()

        # --- State -> District cascading dropdown (unchanged logic) ---
        if district_data:
            all_states = sorted(list(set([
                key.split(" - ")[0] if " - " in key else "Other"
                for key in district_data.keys()
            ])))

            selected_state = st.selectbox("Select State", all_states)

            filtered_districts = {}
            for key, coords in district_data.items():
                if key.startswith(selected_state):
                    clean_district_name = key.split(" - ")[1] if " - " in key else key
                    filtered_districts[clean_district_name] = coords

            selected_district = st.selectbox("Select District", sorted(filtered_districts.keys()))

            latitude, longitude = filtered_districts[selected_district]

            st.write(f"Selected: **{selected_district}, {selected_state}**")
            st.write(f"Coordinates: {latitude}, {longitude}")
        else:
            selected_state = selected_district = None
            latitude, longitude = 28.6139, 77.2090  # fallback if District.json is missing

        live_weather = get_live_weather(latitude, longitude)
        st.caption(f"Coordinates: {latitude:.4f} N, {longitude:.4f} E")

        st.markdown("---")

        season_name = st.selectbox(
            "Season",
            options=["summer", "winter", "monsoon", "post_monsoon"],
            format_func=lambda s: s.replace("_", " ").title(),
        )

        col_day, col_crop = st.columns(2)
        with col_day:
            is_weekend_label = st.radio("Day Type", options=["Weekday", "Weekend"], horizontal=True)
            is_weekend = 1 if is_weekend_label == "Weekend" else 0
        with col_crop:
            st.write("")
            crop_burning_season = 1 if st.toggle("🔥 Crop Burning", value=False) else 0

        voice_enabled = st.toggle("🔊 Voice Alerts", value=True, help="Speaks the AQI result aloud")

        st.markdown("---")
        predict_clicked = st.button("☁️ Run Quantum Inference", use_container_width=True, type="primary")

        st.markdown(
            """
            <div class="footer-note">
            Backend: FastAPI · Model: Hybrid QNN<br>
            PyTorch + PennyLane · 7 Qubits
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "selected_state": selected_state,
        "selected_district": selected_district,
        "latitude": latitude,
        "longitude": longitude,
        "live_weather": live_weather,
        "season_name": season_name,
        "is_weekend": is_weekend,
        "crop_burning_season": crop_burning_season,
        "voice_enabled": voice_enabled,
        "predict_clicked": predict_clicked,
    }
