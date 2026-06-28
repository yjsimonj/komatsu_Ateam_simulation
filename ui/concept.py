"""Page 3 — Concept: measuring spin rate with a laser + Fourier transform.

This page is NOT a parametric simulation — it is something you just watch. An
animation shows the real idea live: half the top is wrapped in aluminium foil
(bright reflection), the other half in black insulating tape (dark). While the
top spins, a laser is aimed at its edge and a light sensor reads the reflected
illuminance. Each revolution the sensor sees one bright + one dark half, so the
signal oscillates once per turn. A Fourier transform of that signal peaks at the
rotation frequency f, and the angular velocity is ω = 2π·f.

The animated signal here is illustrative (synthetic). The real measurement was
done with the top held in place, so its numbers aren't exact — we show the real
rig only as a photo, and use the animation to convey the method.
"""

from __future__ import annotations

import math
import os
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Wedge
import plotly.graph_objects as go

# Real experiment photo (half foil / half black tape, laser + light sensor +
# Arduino). Resolved relative to the repo root so it works on HF Spaces too.
_PHOTO_REL = "assets/experiment_setup.jpg"
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PHOTO_ABS = os.path.join(_REPO_ROOT, _PHOTO_REL)
PHOTO_PATH: str | None = _PHOTO_ABS if os.path.exists(_PHOTO_ABS) else None

ACCENT = "#b5651d"
FOIL = "#c9ccd1"
TAPE = "#1c1c1c"
LASER = "#e7000b"
SENSOR = "#2e86c1"

# Animation parameters
_N_FRAMES = 72
_FPS = 18
_TURNS = 6.0          # how many revolutions across the whole clip
_LASER_ANGLE = 0.0    # the laser hits the rightmost point of the top (angle 0)


def _reading(phase: float) -> float:
    """Arduino light-sensor reading when the foil/tape boundary is at `phase`.

    Foil covers [phase, phase+π); the laser hits angle 0. In our rig the sensor
    reads **higher when it is darker** — i.e. high while the black tape faces the
    beam, low while the foil faces it. A near-square wave once per revolution.
    """
    rel = (_LASER_ANGLE - phase) % (2 * math.pi)
    foil = rel < math.pi
    return (0.12 if foil else 0.92)   # dark (tape) → high reading


def make_concept_gif() -> str:
    """Animated GIF: the top spins, the laser hits it, and the light sensor's
    illuminance trace draws in live. Returns a temp file path."""
    # phase of the foil/tape boundary over time (constant spin, slight slow-down)
    k = np.arange(_N_FRAMES)
    frac = k / (_N_FRAMES - 1)
    phase = 2 * math.pi * _TURNS * (frac - 0.04 * frac * frac)   # gently slowing
    rng = np.random.default_rng(0)
    reading = np.array([_reading(p) for p in phase]) * 60 + 25
    reading = reading + rng.normal(0, 1.3, size=reading.shape)

    fig = plt.figure(figsize=(7.4, 3.4), dpi=92)
    ax_top = fig.add_axes([0.02, 0.06, 0.40, 0.88])   # spinning top + laser
    ax_sig = fig.add_axes([0.50, 0.16, 0.47, 0.70])   # live illuminance trace
    fig.patch.set_facecolor("white")

    def draw(i: int):
        ph = phase[i]
        val = _reading(ph)            # high when the dark tape faces the laser

        # ---- left: top-view of the spinning top + laser + sensor ----
        ax_top.clear()
        ax_top.set_xlim(-1.5, 2.6); ax_top.set_ylim(-1.7, 1.7)
        ax_top.set_aspect("equal"); ax_top.axis("off")
        deg = math.degrees(ph)
        # foil half and tape half (rotating)
        ax_top.add_patch(Wedge((0, 0), 1.0, deg, deg + 180, facecolor=FOIL, edgecolor="#999", lw=0.5))
        ax_top.add_patch(Wedge((0, 0), 1.0, deg + 180, deg + 360, facecolor=TAPE, edgecolor="#999", lw=0.5))
        # spin direction arrow
        ax_top.annotate("", xy=(0.0, 1.28), xytext=(0.62, 1.28),
                        arrowprops=dict(arrowstyle="->", color="#888", lw=1.6))
        ax_top.text(0.18, 1.42, "ω", color="#555", fontsize=12)
        # laser beam from the right hitting the rightmost point (1,0)
        ax_top.plot([2.5, 1.0], [0, 0], color=LASER, lw=2.2, zorder=5)
        ax_top.scatter([1.0], [0], s=70, color=LASER, zorder=6)
        ax_top.text(2.0, 0.22, "laser", color=LASER, fontsize=10)
        # reflected ray toward the sensor, coded by the Arduino reading
        # (thicker/stronger when the reading is high = dark tape facing the beam)
        ax_top.plot([1.0, 1.9], [0, 1.25], color=SENSOR,
                    lw=1.0 + 3.0 * val, alpha=0.25 + 0.7 * val, zorder=4)
        ax_top.scatter([1.9], [1.25], s=80, marker="s", color=SENSOR, zorder=6)
        ax_top.text(1.55, 1.42, "sensor", color=SENSOR, fontsize=10)
        # label which half faces the beam and the resulting reading
        ax_top.text(-1.45, -1.55, "tape (dark) → high" if val > 0.5 else "foil (bright) → low",
                    fontsize=10, color=("#1c1c1c" if val > 0.5 else "#a06a00"))

        # ---- right: Arduino reading trace drawing in live ----
        ax_sig.clear()
        ax_sig.plot(k[:i + 1], reading[:i + 1], color=ACCENT, lw=1.8)
        ax_sig.scatter([k[i]], [reading[i]], s=28, color=ACCENT, zorder=5)
        ax_sig.set_xlim(0, _N_FRAMES - 1); ax_sig.set_ylim(10, 100)
        ax_sig.set_title("Arduino light reading — higher when darker", fontsize=11)
        ax_sig.set_xlabel("time", fontsize=10); ax_sig.set_ylabel("reading", fontsize=10)
        ax_sig.set_xticks([]); ax_sig.grid(alpha=0.25)
        ax_sig.text(0.02, 0.93, "one dark/bright cycle = one revolution",
                    transform=ax_sig.transAxes, fontsize=9, color="#666")

    anim = animation.FuncAnimation(fig, draw, frames=_N_FRAMES, interval=1000 / _FPS)
    path = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name
    anim.save(path, writer=animation.PillowWriter(fps=_FPS))
    plt.close(fig)
    return path


def fft_figure() -> go.Figure:
    """Illustrative magnitude spectrum: the peak gives the rotation frequency f,
    and ω = 2π·f. (Synthetic, to show how the spin rate is extracted.)"""
    fs, dur, f0 = 4000, 1.0, 18.0
    t = np.arange(int(dur * fs)) / fs
    rng = np.random.default_rng(0)
    phase = 2 * math.pi * f0 * t
    # dark→high reading: spikes up when the tape faces the beam (sign flipped)
    reading = 55 - 35 * np.tanh(3.0 * np.sin(phase)) + rng.normal(0, 1.4, size=t.shape)
    x = (reading - reading.mean()) * np.hanning(len(reading))
    spec = np.abs(np.fft.rfft(x))
    freq = np.fft.rfftfreq(len(x), 1.0 / fs)
    band = freq <= 80
    freq, spec = freq[band], spec[band]
    f_peak = float(freq[np.argmax(spec)])
    omega = 2 * math.pi * f_peak

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freq, y=spec, mode="lines",
                             line=dict(color=SENSOR, width=2)))
    fig.add_vline(x=f_peak, line_dash="dash", line_color="red",
                  annotation_text=f"f = {f_peak:.1f} Hz", annotation_position="top right")
    fig.add_annotation(x=f_peak, y=spec.max(), xshift=80, yshift=-8, showarrow=False,
                       text=f"ω = 2π·f ≈ {omega:.0f} rad/s", font=dict(color="red", size=13))
    fig.update_layout(
        title="Fourier transform — peak gives the rotation frequency",
        xaxis_title="frequency [Hz]", yaxis_title="magnitude",
        height=300, plot_bgcolor="white", font=dict(size=13),
        margin=dict(l=60, r=20, t=46, b=44), showlegend=False)
    fig.update_xaxes(range=[0, 80], gridcolor="#eee")
    fig.update_yaxes(gridcolor="#eee")
    return fig


INTRO_MD = """\
A spinning top is too fast to read its rate by eye, so we make its reflection
**blink once per turn** and count the blinks with light:

- **half aluminium foil** (bright) + **half black insulating tape** (dark),
- a **laser** aimed at the edge while it spins,
- a **light sensor + Arduino** recording the reflected light.

In our rig the Arduino reading is **higher when it is darker** — so the value
spikes up each time the black tape faces the beam. Watch below: as foil and tape
sweep past the laser, the reading oscillates — one cycle per revolution. A
**Fourier transform** of that signal peaks at the rotation frequency *f*,
giving **ω = 2π·f**. Because the top keeps slowing down, we use a **short-time
FFT (STFT)** — many short windows — to track ω(t) over the whole spin.

> ⚠️ Real-experiment caveat: our measurement was taken with the top held in
> place, and the laser can't follow the top's precession well, so the numbers
> are only approximate — we read trends, not exact values.
"""
