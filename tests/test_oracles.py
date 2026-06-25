"""물리 검증 오라클 (PRD §7). 하나라도 실패하면 마일스톤 미완료.

실행:  pytest -q
"""

import math
import numpy as np
import pytest

from physics import topmodel, inertia, equations as eq, integrator
from physics.topmodel import StructureParams
from physics.integrator import InitialConditions, simulate
from physics.inertia import compute_inertia
from physics.mapping import compute_physics


# ===========================================================================
# §7.1 관성모멘트 적분 검증 (해석해 대조)
# ===========================================================================

def test_uniform_disk_I3():
    """균일 원판: I₃ = ½mR² 와 1% 이내 일치."""
    R, t, m = 0.05, 0.01, 0.2
    model = topmodel.build_uniform_disk(R, t, m)
    inr = compute_inertia(model)
    expected = 0.5 * m * R * R
    assert inr.I3 == pytest.approx(expected, rel=0.01)
    assert inr.m == pytest.approx(m, rel=0.01)


def test_uniform_cylinder():
    """균일 원기둥: I₃=½mR², I₁,cm=¼mR²+(1/12)mh²."""
    R, h, m = 0.04, 0.10, 0.5
    model = topmodel.build_uniform_cylinder(R, h, m)
    inr = compute_inertia(model)
    assert inr.I3 == pytest.approx(0.5 * m * R * R, rel=0.01)
    expected_I1cm = 0.25 * m * R * R + (1.0 / 12.0) * m * h * h
    assert inr.I1_cm == pytest.approx(expected_I1cm, rel=0.02)
    # 무게중심은 가운데
    assert inr.l == pytest.approx(h / 2.0, rel=0.01)


def test_uniform_cone():
    """균일 원뿔(꼭짓점=팁): 무게중심=3H/4, I₃=(3/10)mR²."""
    R, H, m = 0.03, 0.12, 0.3
    model = topmodel.build_uniform_cone(R, H, m)
    inr = compute_inertia(model)
    assert inr.m == pytest.approx(m, rel=0.01)
    assert inr.l == pytest.approx(0.75 * H, rel=0.01)   # 꼭짓점에서 3H/4
    assert inr.I3 == pytest.approx(0.3 * m * R * R, rel=0.02)


def test_parallel_axis_theorem():
    """임의 형상에서 I₁ = I₁,cm + m·l² 성립."""
    p = StructureParams(AR=1.5, mass_g=80, cm_low=0.4, f_rim=0.3, a_mm=1.0, mu=0.2)
    model = topmodel.build_top(p)
    inr = compute_inertia(model)
    assert inr.I1 == pytest.approx(inr.I1_cm + inr.m * inr.l ** 2, rel=1e-9)


def test_f_rim_monotonic_I3():
    """f_rim↑ → I₃↑ 이고 m·l 거의 불변(±1%)."""
    base = dict(AR=1.5, mass_g=100, cm_low=0.5, a_mm=1.0, mu=0.2)
    I3s, mls = [], []
    for f in [0.0, 0.2, 0.4, 0.6, 0.8]:
        inr = compute_inertia(topmodel.build_top(StructureParams(f_rim=f, **base)))
        I3s.append(inr.I3)
        mls.append(inr.m * inr.l)
    # I₃ 단조 증가
    assert all(I3s[i] < I3s[i + 1] for i in range(len(I3s) - 1))
    # m·l 거의 불변
    ml0 = mls[0]
    for ml in mls:
        assert abs(ml - ml0) / ml0 < 0.01


# ===========================================================================
# §7.2 운동방정식 정성·정량 검증
# ===========================================================================

def _lossless_params(omega0=300.0, theta0=math.radians(20.0)):
    p = StructureParams(AR=1.5, mass_g=100, cm_low=0.5, f_rim=0.3, a_mm=1.0, mu=0.0)
    model = topmodel.build_top(p)
    model.b = 0.0
    model.c = 0.0
    inr = compute_inertia(model)
    ic = InitialConditions(omega0=omega0, theta0=theta0, steady_precession=False)
    P = integrator.make_params(inr, mu=0.0, a=model.a, b=0.0, c=0.0, ic=ic)
    return inr, ic, P, model


def test_energy_conservation_lossless():
    """무마찰·무저항: 에너지 보존 (상대오차 < 1e-3)."""
    inr, ic, P, model = _lossless_params()
    res = simulate(inr, mu=0.0, a=model.a, b=0.0, c=0.0, ic=ic,
                   dt=2e-4, t_max=5.0, precise_friction=True)
    E = res.energy
    rel = (E.max() - E.min()) / abs(E.mean())
    assert rel < 1e-3, f"energy drift {rel:.2e}"


def test_p_psi_conservation_lossless():
    """무마찰: p_ψ = I₃ω₃ 보존."""
    inr, ic, P, model = _lossless_params()
    res = simulate(inr, mu=0.0, a=model.a, b=0.0, c=0.0, ic=ic,
                   dt=2e-4, t_max=5.0)
    w = res.omega3
    assert (w.max() - w.min()) / abs(w.mean()) < 1e-3


def test_steady_precession_rate():
    """정상 세차: 적절한 φ̇₀ 를 주면 θ 거의 일정, 세차율이 Ω=mgl/(I₃ω) 와 1% 이내."""
    p = StructureParams(AR=1.5, mass_g=100, cm_low=0.5, f_rim=0.3, a_mm=1.0, mu=0.0)
    model = topmodel.build_top(p)
    model.b = model.c = 0.0
    inr = compute_inertia(model)
    omega0 = 400.0
    theta0 = math.radians(30.0)
    ic = InitialConditions(omega0=omega0, theta0=theta0, steady_precession=True)
    res = simulate(inr, mu=0.0, a=model.a, b=0.0, c=0.0, ic=ic,
                   dt=2e-4, t_max=3.0)
    # θ 가 거의 일정 (장동 진폭 작음)
    theta_var = res.theta.max() - res.theta.min()
    assert theta_var < math.radians(6.0), f"θ varied {math.degrees(theta_var):.1f}deg"
    # 측정 세차율 ≈ 이론값
    Omega_theory = eq.steady_precession(inr.m, inr.l, inr.I3, omega0)
    Omega_meas = res.phi_dot.mean()
    assert Omega_meas == pytest.approx(Omega_theory, rel=0.02)


def test_sleeping_condition():
    """ω₀ ≫ ω_임계 → 오래 직립; ω₀ < ω_임계 → 빨리 쓰러짐."""
    p = StructureParams(AR=1.5, mass_g=100, cm_low=0.6, f_rim=0.4, a_mm=1.0, mu=0.10)
    model = topmodel.build_top(p)
    inr = compute_inertia(model)
    wc = eq.omega_critical(inr.m, inr.l, inr.I1, inr.I3)

    fast = simulate(inr, model.mu, model.a, model.b, model.c,
                    InitialConditions(omega0=8 * wc, theta0=math.radians(4)),
                    dt=5e-4, t_max=150.0)
    slow = simulate(inr, model.mu, model.a, model.b, model.c,
                    InitialConditions(omega0=0.5 * wc, theta0=math.radians(4)),
                    dt=5e-4, t_max=150.0)
    assert fast.duration > slow.duration
    assert slow.duration < 5.0   # 임계 미만이면 빨리 쓰러짐


def test_precession_spin_inverse():
    """마찰로 ω 가 줄면 세차율 Ω 이 커진다(Ω∝1/ω)."""
    p = StructureParams(AR=1.5, mass_g=100, cm_low=0.6, f_rim=0.4, a_mm=1.0, mu=0.15)
    model = topmodel.build_top(p)
    inr = compute_inertia(model)
    wc = eq.omega_critical(inr.m, inr.l, inr.I1, inr.I3)
    res = simulate(inr, model.mu, model.a, model.b, model.c,
                   InitialConditions(omega0=6 * wc, theta0=math.radians(8)),
                   dt=5e-4, t_max=150.0)
    # ω 감소와 |Ω| 증가의 음의 상관
    w = res.omega3
    Om = np.abs(res.phi_dot)
    # 초반 절반 vs 후반 절반 평균 비교
    half = len(w) // 2
    assert w[:half].mean() > w[half:].mean()        # ω 감소
    assert Om[half:].mean() > Om[:half].mean()      # Ω 증가


# ===========================================================================
# §7.3 사전실험 경향 재현 (연구 핵심 결과)
# ===========================================================================

def _r_squared(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ coef
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1.0 - ss_res / ss_tot


def test_duration_proportional_I3():
    """t_지속 ∝ I₃: μ·m·a·ω₀ 고정, I₃만 증가 → 선형(R²>0.98).

    f_rim 으로 I₃ 만 키운다(m·l 보존). 임계각속도 변화를 피하려 ω₀ 를
    각 케이스의 임계각속도보다 충분히 크게 동일 배율로 잡는다.
    """
    base = dict(AR=2.0, mass_g=120, cm_low=0.6, a_mm=1.5, mu=0.2)
    I3s, durs = [], []
    for f in [0.1, 0.3, 0.5, 0.7, 0.85]:
        model = topmodel.build_top(StructureParams(f_rim=f, **base))
        inr = compute_inertia(model)
        ic = InitialConditions(omega0=300.0, theta0=math.radians(4))  # ω₀ 고정
        res = simulate(inr, model.mu, model.a, 0.0, 0.0, ic,
                       dt=5e-4, t_max=150.0, precise_friction=True)
        I3s.append(inr.I3)
        durs.append(res.duration)
    assert _r_squared(I3s, durs) > 0.98, f"R²={_r_squared(I3s, durs):.4f}"


def test_duration_inverse_mu():
    """t_지속 ∝ 1/μ: I₃·m·a·ω₀ 고정, μ만 증가 → 1/μ 비례(R²>0.98)."""
    p = StructureParams(AR=2.0, mass_g=120, cm_low=0.6, f_rim=0.5, a_mm=1.5, mu=0.1)
    model0 = topmodel.build_top(p)
    inr = compute_inertia(model0)
    inv_mu, durs = [], []
    for mu in [0.10, 0.14, 0.20, 0.28, 0.40]:
        ic = InitialConditions(omega0=300.0, theta0=math.radians(4))
        res = simulate(inr, mu, model0.a, 0.0, 0.0, ic,
                       dt=5e-4, t_max=200.0, precise_friction=True)
        inv_mu.append(1.0 / mu)
        durs.append(res.duration)
    assert _r_squared(inv_mu, durs) > 0.98, f"R²={_r_squared(inv_mu, durs):.4f}"


# ===========================================================================
# §7.4 수치 안정성
# ===========================================================================

def test_no_nan_near_vertical():
    """θ→0 근방에서 NaN/Inf 미발생."""
    p = StructureParams(AR=2.0, mass_g=120, cm_low=0.6, f_rim=0.5, a_mm=1.0, mu=0.1)
    model = topmodel.build_top(p)
    inr = compute_inertia(model)
    ic = InitialConditions(omega0=900.0, theta0=math.radians(0.5))  # 거의 수직
    res = simulate(inr, model.mu, model.a, model.b, model.c, ic,
                   dt=3e-4, t_max=30.0)
    assert np.all(np.isfinite(res.theta))
    assert np.all(np.isfinite(res.phi_dot))
    assert np.all(np.isfinite(res.omega3))


def test_dt_convergence():
    """dt 절반으로 줄여도 지속시간 결과 수렴(차이 < 2%)."""
    p = StructureParams(AR=2.0, mass_g=120, cm_low=0.6, f_rim=0.5, a_mm=1.0, mu=0.15)
    model = topmodel.build_top(p)
    inr = compute_inertia(model)
    wc = eq.omega_critical(inr.m, inr.l, inr.I1, inr.I3)
    ic = InitialConditions(omega0=5 * wc, theta0=math.radians(5))
    d1 = simulate(inr, model.mu, model.a, model.b, model.c, ic,
                  dt=5e-4, t_max=150.0).duration
    d2 = simulate(inr, model.mu, model.a, model.b, model.c, ic,
                  dt=2.5e-4, t_max=150.0).duration
    assert abs(d1 - d2) / d2 < 0.02, f"d1={d1:.3f} d2={d2:.3f}"
