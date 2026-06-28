"""Page 3 — Concept explanation: measuring spin rate with a laser + FFT.

This page is NOT a parametric simulation. It walks through HOW we measured a
top's angular velocity in the real experiment:

  half the top is wrapped in black insulating tape (low reflectance), the other
  half in aluminium foil (high reflectance). While the top spins, a laser is
  aimed at the side and a light sensor reads the reflected illuminance. Each
  revolution the sensor sees one bright half + one dark half, so the signal
  oscillates once per turn. A (short-time) Fourier transform of that signal has
  a peak at the rotation frequency f; the angular velocity is ω = 2π·f.

The plots below are illustrative (synthetic) so the idea is visible even before
the real measurement photo/CSV is dropped in. Replace PHOTO_PATH with the real
experiment photo when available.
"""

from __future__ import annotations

import math
import os
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Real experiment photo (half foil / half black tape, laser + light sensor +
# Arduino). Resolved relative to the repo root so it works on HF Spaces too.
_PHOTO_REL = "assets/experiment_setup.jpg"
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PHOTO_ABS = os.path.join(_REPO_ROOT, _PHOTO_REL)
PHOTO_PATH: str | None = _PHOTO_ABS if os.path.exists(_PHOTO_ABS) else None

ACCENT = "#b5651d"
FOIL = "#c9ccd1"
TAPE = "#222222"


# ---------------------------------------------------------------------------
# Synthetic illuminance signal (half foil / half black tape under a laser)
# ---------------------------------------------------------------------------
def _illuminance_signal(f0: float = 18.0, decay: float = 0.06,
                        dur: float = 1.0, fs: int = 4000, seed: int = 0):
    """Return (t, lux) for a top spinning at ~f0 Hz and slowly slowing down.

    One bright (foil) + one dark (tape) half per revolution → the reflected
    illuminance is a near-square wave at the rotation frequency f(t).
    """
    rng = np.random.default_rng(seed)
    t = np.arange(int(dur * fs)) / fs
    # instantaneous frequency drops slightly as the top slows (friction)
    f_inst = f0 * (1.0 - decay * t)
    phase = 2 * math.pi * np.cumsum(f_inst) / fs
    # smoothed square wave: foil half bright, tape half dark
    sq = np.tanh(3.0 * np.sin(phase))            # ∈[-1,1], soft edges
    lux = 55.0 + 35.0 * sq                       # baseline + contrast [lux]
    lux += rng.normal(0, 1.4, size=lux.shape)    # sensor noise
    return t, lux, float(f_inst.mean())


def illuminance_figure() -> go.Figure:
    """Raw sensor trace: reflected illuminance vs time (shows the oscillation)."""
    t, lux, _ = _illuminance_signal()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t * 1000, y=lux, mode="lines",
                             line=dict(color=ACCENT, width=1.5), name="illuminance"))
    fig.update_layout(
        title="Sensor reading — reflected illuminance vs. time",
        xaxis_title="time [ms]", yaxis_title="illuminance [lux]",
        height=300, plot_bgcolor="white", font=dict(size=13),
        margin=dict(l=60, r=20, t=46, b=44), showlegend=False)
    fig.update_xaxes(range=[0, 220], gridcolor="#eee")
    fig.update_yaxes(gridcolor="#eee")
    return fig


def fft_figure() -> go.Figure:
    """Magnitude spectrum of the illuminance signal — peak at rotation freq."""
    t, lux, f_true = _illuminance_signal()
    fs = 1.0 / (t[1] - t[0])
    x = lux - lux.mean()
    win = np.hanning(len(x))
    spec = np.abs(np.fft.rfft(x * win))
    freq = np.fft.rfftfreq(len(x), d=1.0 / fs)
    band = freq <= 80
    freq, spec = freq[band], spec[band]
    f_peak = float(freq[np.argmax(spec)])
    omega = 2 * math.pi * f_peak

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freq, y=spec, mode="lines",
                             line=dict(color="#2e86c1", width=2), name="|FFT|"))
    fig.add_vline(x=f_peak, line_dash="dash", line_color="red",
                  annotation_text=f"f = {f_peak:.1f} Hz", annotation_position="top right")
    fig.add_annotation(x=f_peak, y=spec.max(), xshift=70, yshift=-10, showarrow=False,
                       text=f"ω = 2π·f ≈ {omega:.0f} rad/s", font=dict(color="red", size=13))
    fig.update_layout(
        title="Fourier transform — peak gives the rotation frequency",
        xaxis_title="frequency [Hz]", yaxis_title="magnitude",
        height=300, plot_bgcolor="white", font=dict(size=13),
        margin=dict(l=60, r=20, t=46, b=44), showlegend=False)
    fig.update_xaxes(range=[0, 80], gridcolor="#eee")
    fig.update_yaxes(gridcolor="#eee")
    return fig


def setup_diagram() -> go.Figure:
    """Schematic top-view: laser → spinning half-foil/half-tape top → sensor."""
    fig = go.Figure()
    # top body (circle), split into a bright foil half and a dark tape half
    ang = np.linspace(-math.pi / 2, math.pi / 2, 60)
    fig.add_trace(go.Scatter(
        x=np.concatenate([[0], np.cos(ang)]), y=np.concatenate([[0], np.sin(ang)]),
        fill="toself", mode="lines", line=dict(color=FOIL),
        fillcolor=FOIL, hoverinfo="skip", name="aluminium foil"))
    fig.add_trace(go.Scatter(
        x=np.concatenate([[0], np.cos(ang + math.pi)]),
        y=np.concatenate([[0], np.sin(ang + math.pi)]),
        fill="toself", mode="lines", line=dict(color=TAPE),
        fillcolor=TAPE, hoverinfo="skip", name="black tape"))
    fig.add_annotation(x=0.45, y=0.0, text="foil", showarrow=False, font=dict(size=12, color="#333"))
    fig.add_annotation(x=-0.5, y=0.0, text="tape", showarrow=False, font=dict(size=12, color="white"))
    # spin arrow
    fig.add_annotation(x=0, y=1.18, ax=0.5, ay=1.18, xref="x", yref="y",
                       axref="x", ayref="y", showarrow=True, arrowhead=3,
                       arrowcolor="#888", text="")
    fig.add_annotation(x=0.25, y=1.32, text="ω (spin)", showarrow=False, font=dict(size=12))
    # laser in, sensor reading
    fig.add_annotation(x=-1.0, y=0.0, ax=-2.1, ay=0.0, xref="x", yref="y",
                       axref="x", ayref="y", showarrow=True, arrowhead=3,
                       arrowcolor="red", text="")
    fig.add_annotation(x=-2.15, y=0.18, text="laser", showarrow=False, font=dict(color="red", size=13))
    fig.add_annotation(x=-1.55, y=0.95, ax=-1.0, ay=0.18, xref="x", yref="y",
                       axref="x", ayref="y", showarrow=True, arrowhead=3,
                       arrowcolor="#2e86c1", text="")
    fig.add_annotation(x=-1.9, y=1.05, text="↗ light sensor", showarrow=False,
                       font=dict(color="#2e86c1", size=13))
    fig.update_xaxes(visible=False, range=[-2.6, 1.6], scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, range=[-1.4, 1.6])
    fig.update_layout(title="Measurement setup (top view)", height=320,
                      plot_bgcolor="white", margin=dict(l=10, r=10, t=46, b=10),
                      showlegend=False, font=dict(size=13))
    return fig


# ---------------------------------------------------------------------------
# Step-through explanation (Prev / Next)
# ---------------------------------------------------------------------------
STEPS = [
    ("1 · The idea",
     "We need the spin rate ω, but a spinning top is too fast to read directly. "
     "**Trick:** make the top's reflection blink once per turn, then count the blinks "
     "with light instead of with our eyes."),
    ("2 · Half foil, half tape",
     "We wrap **one half of the top in aluminium foil** (high reflectance, bright) and "
     "**the other half in black insulating tape** (low reflectance, dark). "
     "Now each full revolution shows the sensor exactly one bright half and one dark half."),
    ("3 · Laser + light sensor + Arduino",
     "While the top spins we aim a **laser** at its side and point a **light sensor** "
     "at the reflection, logged by an **Arduino**. As foil and tape alternate past the "
     "beam, the measured **illuminance oscillates** — one bright/dark cycle per revolution. "
     "(See the real rig in the photo on the left.)"),
    ("4 · The raw signal",
     "The sensor trace is a near-**square wave**: high while the foil faces the laser, "
     "low while the tape does. Its period **T** is one revolution, so the rotation "
     "frequency is f = 1/T. But noise and a slowly changing T make it hard to read T by eye."),
    ("5 · Fourier transform → ω",
     "We take a **(short-time) Fourier transform** of the illuminance signal. "
     "The spectrum has a clear **peak at the rotation frequency f**. "
     "The angular velocity is then **ω = 2π·f**. "
     "Doing this over short windows tracks how ω decays as the top slows down."),
]


def step_md(i: int) -> str:
    i = max(0, min(i, len(STEPS) - 1))
    title, body = STEPS[i]
    dots = " ".join("●" if k == i else "○" for k in range(len(STEPS)))
    return f"### {title}\n\n{body}\n\n<sub>{dots}  ({i+1}/{len(STEPS)})</sub>"
