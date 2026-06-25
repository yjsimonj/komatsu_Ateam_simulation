"""프리셋 데이터 구조 (PRD §6.3, §6.7).

각 구조 변수는 (min, max, default) 범위를 가진다. 탭(한/일/하이브리드)에 따라
범위가 다르게 제한되어, 각국 전통 팽이의 형태 특성을 강제한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class Range:
    lo: float
    hi: float
    default: float
    note: str = ""   # 범위 경계 안내(왜 제한되는지, §2.3 근거)


@dataclass
class Preset:
    key: str
    name_ko: str
    name_en: str
    name_ja: str
    AR: Range
    mass_g: Range
    cm_low: Range
    f_rim: Range
    mu: Range
    a_mm: Range
    omega0: Range          # 초기 스핀 [rad/s]
    material: str          # 기본 재질(시각/텍스처)
    drive: str             # "whip"(채찍) | "string"(줄) | "both"
    description_ko: str = ""
    boundary_msg_ko: str = ""   # 경계 도달 시 툴팁
