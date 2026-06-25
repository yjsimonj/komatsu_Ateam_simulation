"""일본 코마/베이고마 (편구·금속·저마찰·줄 구동) — PRD §6.3.2."""

from .schema import Preset, Range

JAPANESE = Preset(
    key="japanese",
    name_ko="일본 코마",
    name_en="Japanese Koma",
    name_ja="日本のこま",
    # 종횡비 1.5~4.0 (납작·넓음, 편구, 원반형)
    AR=Range(1.5, 4.0, 2.5, "일본 코마/베이고마는 납작한 편구(oblate) 원반형입니다."),
    # 금속(주철) → 고밀도 60~250 g
    mass_g=Range(60, 250, 120, "주철 등 금속 재질이라 무겁습니다."),
    cm_low=Range(0.4, 1.0, 0.7, "무게중심을 낮게 형성합니다."),
    # 외곽 집중 → I₃ 큼 0.3~0.8
    f_rim=Range(0.3, 0.8, 0.55, "질량이 외곽 테두리에 모여 I₃ 가 큽니다(편구)."),
    # 쇠팁, 저마찰 0.05~0.20
    mu=Range(0.05, 0.20, 0.10, "쇠팁 계열로 저마찰·장시간 회전을 지향합니다."),
    a_mm=Range(0.3, 2.0, 1.0),
    omega0=Range(200, 700, 420),   # 고 ω₀, 단발
    material="cast_iron",
    drive="string",
    description_ko=("납작하고 넓은 금속 원반형. 외곽에 질량이 집중되어 I₃ 가 크고, "
                    "줄을 감아 한 번에 고속을 부여합니다(단발)."),
    boundary_msg_ko="이 값은 일본 코마/베이고마의 형태 범위 한계입니다.",
)
