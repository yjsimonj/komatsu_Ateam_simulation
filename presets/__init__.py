"""세 팽이 프리셋 + 구조 변수 범위 제한 (PRD §6.3)."""

from .korean import KOREAN
from .japanese import JAPANESE
from .hybrid import HYBRID

PRESETS = {
    "korean": KOREAN,
    "japanese": JAPANESE,
    "hybrid": HYBRID,
}

__all__ = ["PRESETS", "KOREAN", "JAPANESE", "HYBRID"]
