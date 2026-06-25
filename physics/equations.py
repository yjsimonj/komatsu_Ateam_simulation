"""무거운 대칭 팽이 운동방정식 + 파생 물리량 (PRD §6.1, §6.2.3, §12.1).

상태(적분 대상): s = [θ, θ̇, φ, ψ, ω₃, p_φ]
 - θ   : 연직과의 기울임각 [rad] (위쪽 연직 기준)
 - θ̇   : 기울임각 각속도 [rad/s]
 - φ   : 세차각(방위각) [rad]
 - ψ   : 자전각 [rad]
 - ω₃  : 대칭축 둘레 스핀 = ψ̇ + φ̇·cosθ [rad/s]
 - p_φ : 연직축 각운동량 L_z = I₁·φ̇·sin²θ + I₃·ω₃·cosθ

세차율 φ̇ 는 독립 상태가 아니라 p_φ 로부터 매 평가마다 유도한다(PRD §6.1.1).

⚠️ 물리 정확성 핵심: 스핀 감쇠 마찰 토크는 대칭축 ê₃ 방향이므로 그 연직(ẑ)
성분 = τ_axis·cosθ 만큼 L_z(=p_φ)도 감쇠한다. 중력 토크는 마디선(node) 둘레로
연직 성분이 없어 p_φ 를 바꾸지 않는다. 따라서
    dp_φ/dt = cosθ · τ_axis = cosθ · I₃·(dω₃/dt)
p_φ 를 상수로 두면(이전 단순화) ω₃ 감쇠 시 φ̇ 가 비물리적으로 폭증해 팽이가
조기에 기울어진다. p_φ 를 위와 같이 적분하면 무마찰 극한에서 보존(dω₃=0)되고,
감쇠 시에는 sleeping 이 오래 유지되다 ω≈ω_임계 에서 급격히 쓰러진다(PRD §6.1.3).

라그랑지안:
    L = ½·I₁(θ̇² + φ̇²·sin²θ) + ½·I₃(ψ̇ + φ̇·cosθ)² - m·g·l·cosθ
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from . import constants as C


@dataclass
class TopParams:
    """적분기에 넘기는 물리 파라미터(구조→물리 매핑 결과 + 마찰/저항)."""

    I1: float       # 팁 기준 가로축 관성
    I3: float       # 대칭축 관성
    m: float        # 질량
    l: float        # 팁→무게중심
    a: float        # 팁 곡률반경
    mu: float       # 마찰계수
    b: float        # 점성 공기저항
    c: float        # 난류 공기저항
    p_phi: float    # 초기 세차 모멘텀(발사 시 1회 설정; 이후 상태로 적분)
    precise_friction: bool = True  # True: (2/3)μmga·cosθ, False: μmga
    gamma: float = 0.0             # 피벗 수평마찰(장동 감쇠) 계수, 무손실 시 0


def phi_dot(theta: float, omega3: float, p_phi: float, P: TopParams) -> float:
    """세차율 φ̇ = (p_φ - I₃·ω₃·cosθ)/(I₁·sin²θ).  sin²θ→0 보호 (PRD §6.1.2)."""
    s = math.sin(theta)
    s2 = s * s
    if s2 < C.SIN_EPS * C.SIN_EPS:        # |sinθ|<ε 분모 클램프(부호 유지)
        s2 = C.SIN_EPS * C.SIN_EPS
    return (p_phi - P.I3 * omega3 * math.cos(theta)) / (P.I1 * s2)


def _axis_torque(theta_ct: float, omega3: float, P: TopParams) -> float:
    """대칭축 둘레 토크 τ_axis = -(2/3)μmga·cosθ - b·ω₃ - c·ω₃|ω₃|  (PRD §6.1.1)."""
    if P.precise_friction:
        fric = (2.0 / 3.0) * P.mu * P.m * C.G * P.a * theta_ct   # θ 의존 정밀형
    else:
        fric = P.mu * P.m * C.G * P.a                            # 단순 근사형
    return -fric - P.b * omega3 - P.c * omega3 * (omega3 if omega3 >= 0 else -omega3)


def derivatives(state, P: TopParams):
    """상태 s=[θ,θ̇,φ,ψ,ω₃,p_φ] 의 시간 도함수. 핫루프 성능을 위해 스칼라 튜플."""
    theta = state[0]
    theta_dot = state[1]
    omega3 = state[4]
    p_phi = state[5]

    st = math.sin(theta)
    ct = math.cos(theta)

    # 세차율 φ̇ = (p_φ - I₃·ω₃·cosθ)/(I₁·sin²θ), sin²θ→0 보호
    s2 = st * st
    if s2 < C.SIN_EPS * C.SIN_EPS:
        s2 = C.SIN_EPS * C.SIN_EPS
    pd = (p_phi - P.I3 * omega3 * ct) / (P.I1 * s2)

    # θ̈ = sinθ·(I₁·φ̇²·cosθ - I₃·ω₃·φ̇ + m·g·l)/I₁  (- 피벗 감쇠)
    theta_ddot = (st * (P.I1 * pd * pd * ct - P.I3 * omega3 * pd + P.m * C.G * P.l) / P.I1
                  - P.gamma * theta_dot)

    # ψ̇ = ω₃ - φ̇·cosθ
    psi_dot = omega3 - pd * ct

    # 스핀 감쇠 토크 → ω̇₃, 그리고 그 연직성분이 p_φ 를 감쇠
    tau_axis = _axis_torque(ct, omega3, P)
    w3d = tau_axis / P.I3
    p_phi_dot = ct * tau_axis            # dp_φ/dt = cosθ·τ_axis

    return (theta_dot, theta_ddot, pd, psi_dot, w3d, p_phi_dot)


# ---------------------------------------------------------------------------
# 보존량 / 에너지 (오라클 §7.2 검증용)
# ---------------------------------------------------------------------------

def energy(state, P: TopParams) -> float:
    """E = ½I₁(θ̇² + φ̇²sin²θ) + ½I₃ω₃² + mgl·cosθ."""
    theta, theta_dot, phi, psi, omega3, p_phi = state
    pd = phi_dot(theta, omega3, p_phi, P)
    st = math.sin(theta)
    return (0.5 * P.I1 * (theta_dot ** 2 + pd * pd * st * st)
            + 0.5 * P.I3 * omega3 ** 2
            + P.m * C.G * P.l * math.cos(theta))


def p_psi(state, P: TopParams) -> float:
    """대칭축 각운동량 p_ψ = I₃·ω₃ (무손실 극한에서 보존)."""
    return P.I3 * state[4]


def p_phi_of(state, P: TopParams) -> float:
    """연직축 각운동량 p_φ (상태로 직접 적분되는 값)."""
    return state[5]


# ---------------------------------------------------------------------------
# 파생 물리량 (패널 표시값, PRD §6.2.3 / §12.1)
# ---------------------------------------------------------------------------

def omega_critical(m: float, l: float, I1: float, I3: float) -> float:
    """임계 각속도 ω_임계 = 2·√(m·g·l·I₁) / I₃."""
    if I3 <= 0:
        return float("inf")
    return 2.0 * math.sqrt(max(m * C.G * l * I1, 0.0)) / I3


def steady_precession(m: float, l: float, I3: float, omega: float) -> float:
    """정상 세차율 Ω = m·g·l / (I₃·ω) (sinθ 소거, 기울기 무관)."""
    if I3 <= 0 or omega == 0:
        return 0.0
    return m * C.G * l / (I3 * omega)


def predicted_duration(I3: float, omega0: float, m: float, l: float,
                       a: float, mu: float, precise: bool = True) -> float:
    """예측 지속시간 t ≈ I₃·ω₀ / ((2/3)·μ·m·g·a)  (사전실험 1차 모델)."""
    coeff = (2.0 / 3.0) if precise else 1.0
    denom = coeff * mu * m * C.G * a
    if denom <= 0:
        return float("inf")
    return I3 * omega0 / denom


def stability_bundle(m: float, l: float, I1: float, I3: float) -> float:
    """변인통제용 결합량 mgl·I₁/I₃² (PRD §6.2.2 노트). ω_임계² 의 1/4 에 해당."""
    if I3 <= 0:
        return float("inf")
    return m * C.G * l * I1 / (I3 * I3)
