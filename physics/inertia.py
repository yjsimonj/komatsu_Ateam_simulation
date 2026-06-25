"""구조 → 물리량 적분 (PRD §6.2.1, §12.1).

팽이를 얇은 원판들로 이산화해 다음 4개 적분을 계산한다. 이 값들이
모든 물리량의 단일 출처(single source of truth)다. closed-form 가짜 공식을
쓰지 않고 적분으로 처리하여, 형상이 달라도 같은 코드로 다루고 §7 오라클에서
해석해와 대조 검증할 수 있게 한다.

    dmᵢ   = ρᵢ · π · Rᵢ² · dz
    m     = Σ dmᵢ
    z_cm  = (Σ zᵢ·dmᵢ) / m            →  l = z_cm   (팁→무게중심)
    I₃    = Σ ½ · dmᵢ · Rᵢ²                          (대칭축)
    I₁,cm = Σ dmᵢ · ( ¼·Rᵢ² + (zᵢ - z_cm)² )
    I₁    = I₁,cm + m·l²                             (평행축 정리, 팁 기준)

외곽 테두리 후프(rim)는 같은 Σ 틀에 해석 기여를 더한다:
    얇은 후프(반경 r, 질량 mr)의 대칭축 관성    = mr·r²
    후프(수평면)의 자기 지름축 관성(I₁,cm 기여)  = ½·mr·r²
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .topmodel import TopModel


@dataclass
class InertiaResult:
    m: float        # 총 질량 [kg]
    l: float        # 팁→무게중심 거리 [m] (= z_cm)
    I3: float       # 대칭축 관성모멘트 [kg·m^2]
    I1_cm: float    # 무게중심 기준 가로축 관성모멘트 [kg·m^2]
    I1: float       # 팁(접촉점) 기준 가로축 관성모멘트 [kg·m^2]


def compute_inertia(model: TopModel) -> InertiaResult:
    """TopModel → (m, l, I₃, I₁,cm, I₁). PRD §6.2.1 적분."""
    z = model.z
    R = model.R
    rho = model.rho
    dz = model.dz

    # 원판 질량 요소
    dm = rho * math.pi * R * R * dz          # dmᵢ = ρ·π·R²·dz

    m_body = float(np.sum(dm))
    # 후프 질량
    m_rim = float(model.rim_mass)
    m = m_body + m_rim

    if m <= 0.0:
        return InertiaResult(0.0, 0.0, 0.0, 0.0, 0.0)

    # 무게중심 (몸체 + 후프)
    moment_z = float(np.sum(z * dm)) + m_rim * model.rim_z
    z_cm = moment_z / m
    l = z_cm

    # 대칭축 관성 I₃ = Σ ½ dm R²  (+ 후프 mr·r²)
    I3 = float(np.sum(0.5 * dm * R * R)) + m_rim * model.rim_radius ** 2

    # 무게중심 기준 가로축 I₁,cm = Σ dm (¼R² + (z - z_cm)²)
    I1_cm_body = float(np.sum(dm * (0.25 * R * R + (z - z_cm) ** 2)))
    # 후프의 I₁,cm 기여: 지름축 ½ mr r² + 평행축 mr (z_rim - z_cm)²
    I1_cm_rim = m_rim * (0.5 * model.rim_radius ** 2 + (model.rim_z - z_cm) ** 2)
    I1_cm = I1_cm_body + I1_cm_rim

    # 평행축 정리: 팁 기준 I₁ = I₁,cm + m·l²
    I1 = I1_cm + m * l * l

    return InertiaResult(m=m, l=l, I3=I3, I1_cm=I1_cm, I1=I1)
