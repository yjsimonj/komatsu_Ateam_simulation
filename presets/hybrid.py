"""하이브리드 팽이 (제한 최소) — PRD §6.3.3.

목표 시연: 큰 I₃(편구·테두리) + 낮은 l + 저마찰 금속 팁 으로
한국/일본 기본값보다 긴 지속시간·낮은 ω_임계 달성.
"""

from .schema import Preset, Range

HYBRID = Preset(
    key="hybrid",
    name_ko="하이브리드 팽이",
    name_en="Hybrid Top",
    name_ja="ハイブリッドコマ",
    AR=Range(0.4, 4.0, 2.0, "전 범위 — 두 전통의 형태를 자유롭게 융합합니다."),
    mass_g=Range(30, 300, 100, "전 범위."),
    cm_low=Range(0.0, 1.0, 0.8, "무게중심 자유 — 낮출수록 안정에 유리합니다."),
    f_rim=Range(0.0, 0.9, 0.6, "큰 I₃ 허용 — 외곽 질량 재분배(Spin-It)."),
    mu=Range(0.03, 0.45, 0.08, "저마찰 금속 팁까지 허용."),
    a_mm=Range(0.3, 3.0, 1.0),
    omega0=Range(60, 800, 450),
    material="brass",
    drive="both",
    description_ko=("두 전통이 비워둔 영역을 탐색: 큰 I₃ + 낮은 l + 저마찰 금속 팁. "
                    "f_rim↑·μ↓·l↓ 을 시도해 기본값보다 긴 지속시간을 직접 찾아보세요."),
    boundary_msg_ko="하이브리드는 제한이 거의 없습니다 — 물리적으로 안정한 범위 한계입니다.",
)
