"""
components/bloch_sphere.py
-----------------------------
Interactive 3D Bloch sphere (Plotly) showing a single qubit state |ψ⟩,
driven by user-adjustable θ / φ sliders.
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st


@st.cache_resource(show_spinner=False)
def build_bloch_sphere(theta: float = 0.9, phi: float = 1.4):
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))

    fig = go.Figure()

    fig.add_trace(
        go.Surface(
            x=x, y=y, z=z,
            colorscale=[[0, "rgba(255,215,0,0.15)"], [1, "rgba(255,255,255,0.15)"]],
            showscale=False,
            opacity=0.35,
            contours=dict(x=dict(show=False), y=dict(show=False), z=dict(show=False)),
        )
    )

    # Axes (X, Y, Z) through the sphere
    axis_len = 1.3
    for vec, name, color in [
        ([axis_len, 0, 0], "X", "#cccccc"),
        ([0, axis_len, 0], "Y", "#cccccc"),
        ([0, 0, axis_len], "Z", "#cccccc"),
    ]:
        fig.add_trace(go.Scatter3d(
            x=[-vec[0], vec[0]], y=[-vec[1], vec[1]], z=[-vec[2], vec[2]],
            mode="lines", line=dict(color=color, width=3), showlegend=False,
        ))
        fig.add_trace(go.Scatter3d(
            x=[vec[0]], y=[vec[1]], z=[vec[2]], mode="text",
            text=[name], textfont=dict(color="#FFFFFF", size=14), showlegend=False,
        ))

    # State vector |ψ⟩ = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>
    sx = np.sin(theta) * np.cos(phi)
    sy = np.sin(theta) * np.sin(phi)
    sz = np.cos(theta)

    fig.add_trace(go.Scatter3d(
        x=[0, sx], y=[0, sy], z=[0, sz],
        mode="lines+markers",
        line=dict(color="#FFD700", width=8),
        marker=dict(size=[0, 8], color="#FFD700"),
        name="|ψ⟩ qubit state",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(visible=False, range=[-1.4, 1.4]),
            yaxis=dict(visible=False, range=[-1.4, 1.4]),
            zaxis=dict(visible=False, range=[-1.4, 1.4]),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.9)),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
        showlegend=False,
    )
    return fig


def render_bloch_section():
    st.markdown('<p class="section-header">🌐 Qubit State — Bloch Sphere</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        theta = st.slider("θ (polar)", 0.0, float(np.pi), 0.9, 0.05, key="theta_slider")
    with b_col2:
        phi = st.slider("φ (azimuthal)", 0.0, float(2 * np.pi), 1.4, 0.05, key="phi_slider")
    bloch_fig = build_bloch_sphere(theta, phi)
    st.plotly_chart(bloch_fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Drag to rotate. The gold vector represents a single qubit's state |ψ⟩.")
    st.markdown("</div>", unsafe_allow_html=True)
