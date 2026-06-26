"""팽이 형상 파라미터화: 구조 변수 → 반경 프로파일 R(z) / 밀도 ρ(z) (PRD §6.2.1).

팽이를 회전체(solid of revolution)로 보고 N개의 얇은 원판으로 이산화한다.
몸체는 회전 타원체(spheroid)로 모델링한다 — 이렇게 하면 종횡비 AR 하나로
편장(prolate, 길쭉, 한국형)과 편구(oblate, 납작, 일본형)를 자연스럽게 표현할 수 있다.

Spin-It(2014) 식 내부 질량 재분배(f_rim)는 몸체 질량의 일부를 외곽 테두리
'후프(hoop)'로 옮겨 m·l 은 거의 보존한 채 I₃ 만 키운다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import numpy as np

from . import constants as C

# 몸체 기준 부피 [m^3]. AR 이 바뀌어도 이 부피를 보존하며 형상만 바꾼다(PRD §6.2.2).
# 약 3cm 반경 / 5cm 높이 급의 현실적인 팽이 크기가 나오도록 잡았다.
REFERENCE_VOLUME = 3.0e-5  # 30 cm^3

# 무게중심 하강 바이어스 최대 계수(쇠심 효과). cm_low=1 일 때 하부 밀도 가중치.
CM_BIAS_MAX = 5.0

# 공기저항 계수 스케일링(현상학적; 마찰보다 부차적이도록 작게, PRD §6.1.1).
AIR_VISC = 4.0e-4   # b = AIR_VISC * frontal_area
AIR_TURB = 4.0e-4   # c = AIR_TURB * frontal_area * R_max

# 이산화 원판 개수
N_DISKS = 400


@dataclass
class StructureParams:
    """사이드바 구조 변수(PRD §6.2.2). 사용자가 직접 만지는 값들."""

    AR: float = 1.2          # 종횡비 = 지름/높이 (>1 편구/납작, <1 편장/길쭉)
    mass_g: float = 60.0     # 총 질량 [g]
    cm_low: float = 0.6      # 무게중심 하강 정도 ∈[0,1] (쇠심, l↓)
    f_rim: float = 0.1       # 테두리 질량 비율 ∈[0,1)
    a_mm: float = 1.5        # 팁 곡률반경 [mm]
    mu: float = 0.30         # 팁-바닥 마찰계수
    material: str = "wood"   # 시각/텍스처용 재질 키


@dataclass
class TopModel:
    """이산화된 팽이. inertia.compute_inertia 의 입력이 되는 단일 출처."""

    z: np.ndarray        # 원판 중심 높이 [m] (팁 z=0 부터)
    dz: float            # 원판 두께 [m]
    R: np.ndarray        # 각 원판 반경 [m]
    rho: np.ndarray      # 각 원판 밀도 [kg/m^3]
    H: float             # 전체 높이 [m]
    R_max: float         # 최대 반경 [m]
    a: float             # 팁 곡률반경 [m]
    mu: float            # 마찰계수
    b: float             # 점성 공기저항 계수
    c: float             # 난류 공기저항 계수
    material: str = "wood"
    # 외곽 테두리 후프(없으면 None)
    rim_mass: float = 0.0
    rim_radius: float = 0.0
    rim_z: float = 0.0


def _top_profile(H: float, R_max: float, z: np.ndarray) -> np.ndarray:
    """팽이 실루엣 반경 R(z).

    아래(z=0)는 뾰족한 팁, 하부에서 빠르게 벌어져 최대 반경(belly)을 이루고,
    위로 갈수록 좁아지는 전형적인 팽이/말뚝 모양. 종횡비 AR 은 호출부에서 H, R_max
    비율로 이미 반영되므로(편장↔편구), 여기서는 정규화된 실루엣만 만든다.
    """
    s = np.clip(z / H, 0.0, 1.0)
    # 팽이 실루엣: 아래(s=0) 뾰족한 팁 → 위로 갈수록 굵어져 상부(belly)가 가장 넓고
    # 맨 위는 짧게 좁아지는 작은 꼭지(stem). belly 가 위쪽(s≈0.78)에 오도록.
    g = np.power(s, 0.62) * np.power(1.0 - s, 0.16)
    gmax = g.max() if g.size else 1.0
    return R_max * (g / gmax if gmax > 0 else g)


def build_top(p: StructureParams) -> TopModel:
    """구조 변수 → 이산화 TopModel. 부피 보존, 목표 질량/무게중심에 맞춰 밀도 조정."""
    AR = max(p.AR, 1e-3)
    m_target = p.mass_g / 1000.0           # g → kg
    a = p.a_mm / 1000.0                    # mm → m

    # --- 부피 보존하에 AR 로 H, R_max 결정 -------------------------------
    # 회전타원체 부피 V = (2/3)·π·R_max²·H, 그리고 AR = 2·R_max / H.
    # ⟹ R_max = AR·H/2 ⟹ V = (π/6)·AR²·H³ ⟹ H = (6V/(π·AR²))^(1/3)
    H = (6.0 * REFERENCE_VOLUME / (math.pi * AR * AR)) ** (1.0 / 3.0)
    R_max = AR * H / 2.0

    # --- 원판 이산화 --------------------------------------------------
    dz = H / N_DISKS
    z = (np.arange(N_DISKS) + 0.5) * dz    # 원판 중심
    R = _top_profile(H, R_max, z)

    # --- 밀도: 하부 가중(쇠심)으로 무게중심 하강, 이후 목표 질량에 맞춰 스케일 ---
    k = p.cm_low * CM_BIAS_MAX
    rho_shape = 1.0 + k * (1.0 - z / H)    # 아래(z작음)일수록 큼
    # 몸체 부피 적분
    disk_vol = math.pi * R * R * dz
    body_vol = float(np.sum(disk_vol))
    # f_rim 비율은 후프로 빠지므로 몸체 목표 질량은 (1-f_rim)·m_target
    body_mass_target = (1.0 - p.f_rim) * m_target
    # rho = rho0 * rho_shape, rho0 를 body_mass_target 에 맞춤
    denom = float(np.sum(rho_shape * disk_vol))
    rho0 = body_mass_target / denom if denom > 0 else 0.0
    rho = rho0 * rho_shape

    # --- 외곽 테두리 후프(Spin-It): 무게중심 z 에 배치해 l 불변, I₃만 증가 ---
    body_mass = float(np.sum(rho * disk_vol))
    z_cm_body = float(np.sum(z * rho * disk_vol) / body_mass) if body_mass > 0 else H / 2.0
    rim_mass = p.f_rim * m_target
    rim_radius = R_max
    rim_z = z_cm_body  # 후프를 몸체 무게중심 높이에 두어 전체 무게중심을 보존

    # --- 공기저항 계수(형상 비례, 현상학적) ----------------------------
    frontal_area = math.pi * R_max * R_max
    b = AIR_VISC * frontal_area
    c = AIR_TURB * frontal_area * R_max

    return TopModel(
        z=z, dz=dz, R=R, rho=rho, H=H, R_max=R_max,
        a=a, mu=p.mu, b=b, c=c, material=p.material,
        rim_mass=rim_mass, rim_radius=rim_radius, rim_z=rim_z,
    )


def fall_angle(model: TopModel) -> float:
    """팽이 몸체의 '가장 바깥 면'이 바닥에 처음 닿는 기울임각 θ_fall [rad].

    팁(피벗)을 원점, 대칭축에서 반경 r·축높이 z 인 표면점은 기울임각 θ 에서
    다운힐 쪽 바닥높이가  z·cosθ − r·sinθ.  이 값이 0 이 되는
        θ = atan(z / r)
    에서 그 점이 바닥(피벗면)에 닿는다. 팽이가 기울 때 실제로 바닥을 처음
    때리는 곳은 가장 바깥쪽(최대 반경 belly)이므로 r=R_max 인 점을 기준으로
    한다. 뾰족한 팁 부근의 얇은 살(R→0)은 z/r→0 이라 비현실적으로 작은 각을
    주므로 접지 기준에서 제외한다(피벗은 팁 한 점으로 본다). 외곽 테두리
    후프가 있으면 그쪽이 먼저 닿을 수 있어 함께 비교한다.
    """
    R_max = float(model.R_max)
    if R_max <= 0:
        return math.pi / 2.0
    # 최대 반경(belly) 위치
    i_belly = int(np.argmax(model.R))
    theta = math.atan(float(model.z[i_belly]) / R_max)
    # 테두리 후프(반경 = R_max)도 후보
    if model.rim_mass > 0 and model.rim_radius > 1e-9:
        theta = min(theta, math.atan(model.rim_z / model.rim_radius))
    return theta


def build_uniform_disk(R: float, thickness: float, mass: float, n: int = 400) -> TopModel:
    """검증용: 균일 원판 (오라클 §7.1)."""
    dz = thickness / n
    z = (np.arange(n) + 0.5) * dz
    Rarr = np.full(n, R)
    vol = math.pi * R * R * thickness
    rho = np.full(n, mass / vol)
    return TopModel(z=z, dz=dz, R=Rarr, rho=rho, H=thickness, R_max=R,
                    a=0.001, mu=0.0, b=0.0, c=0.0)


def build_uniform_cylinder(R: float, height: float, mass: float, n: int = 400) -> TopModel:
    """검증용: 균일 원기둥 (오라클 §7.1)."""
    return build_uniform_disk(R, height, mass, n)


def build_uniform_cone(R: float, height: float, mass: float, n: int = 800) -> TopModel:
    """검증용: 균일 원뿔. 꼭짓점(=팁)이 z=0, 바닥 반경 R 이 z=H (오라클 §7.1)."""
    dz = height / n
    z = (np.arange(n) + 0.5) * dz
    Rarr = R * (z / height)                 # 선형으로 벌어짐, 꼭짓점에서 0
    vol = math.pi * R * R * height / 3.0
    rho = np.full(n, mass / vol)
    return TopModel(z=z, dz=dz, R=Rarr, rho=rho, H=height, R_max=R,
                    a=0.001, mu=0.0, b=0.0, c=0.0)
