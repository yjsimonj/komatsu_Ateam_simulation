"""3D 팽이 GIF 애니메이션 (PRD §6.6).

Gradio 안에서 Plotly 애니메이션 재생 버튼이 불안정하므로, 서버에서 matplotlib 로
GIF 를 만들어 gr.Image 로 보여준다(자동 재생·반복, 브라우저 호환).

팽이가 초기 직립(sleeping) → 세차/장동 → ω<ω_임계 에서 기울어 쓰러짐 까지
시간 순으로 실제로 움직인다. 자전 ψ 는 실제 각속도(수백 rad/s)로 그리면 프레임
사이에서 앨리어싱되므로, ω(t) 에 비례하되 보기 좋은 속도로 스케일해 표현한다.
"""

from __future__ import annotations

import math
import tempfile
from typing import List, Tuple

import numpy as np
import matplotlib
matplotlib.use("Agg")  # 헤드리스(서버) 렌더링
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (3D 투영 등록)

from physics.topmodel import TopModel
from physics.integrator import SimResult

# 한국=우드톤, 일본=메탈톤, 하이브리드=융합 (PRD §11)
THEME = {
    "korean": dict(body="#b5651d", axis="#8b4513", rim="#d4ac0d"),
    "japanese": dict(body="#5d6d7e", axis="#2c3e50", rim="#d4ac0d"),
    "hybrid": dict(body="#c0883a", axis="#5d6d7e", rim="#d4ac0d"),
}

N_FRAMES = 44          # GIF 프레임 수
FPS = 14               # 재생 속도
VISUAL_SPIN_TURNS = 7  # 애니메이션 전체에서 보여줄 자전 바퀴 수(앨리어싱 방지)


def _surface_grid(model: TopModel, n_theta: int = 36, n_z: int = 26):
    """팽이 표면(회전체) 격자를 몸체 좌표계 (3, n_z, n_theta) 로 반환.

    표면에 자전이 보이도록 세로 줄무늬(stripe) 마스크도 함께 만든다.
    """
    H = model.H
    zz = np.linspace(0, H, n_z)
    rr = np.interp(zz, model.z, model.R)
    ang = np.linspace(0, 2 * math.pi, n_theta)
    A, Z = np.meshgrid(ang, zz)          # (n_z, n_theta)
    Rg = np.repeat(rr[:, None], n_theta, axis=1)
    X = Rg * np.cos(A)
    Y = Rg * np.sin(A)
    pts = np.stack([X, Y, Z], axis=0)    # (3, n_z, n_theta)
    stripe = (np.floor(A / (2 * math.pi) * 8) % 2)   # 자전 가시화용 줄무늬
    return pts, stripe, zz


def _rim_line(model: TopModel, n_circ: int = 48):
    if model.rim_mass <= 0:
        return None
    ang = np.linspace(0, 2 * math.pi, n_circ)
    r = model.rim_radius
    return np.vstack([r * np.cos(ang), r * np.sin(ang), np.full(n_circ, model.rim_z)])


def _euler_zxz(phi: float, theta: float, psi: float) -> np.ndarray:
    cphi, sphi = math.cos(phi), math.sin(phi)
    cth, sth = math.cos(theta), math.sin(theta)
    cps, sps = math.cos(psi), math.sin(psi)
    Rz_phi = np.array([[cphi, -sphi, 0], [sphi, cphi, 0], [0, 0, 1]])
    Rx_th = np.array([[1, 0, 0], [0, cth, -sth], [0, sth, cth]])
    Rz_psi = np.array([[cps, -sps, 0], [sps, cps, 0], [0, 0, 1]])
    return Rz_phi @ Rx_th @ Rz_psi


def make_top_gif(model: TopModel, res: SimResult, theme_key: str = "hybrid") -> str:
    """팽이가 초기부터 쓰러질 때까지 도는 GIF 를 만들어 파일 경로를 반환."""
    th = THEME.get(theme_key, THEME["hybrid"])
    H = model.H
    R_max = float(model.R_max)
    pts, stripe, zz = _surface_grid(model)
    rim = _rim_line(model)

    n = len(res.t)
    # 적응형 프레임 샘플링: sleeping 구간은 듬성, 쓰러지는(θ 급변) 구간은 촘촘하게.
    dth = np.abs(np.diff(res.theta, prepend=res.theta[0]))
    weight = 0.4 / n + 0.6 * (dth / (dth.sum() if dth.sum() > 0 else 1.0))
    cum = np.cumsum(weight); cum /= cum[-1]
    idx = np.clip(np.searchsorted(cum, np.linspace(0.0, 1.0, min(N_FRAMES, n))), 0, n - 1)

    # 보기용 자전각 ψ_vis: ω(t) 비례 누적각을 VISUAL_SPIN_TURNS 바퀴로 정규화
    w = np.abs(res.omega3)
    cumw = np.concatenate([[0.0], np.cumsum((w[:-1] + w[1:]) / 2.0 * np.diff(res.t))])
    psi_vis = cumw / cumw[-1] * (2 * math.pi * VISUAL_SPIN_TURNS) if cumw[-1] > 0 else cumw * 0

    # 축 끝 궤적(세차·장동 흔적)
    axis_tip = np.array([
        _euler_zxz(res.phi[i], res.theta[i], 0.0) @ np.array([0, 0, H]) for i in range(n)
    ])

    # 표면 두 색(줄무늬) — 자전이 보이도록
    base = np.array(_hex(th["body"]))
    dark = base * 0.72
    facecol = np.empty(stripe.shape + (3,))
    facecol[stripe == 0] = base
    facecol[stripe == 1] = dark

    shape = pts[0].shape
    flat = pts.reshape(3, -1)

    # 데이터 기반 화면 범위: 전 프레임(직립~쓰러짐)의 실제 최대 반경/높이에 맞춰
    # 여백을 최소화하고 클리핑도 방지한다.
    max_xy, max_z = 0.0, 0.0
    for i in idx:
        Rm = _euler_zxz(res.phi[i], res.theta[i], psi_vis[i])
        rp = Rm @ flat
        max_xy = max(max_xy, float(np.abs(rp[0]).max()), float(np.abs(rp[1]).max()))
        max_z = max(max_z, float(rp[2].max()))
    lim = 1.06 * max(max_xy, 1e-6)
    ztop = 1.08 * max(max_z, 1e-6)
    z_aspect = ztop / (2 * lim)

    fig = plt.figure(figsize=(4.4, 4.4), dpi=85)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0.02, top=0.94)

    # 바닥 그림자 원
    gtheta = np.linspace(0, 2 * math.pi, 40)

    def draw(frame_k: int):
        ax.clear(); ax.set_axis_off()
        i = idx[frame_k]
        R = _euler_zxz(res.phi[i], res.theta[i], psi_vis[i])

        # 바닥 면(z=0 평면) — 팽이가 서 있는 지면.
        # plot_surface 는 면 전체를 평균 깊이로 정렬하므로 큰 평면 하나면
        # 팽이를 가린다. 잘게 나눈 격자로 그려 타일별 깊이정렬이 되게 한다.
        fg = np.linspace(-lim, lim, 24)
        fx, fy = np.meshgrid(fg, fg)
        ax.plot_surface(fx, fy, np.zeros_like(fx), color="#e8e8e8",
                        alpha=0.5, linewidth=0, antialiased=False,
                        shade=False, rcount=24, ccount=24)

        rot = (R @ flat).reshape(3, *shape)
        ax.plot_surface(rot[0], rot[1], rot[2], facecolors=facecol,
                        linewidth=0, antialiased=True, shade=True,
                        rcount=shape[0], ccount=shape[1])
        # 테두리 후프
        if rim is not None:
            p = R @ rim
            ax.plot(p[0], p[1], p[2], color=th["rim"], lw=3)
        # 자전축
        axv = R @ np.array([0, 0, H * 1.05])
        ax.plot([0, axv[0]], [0, axv[1]], [0, axv[2]], color=th["axis"], lw=1.5, alpha=0.5)
        # 누적 궤적
        tip = axis_tip[:i + 1]
        if len(tip) > 2:
            ax.plot(tip[:, 0], tip[:, 1], tip[:, 2], color="#b0b0b0", lw=1.0, ls=":")
        # 접촉점 + 바닥 그림자
        ax.scatter([0], [0], [0], color="black", s=12)
        gr = 0.6 * R_max
        ax.plot(gr * np.cos(gtheta), gr * np.sin(gtheta), np.zeros_like(gtheta),
                color="#cccccc", lw=1)

        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(0, ztop)
        ax.set_box_aspect((1, 1, z_aspect))   # 등방 스케일(왜곡 없음)
        ax.view_init(elev=16, azim=35)
        ax.set_title(f"t = {res.t[i]:4.1f}s    ω = {res.omega3[i]:4.0f} rad/s    "
                     f"θ = {math.degrees(res.theta[i]):4.1f}°", fontsize=11, color="#333")

    anim = animation.FuncAnimation(fig, draw, frames=len(idx), interval=1000 / FPS)
    path = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name
    anim.save(path, writer=animation.PillowWriter(fps=FPS))
    plt.close(fig)
    return path


def _hex(h: str):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
