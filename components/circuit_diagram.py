"""
components/circuit_diagram.py
-------------------------------
Draws the mock 7-qubit variational circuit (AngleEmbedding +
BasicEntanglerLayers) that mirrors the backend model's real architecture.
Uses qml.draw_mpl (fully gate-level decomposed, level="device"/2) when
PennyLane is available; falls back to a hand-drawn matplotlib schematic
otherwise. This is a *visual mock*, not a live inference call.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from utils import N_QUBITS

try:
    import pennylane as qml
    PENNYLANE_AVAILABLE = True
except ImportError:
    PENNYLANE_AVAILABLE = False


def build_circuit_figure(dynamic_inputs, n_qubits: int = N_QUBITS):
    if PENNYLANE_AVAILABLE:
        dev = qml.device("default.qubit", wires=n_qubits)
        weight_shape = qml.BasicEntanglerLayers.shape(n_layers=2, n_wires=n_qubits)
        rng = np.random.default_rng(42)
        weights = rng.uniform(0, np.pi, size=weight_shape)

        dyn_arr = np.array(dynamic_inputs, dtype=float)
        if len(dyn_arr) < n_qubits:
            inputs = np.pad(dyn_arr, (0, n_qubits - len(dyn_arr)), "constant")
        else:
            inputs = dyn_arr[:n_qubits]

        @qml.qnode(dev)
        def circuit(inputs, weights):
            qml.AngleEmbedding(inputs, wires=range(n_qubits))
            qml.BasicEntanglerLayers(weights, wires=range(n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

        # level="device"/2 forces PennyLane to fully DECOMPOSE the high-level
        # templates down to fundamental gates (RX/RZ rotations + CNOT ring)
        # instead of drawing one solid block per template. Older PennyLane
        # versions (<0.33) don't accept a `level` kwarg, so fall back gracefully.
        try:
            fig, ax = qml.draw_mpl(
                circuit,
                style="black_white_dark",
                level=2,
                decimals=2,
                fontsize=11,
            )(inputs, weights)
        except TypeError:
            try:
                fig, ax = qml.draw_mpl(circuit, style="black_white_dark", level=2)(inputs, weights)
            except TypeError:
                fig, ax = qml.draw_mpl(circuit, style="black_white_dark")(inputs, weights)

        # Force a solid dark background so it blends into the (now solid,
        # projector-safe) glass card.
        fig.patch.set_facecolor("#050505")
        for a in fig.axes:
            a.set_facecolor("#050505")
        fig.tight_layout()
        return fig

    # ---- Fallback hand-drawn schematic if PennyLane isn't installed ----
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#050505")
    ax.set_facecolor("#050505")
    for q in range(n_qubits):
        y = n_qubits - q
        ax.hlines(y, 0, 10, color="#cccccc", linewidth=1)
        ax.text(-0.4, y, f"|q{q}⟩", color="#FFD700", fontsize=11, va="center", ha="right")
        ax.add_patch(plt.Rectangle((1.2, y - 0.25), 0.9, 0.5, color="#00c2ff", alpha=0.9))
        ax.text(1.65, y, "RX", color="#001018", fontsize=8, ha="center", va="center", weight="bold")
        ax.add_patch(plt.Rectangle((3.2, y - 0.25), 0.9, 0.5, color="#00ffb3", alpha=0.9))
        ax.text(3.65, y, "RY", color="#001018", fontsize=8, ha="center", va="center", weight="bold")
    for q in range(n_qubits - 1):
        y1, y2 = n_qubits - q, n_qubits - q - 1
        ax.plot([5.5, 5.5], [y1, y2], color="#ff5da2", linewidth=1.5)
        ax.scatter([5.5, 5.5], [y1, y2], color="#ff5da2", s=30, zorder=5)
    ax.text(5.5, n_qubits + 0.6, "Entangling Layer (CNOT ring)", color="#ff5da2", fontsize=9, ha="center")
    for q in range(n_qubits):
        y = n_qubits - q
        ax.add_patch(plt.Rectangle((7.6, y - 0.25), 0.9, 0.5, color="#ffd166", alpha=0.9))
        ax.text(8.05, y, "⟨Z⟩", color="#001018", fontsize=8, ha="center", va="center", weight="bold")
    ax.set_xlim(-1.2, 9.5)
    ax.set_ylim(0.2, n_qubits + 1.2)
    ax.axis("off")
    ax.set_title(
        "7-Qubit Variational Circuit (AngleEmbedding + BasicEntanglerLayers)",
        color="#FFFFFF", fontsize=11, pad=10,
    )
    fig.tight_layout()
    return fig


def render_circuit_section(latitude, longitude, is_weekend, crop_burning_season):
    st.markdown('<p class="section-header">🔗 Model Circuit Architecture</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    current_inputs = [latitude, longitude, float(is_weekend), float(crop_burning_season)]
    fig = build_circuit_figure(current_inputs)
    st.pyplot(fig, use_container_width=True)
    st.caption(
        "Mock visualization of the backend's variational circuit: 7 qubits, "
        "AngleEmbedding for classical-to-quantum feature encoding, followed by "
        "BasicEntanglerLayers for trainable entanglement."
    )
    st.markdown("</div>", unsafe_allow_html=True)
