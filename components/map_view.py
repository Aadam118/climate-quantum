"""
components/map_view.py
------------------------
Renders the Folium map marker showing the predicted AQI at the selected
location, color-coded by severity.
"""

import folium
from streamlit_folium import st_folium


def create_aqi_map(lat: float, lon: float, aqi_value: float) -> folium.Map:
    m = folium.Map(location=[lat, lon], zoom_start=12)
    if aqi_value <= 50:
        color = "green"
    elif aqi_value <= 150:
        color = "orange"
    else:
        color = "red"
    folium.Marker(
        [lat, lon],
        popup=f"Predicted AQI: {aqi_value:.2f}",
        icon=folium.Icon(color=color, icon="info-sign"),
    ).add_to(m)
    return m


def render_map(lat: float, lon: float, aqi_value: float):
    map_fig = create_aqi_map(lat, lon, aqi_value)
    st_folium(map_fig, width=650, height=350)
