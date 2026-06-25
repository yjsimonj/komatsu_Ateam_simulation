"""구조 변수 → 물리량 → 파생 패널값 전체 파이프라인 (PRD §6.2).

사용자는 구조 변수(StructureParams)를 만지고, 이 모듈이 물리량을 계산한다.
'구조가 바뀌면 I₃·I₁·l·m 이 물리적으로 옳게 변한다' 는 것이 핵심.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

from .topmodel import StructureParams, build_top, TopModel
from .inertia import compute_inertia, InertiaResult
from . import equations as eq


@dataclass
class PhysicsSummary:
    # 기본 물리량
    m: float        # [kg]
    l: float        # [m]
    I3: float       # [kg·m^2]
    I1: float       # [kg·m^2]
    I1_cm: float    # [kg·m^2]
    mu: float
    a: float        # [m]
    b: float
    c: float
    # 파생량 (초기 스핀 ω₀ 기준)
    omega_crit: float   # [rad/s]
    Omega0: float       # 정상세차율 [rad/s]
    t_pred: float       # 예측 지속시간 [s]
    bundle: float       # mgl·I₁/I₃²


def compute_physics(p: StructureParams, omega0: float,
                    precise_friction: bool = True) -> (TopModel, InertiaResult, PhysicsSummary):
    """구조 변수 + 초기 스핀 → (형상모델, 관성, 파생물리량 요약)."""
    model = build_top(p)
    inr = compute_inertia(model)

    omega_crit = eq.omega_critical(inr.m, inr.l, inr.I1, inr.I3)
    Omega0 = eq.steady_precession(inr.m, inr.l, inr.I3, omega0)
    t_pred = eq.predicted_duration(inr.I3, omega0, inr.m, inr.l, model.a,
                                   model.mu, precise_friction)
    bundle = eq.stability_bundle(inr.m, inr.l, inr.I1, inr.I3)

    summary = PhysicsSummary(
        m=inr.m, l=inr.l, I3=inr.I3, I1=inr.I1, I1_cm=inr.I1_cm,
        mu=model.mu, a=model.a, b=model.b, c=model.c,
        omega_crit=omega_crit, Omega0=Omega0, t_pred=t_pred, bundle=bundle,
    )
    return model, inr, summary
