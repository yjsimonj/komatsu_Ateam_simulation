"""Plotly 시각화: 실시간 그래프 + 3D 팽이 애니메이션 (PRD §6.5, §6.6).

CPU basic 환경을 고려해 시뮬레이션은 미리 계산하고(precompute), 결과를
정적 그래프 + 프레임 애니메이션으로 렌더링한다(물리/렌더 분리, PRD §3.3).
"""

from __future__ import annotations

import math
from typing import List, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from physics.topmodel import TopModel
from physics.integrator import SimResult

# 한국=우드톤, 일본=메탈톤, 하이브리드=융합 (PRD §11)
THEME = {
    "korean": dict(body="#b5651d", accent="#8b4513", grid="#e8d5b5"),
    "japanese": dict(body="#6c7a89", accent="#34495e", grid="#d6dbdf"),
    "hybrid": dict(body="#c0883a", accent="#5d6d7e", grid="#e0d3c0"),
}


# ---------------------------------------------------------------------------
# 시계열 그래프 θ(t) / ω(t) / Ω(t)  (PRD §6.5)
# ---------------------------------------------------------------------------
def time_series_figure(res: SimResult, theme_key: str = "hybrid") -> go.Figure:
    th = THEME.get(theme_key, THEME["hybrid"])
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
        subplot_titles=("기울임각 θ(t)  [deg]",
                        "자전 각속도 ω(t)  [rad/s]",
                        "세차 각속도 Ω(t) = |φ̇|  [rad/s]"),
    )
    t = res.t
    # θ(t)
    fig.add_trace(go.Scatter(x=t, y=np.degrees(res.theta), name="θ",
                             line=dict(color=th["accent"], width=3)), row=1, col=1)
    theta_fall_deg = math.degrees(res.theta_fall)
    fig.add_hline(y=theta_fall_deg, line_dash="dot", line_color="red",
                  annotation_text=f"몸체 접지 θ_쓰러짐={theta_fall_deg:.0f}°",
                  annotation_position="bottom right", row=1, col=1)

    # ω(t) + ω_임계 가로선
    fig.add_trace(go.Scatter(x=t, y=res.omega3, name="ω₃",
                             line=dict(color="#2e86c1", width=3)), row=2, col=1)
    if math.isfinite(res.omega_crit):
        fig.add_hline(y=res.omega_crit, line_dash="dash", line_color="red",
                      annotation_text="ω_임계", annotation_position="top right",
                      row=2, col=1)
    if res.t_cross_crit is not None:
        fig.add_vline(x=res.t_cross_crit, line_dash="dot", line_color="orange",
                      annotation_text="여기서부터 급격히 기울어짐",
                      row=2, col=1)

    # Ω(t)
    fig.add_trace(go.Scatter(x=t, y=np.abs(res.phi_dot), name="Ω",
                             line=dict(color="#27ae60", width=3)), row=3, col=1)

    fig.update_xaxes(title_text="시간 t [s]", row=3, col=1)
    fig.update_layout(height=620, showlegend=False, margin=dict(l=60, r=20, t=40, b=40),
                      plot_bgcolor="white", font=dict(size=14))
    fig.update_xaxes(gridcolor="#eee")
    fig.update_yaxes(gridcolor="#eee")
    return fig


# ---------------------------------------------------------------------------
# 3D 팽이 와이어프레임 (몸체 좌표계)
# ---------------------------------------------------------------------------
def _body_wireframe(model: TopModel, n_rings: int = 6, n_merid: int = 16,
                    n_circ: int = 28, n_zsamp: int = 22):
    """몸체 좌표계의 와이어프레임 선분 점들을 (xs, ys, zs) 로 반환(None 으로 선 분리)."""
    H = model.H
    R_of = lambda z: float(np.interp(z, model.z, model.R))

    xs: List[Optional[float]] = []
    ys: List[Optional[float]] = []
    zs: List[Optional[float]] = []

    # 위도 링(latitude rings)
    for zr in np.linspace(0.08 * H, 0.92 * H, n_rings):
        r = R_of(zr)
        ang = np.linspace(0, 2 * math.pi, n_circ)
        xs.extend((r * np.cos(ang)).tolist() + [None])
        ys.extend((r * np.sin(ang)).tolist() + [None])
        zs.extend([zr] * n_circ + [None])

    # 경도선(meridians)
    zz = np.linspace(0, H, n_zsamp)
    rr = np.array([R_of(z) for z in zz])
    for a in np.linspace(0, 2 * math.pi, n_merid, endpoint=False):
        xs.extend((rr * math.cos(a)).tolist() + [None])
        ys.extend((rr * math.sin(a)).tolist() + [None])
        zs.extend(zz.tolist() + [None])

    return np.array(xs, dtype=object), np.array(ys, dtype=object), np.array(zs, dtype=object)


def _rim_ring(model: TopModel, n_circ: int = 40):
    if model.rim_mass <= 0:
        return None
    ang = np.linspace(0, 2 * math.pi, n_circ)
    r = model.rim_radius
    return (r * np.cos(ang), r * np.sin(ang), np.full(n_circ, model.rim_z))


def _euler_zxz(phi: float, theta: float, psi: float) -> np.ndarray:
    """3-1-3 (ZXZ) 오일러 회전행렬 R = Rz(φ)·Rx(θ)·Rz(ψ)."""
    cphi, sphi = math.cos(phi), math.sin(phi)
    cth, sth = math.cos(theta), math.sin(theta)
    cps, sps = math.cos(psi), math.sin(psi)
    Rz_phi = np.array([[cphi, -sphi, 0], [sphi, cphi, 0], [0, 0, 1]])
    Rx_th = np.array([[1, 0, 0], [0, cth, -sth], [0, sth, cth]])
    Rz_psi = np.array([[cps, -sps, 0], [sps, cps, 0], [0, 0, 1]])
    return Rz_phi @ Rx_th @ Rz_psi


def _rotate_objarray(xs, ys, zs, R):
    """None 구분자를 보존한 채 점들을 회전."""
    out_x, out_y, out_z = [], [], []
    for x, y, z in zip(xs, ys, zs):
        if x is None:
            out_x.append(None); out_y.append(None); out_z.append(None)
            continue
        v = R @ np.array([x, y, z])
        out_x.append(v[0]); out_y.append(v[1]); out_z.append(v[2])
    return out_x, out_y, out_z


def top_3d_figure(model: TopModel, res: SimResult, theme_key: str = "hybrid",
                  n_frames: int = 40) -> go.Figure:
    """자전+세차+장동하는 3D 팽이 애니메이션 + 축끝 궤적(세차/장동 가시화)."""
    th = THEME.get(theme_key, THEME["hybrid"])
    H = model.H
    bx, by, bz = _body_wireframe(model)
    rim = _rim_ring(model)

    # 프레임 샘플 인덱스
    n = len(res.t)
    idx = np.linspace(0, n - 1, min(n_frames, n)).astype(int)

    # 축끝(symmetry axis tip at body (0,0,H)) 궤적 — 세차/장동 흔적
    axis_tip = np.array([
        _euler_zxz(res.phi[i], res.theta[i], res.psi[i]) @ np.array([0, 0, H])
        for i in range(n)
    ])

    def make_frame_data(i):
        R = _euler_zxz(res.phi[i], res.theta[i], res.psi[i])
        wx, wy, wz = _rotate_objarray(bx, by, bz, R)
        data = [go.Scatter3d(x=wx, y=wy, z=wz, mode="lines",
                             line=dict(color=th["body"], width=3), name="몸체",
                             hoverinfo="skip")]
        # 대칭축
        axis = R @ np.array([0, 0, H])
        data.append(go.Scatter3d(x=[0, axis[0]], y=[0, axis[1]], z=[0, axis[2]],
                                 mode="lines", line=dict(color=th["accent"], width=6),
                                 name="자전축", hoverinfo="skip"))
        # 테두리 후프
        if rim is not None:
            rr = np.vstack(rim)
            rrot = R @ rr
            data.append(go.Scatter3d(x=rrot[0], y=rrot[1], z=rrot[2], mode="lines",
                                     line=dict(color="#d4ac0d", width=5), name="테두리",
                                     hoverinfo="skip"))
        return data

    # 초기 프레임 + 정적 보조요소(궤적, 바닥, 피벗)
    init = make_frame_data(idx[0])
    trace_trail = go.Scatter3d(x=axis_tip[:, 0], y=axis_tip[:, 1], z=axis_tip[:, 2],
                               mode="lines", line=dict(color="#aaaaaa", width=2, dash="dot"),
                               name="축끝 궤적(세차·장동)", hoverinfo="skip")
    trace_pivot = go.Scatter3d(x=[0], y=[0], z=[0], mode="markers",
                               marker=dict(size=4, color="black"), name="접촉점",
                               hoverinfo="skip")

    lim = 1.15 * H
    frames = [go.Frame(data=make_frame_data(i), name=str(k)) for k, i in enumerate(idx)]

    fig = go.Figure(data=init + [trace_trail, trace_pivot], frames=frames)
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-lim, lim], showbackground=True, backgroundcolor="#fafafa",
                       title=""),
            yaxis=dict(range=[-lim, lim], showbackground=True, backgroundcolor="#fafafa",
                       title=""),
            zaxis=dict(range=[-0.1 * H, 1.3 * H], title="z"),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.0)),
        ),
        margin=dict(l=0, r=0, t=30, b=0), height=520, showlegend=False,
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.05, y=0.05, xanchor="left",
            buttons=[
                dict(label="▶ 재생", method="animate",
                     args=[None, dict(frame=dict(duration=60, redraw=True),
                                      fromcurrent=True, mode="immediate")]),
                dict(label="❚❚ 정지", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode="immediate")]),
            ],
        )],
    )
    return fig


# ---------------------------------------------------------------------------
# 비교 모드: 세 팽이 기본값 지속시간 막대 (PRD §6.5)
# ---------------------------------------------------------------------------
def comparison_bar(durations: dict) -> go.Figure:
    names = list(durations.keys())
    vals = [durations[k] for k in names]
    colors = [THEME.get(k, THEME["hybrid"])["body"] for k in names]
    fig = go.Figure(go.Bar(x=names, y=vals, marker_color=colors,
                           text=[f"{v:.1f}s" for v in vals], textposition="outside"))
    fig.update_layout(title="기본값 회전 지속시간 비교", yaxis_title="지속시간 [s]",
                      height=380, plot_bgcolor="white", font=dict(size=14),
                      margin=dict(l=50, r=20, t=50, b=40))
    return fig


# ---------------------------------------------------------------------------
# 검증 모드: 사전실험 경향 t∝I₃, t∝1/μ (PRD §7.3)
# ---------------------------------------------------------------------------
def trend_figure(x, y, xlabel: str, title: str) -> go.Figure:
    x = np.asarray(x, float); y = np.asarray(y, float)
    A = np.vstack([x, np.ones_like(x)]).T
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    yhat = A @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers", marker=dict(size=10, color="#2e86c1"),
                             name="시뮬레이션"))
    fig.add_trace(go.Scatter(x=x, y=yhat, mode="lines", line=dict(color="red", dash="dash"),
                             name=f"선형적합 (R²={r2:.4f})"))
    fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title="지속시간 [s]",
                      height=380, plot_bgcolor="white", font=dict(size=14),
                      margin=dict(l=60, r=20, t=50, b=45))
    return fig
