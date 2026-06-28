"""RK4 고정 스텝 적분기 + 시뮬레이션 드라이버 (PRD §6.1.2 ~ §6.1.4).

물리 dt 와 기록(샘플) dt 를 분리한다(고정 타임스텝 누산기 패턴, PRD §3.3).
쓰러짐(θ ≥ θ_fall) 시점을 회전 지속시간으로 본다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import List, Optional, Tuple

import numpy as np

from . import constants as C
from . import equations as eq
from .equations import TopParams


@dataclass
class InitialConditions:
    omega0: float                 # 초기 스핀 ω₃(0) [rad/s]
    theta0: float = math.radians(5.0)   # 초기 기울임각 [rad]
    steady_precession: bool = True      # φ̇₀ 를 정상세차값으로 줄지(아니면 0)


@dataclass
class SimResult:
    t: np.ndarray
    theta: np.ndarray             # [rad]
    omega3: np.ndarray            # [rad/s]
    phi: np.ndarray
    psi: np.ndarray
    phi_dot: np.ndarray           # 세차율 Ω(t) [rad/s]
    energy: np.ndarray
    duration: float               # 회전 지속시간 [s] (쓰러진 시각)
    upright_time: float           # 직립시간 [s] (θ < θ_upright 유지 시간)
    fell: bool                    # 시뮬 종료 전 쓰러졌는가
    omega_crit: float             # 임계 각속도 [rad/s]
    t_cross_crit: Optional[float] # ω 가 ω_임계 를 가로지른 시각
    theta_fall: float = C.THETA_FALL  # 쓰러짐 판정 각도 [rad] (몸체 접지각)


_NS = 6  # 상태 차원 [θ, θ̇, φ, ψ, ω₃, p_φ]


def rk4_step(state, P: TopParams, dt: float):
    """고전 4차 룽게-쿠타 한 스텝(스칼라 6-튜플)."""
    k1 = eq.derivatives(state, P)
    s2 = tuple(state[i] + 0.5 * dt * k1[i] for i in range(_NS))
    k2 = eq.derivatives(s2, P)
    s3 = tuple(state[i] + 0.5 * dt * k2[i] for i in range(_NS))
    k3 = eq.derivatives(s3, P)
    s4 = tuple(state[i] + dt * k3[i] for i in range(_NS))
    k4 = eq.derivatives(s4, P)
    return tuple(
        state[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i])
        for i in range(_NS)
    )


def make_params(inertia, mu: float, a: float, b: float, c: float,
                ic: InitialConditions, precise_friction: bool = True,
                gamma: float = 0.0) -> TopParams:
    """관성 결과 + 초기조건으로 TopParams 생성(p_φ 초기값 계산)."""
    theta0 = ic.theta0
    if ic.steady_precession:
        # 정상 세차값 φ̇₀ = mgl/(I₃ω₀)
        phi_dot0 = eq.steady_precession(inertia.m, inertia.l, inertia.I3, ic.omega0)
    else:
        phi_dot0 = 0.0
    st = math.sin(theta0)
    p_phi = inertia.I1 * phi_dot0 * st * st + inertia.I3 * ic.omega0 * math.cos(theta0)
    return TopParams(
        I1=inertia.I1, I3=inertia.I3, m=inertia.m, l=inertia.l,
        a=a, mu=mu, b=b, c=c, p_phi=p_phi, precise_friction=precise_friction,
        gamma=gamma,
    )


def initial_state(ic: InitialConditions, P: TopParams):
    """초기 상태벡터 [θ, θ̇, φ, ψ, ω₃, p_φ]."""
    theta0 = ic.theta0
    # θ̇₀ = 0, φ₀ = 0, ψ₀ = 0, p_φ = 초기값(make_params 에서 계산)
    return [theta0, 0.0, 0.0, 0.0, ic.omega0, P.p_phi]


def simulate(inertia, mu: float, a: float, b: float, c: float,
             ic: InitialConditions, dt: float = C.DEFAULT_PHYSICS_DT,
             t_max: float = 60.0, sample_dt: float = 0.02,
             precise_friction: bool = True, gamma: float = 0.0,
             theta_fall: float = C.THETA_FALL) -> SimResult:
    """전체 시뮬레이션. 물리 dt 로 적분하고 sample_dt 간격으로 기록."""
    P = make_params(inertia, mu, a, b, c, ic, precise_friction, gamma)

    omega_crit = eq.omega_critical(inertia.m, inertia.l, inertia.I1, inertia.I3)

    ts, thetas, omegas, phis, psis, pdots, energies = [], [], [], [], [], [], []

    def record(t: float, s: np.ndarray):
        ts.append(t)
        thetas.append(s[0])
        omegas.append(s[4])
        phis.append(s[2])
        psis.append(s[3])
        pdots.append(eq.phi_dot(s[0], s[4], s[5], P))
        energies.append(eq.energy(s, P))

    state = list(initial_state(ic, P))   # 가변 리스트로(채찍질 주입 위해)
    t = 0.0
    record(t, state)
    next_sample = sample_dt
    upright_time = 0.0
    t_cross_crit: Optional[float] = None
    prev_omega = state[4]
    fell = False

    n_max = int(math.ceil(t_max / dt))
    for _ in range(n_max):
        state = list(rk4_step(state, P, dt))
        t += dt

        theta_now = state[0]
        omega_now = state[4]

        # 직립시간 누적
        if theta_now < C.THETA_UPRIGHT:
            upright_time += dt

        # 임계 각속도 가로지름 기록(처음 한 번)
        if t_cross_crit is None and prev_omega >= omega_crit > omega_now:
            t_cross_crit = t
        prev_omega = omega_now

        # 샘플 기록
        if t >= next_sample:
            record(t, state)
            next_sample += sample_dt

        # 쓰러짐 판정
        if theta_now >= theta_fall:
            record(t, state)
            fell = True
            break

        # 수치 발산 방어
        if not (math.isfinite(theta_now) and math.isfinite(omega_now)):
            fell = True
            break

    duration = t if fell else float(t)

    return SimResult(
        t=np.array(ts), theta=np.array(thetas), omega3=np.array(omegas),
        phi=np.array(phis), psi=np.array(psis), phi_dot=np.array(pdots),
        energy=np.array(energies), duration=duration, upright_time=upright_time,
        fell=fell, omega_crit=omega_crit, t_cross_crit=t_cross_crit,
        theta_fall=theta_fall,
    )
