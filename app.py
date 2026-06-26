"""한·일 팽이 회전 안정성 — 물리 시뮬레이션 웹앱 (PRD 구현).

HuggingFace Spaces / Gradio / CPU basic 환경용. PRD 의 React/Vite 스택을 Gradio 로
이식했으며, 물리 엔진(physics/)·검증 오라클(tests/)은 PRD §6.1·§6.2·§7 을 그대로 따른다.

페이지 1: 연구 소개(Research)   페이지 2: 물리 시뮬레이션(Simulation)
"""

from __future__ import annotations

import math
import gradio as gr

from physics.topmodel import StructureParams
from physics.mapping import compute_physics
from physics.integrator import InitialConditions, simulate
from physics import constants as C
from presets import PRESETS
from ui import plots
from ui.anim import make_top_gif
from ui.research import RESEARCH

LATEX = [
    {"left": "$$", "right": "$$", "display": True},
    {"left": "$", "right": "$", "display": False},
]

# 시뮬레이션 적분 설정(CPU basic 고려: dt=5e-4, 화면 샘플 20ms)
SIM_DT = C.DEFAULT_PHYSICS_DT
SIM_SAMPLE_DT = 0.02
SIM_TMAX = 150.0
# 앱 표시용 피벗 감쇠(장동이 무한 지속되지 않도록 아주 작게, PRD §6.1.1)
PIVOT_GAMMA = 0.02


# ---------------------------------------------------------------------------
# 헬퍼: 입력 → StructureParams / 물리 계산
# ---------------------------------------------------------------------------
def _structure(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm):
    mat = PRESETS[preset_key].material
    return StructureParams(AR=AR, mass_g=mass_g, cm_low=cm_low, f_rim=f_rim,
                           a_mm=a_mm, mu=mu, material=mat)


def _fmt(v, unit="", nd=3):
    if v is None or not math.isfinite(v):
        return "—"
    return f"{v:.{nd}g} {unit}".strip()


def _arrow(new, old):
    if old is None or not math.isfinite(old) or not math.isfinite(new):
        return ""
    if new > old * 1.0005:
        return " 🔺"
    if new < old * 0.9995:
        return " 🔻"
    return ""


def panel_markdown(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0,
                   precise, prev):
    """파생 물리량 패널(PRD §6.5). prev=이전 summary dict 로 증감 화살표."""
    p = _structure(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm)
    model, inr, s = compute_physics(p, omega0, precise_friction=precise)

    def A(name, val):
        return _arrow(val, (prev or {}).get(name))

    rpm = s.omega_crit * 60 / (2 * math.pi) if math.isfinite(s.omega_crit) else float("inf")
    md = f"""
#### 물리량
| | |
|--|--|
| 질량 m | **{_fmt(s.m*1000,'g',3)}**{A('m',s.m)} |
| 무게중심 l | **{_fmt(s.l*1000,'mm',3)}**{A('l',s.l)} |
| 회전관성 I₃ | **{_fmt(s.I3*1e7,'g·cm²',3)}**{A('I3',s.I3)} |
| 가로관성 I₁ | {_fmt(s.I1*1e7,'g·cm²',3)}{A('I1',s.I1)} |
| 마찰 μ | {_fmt(s.mu,'',2)} |

#### 안정성
| | |
|--|--|
| 임계 각속도 ω_crit | **{_fmt(s.omega_crit,'rad/s',3)}**{A('wc',s.omega_crit)} |
| | <sub>{rpm:.0f} rpm</sub> |
| 세차율 Ω₀ | {_fmt(s.Omega0,'rad/s',3)} |
| 예측 지속시간 | **{_fmt(s.t_pred,'s',3)}**{A('t',s.t_pred)} |

<sub>🔺/🔻 = 직전 대비 증감 · ω₀={omega0:.0f} rad/s 기준</sub>
"""
    new_prev = dict(m=s.m, l=s.l, I3=s.I3, I1=s.I1, wc=s.omega_crit, t=s.t_pred)
    return md, new_prev


# ---------------------------------------------------------------------------
# 시뮬레이션 실행 → 그래프/3D/요약
# ---------------------------------------------------------------------------
def launch(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, theta0_deg,
           precise, steady, whip_count, whip_delta):
    p = _structure(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm)
    model, inr, s = compute_physics(p, omega0, precise_friction=precise)

    drive = PRESETS[preset_key].drive
    # 줄(단발 고속)에서는 채찍질 비활성
    wc = int(whip_count) if drive in ("whip", "both") else 0
    ic = InitialConditions(omega0=omega0, theta0=math.radians(theta0_deg),
                           steady_precession=steady,
                           whip_count=wc, whip_delta=whip_delta)
    res = simulate(inr, model.mu, model.a, model.b, model.c, ic,
                   dt=SIM_DT, t_max=SIM_TMAX, sample_dt=SIM_SAMPLE_DT,
                   precise_friction=precise, gamma=PIVOT_GAMMA)

    ts_fig = plots.time_series_figure(res, preset_key)
    gif_path = make_top_gif(model, res, preset_key)   # 자동 재생 GIF

    status = "쓰러짐 ✅" if res.fell else f"{SIM_TMAX:.0f}s 동안 직립 유지"
    cross = f"{res.t_cross_crit:.2f} s" if res.t_cross_crit is not None else "—"
    summary = f"""
### 결과 요약
- **회전 지속시간: {res.duration:.2f} s** ({status})
- 직립시간(θ<{math.degrees(C.THETA_UPRIGHT):.0f}°): **{res.upright_time:.2f} s**
- 임계 각속도 통과 시각: {cross}  ·  ω_임계 = {res.omega_crit:.2f} rad/s
- 구동: **{'채찍(재가속)' if drive=='whip' else '줄(단발 고속)' if drive=='string' else '채찍+줄'}**
  {f'· 채찍질 {wc}회 (+{whip_delta:.0f} rad/s/회)' if wc>0 else ''}
"""
    return ts_fig, gif_path, summary


# ---------------------------------------------------------------------------
# 비교 모드 / 검증 모드
# ---------------------------------------------------------------------------
def compare_defaults():
    durations = {}
    for key, pr in PRESETS.items():
        p = StructureParams(AR=pr.AR.default, mass_g=pr.mass_g.default,
                            cm_low=pr.cm_low.default, f_rim=pr.f_rim.default,
                            a_mm=pr.a_mm.default, mu=pr.mu.default, material=pr.material)
        _, inr, _ = compute_physics(p, pr.omega0.default)
        ic = InitialConditions(omega0=pr.omega0.default, theta0=math.radians(5))
        res = simulate(inr, p.mu, inr_a(p), 0, 0, ic, dt=SIM_DT, t_max=SIM_TMAX,
                       sample_dt=0.1, gamma=PIVOT_GAMMA)
        durations[key] = res.duration
    return plots.comparison_bar(durations)


def inr_a(p: StructureParams):
    from physics.topmodel import build_top
    return build_top(p).a


def verify_mode():
    """사전실험 경향 t∝I₃, t∝1/μ 자동 생성 (PRD §7.3)."""
    import numpy as np
    from physics.topmodel import build_top
    from physics.inertia import compute_inertia
    # t ~ I3 (f_rim 으로 I3 만 증가)
    base = dict(AR=2.0, mass_g=120, cm_low=0.6, a_mm=1.5, mu=0.2)
    I3s, d1 = [], []
    for f in [0.1, 0.3, 0.5, 0.7, 0.85]:
        m = build_top(StructureParams(f_rim=f, **base)); inr = compute_inertia(m)
        res = simulate(inr, m.mu, m.a, 0, 0, InitialConditions(omega0=300, theta0=math.radians(4)),
                       dt=SIM_DT, t_max=200, sample_dt=0.2)
        I3s.append(inr.I3 * 1e7); d1.append(res.duration)
    fig1 = plots.trend_figure(I3s, d1, "I₃ [g·cm²]", "t_지속 ∝ I₃")

    p0 = StructureParams(AR=2.0, mass_g=120, cm_low=0.6, f_rim=0.5, a_mm=1.5, mu=0.1)
    m0 = build_top(p0); inr0 = compute_inertia(m0)
    inv, d2 = [], []
    for mu in [0.10, 0.14, 0.20, 0.28, 0.40]:
        res = simulate(inr0, mu, m0.a, 0, 0, InitialConditions(omega0=300, theta0=math.radians(4)),
                       dt=SIM_DT, t_max=250, sample_dt=0.2)
        inv.append(1.0 / mu); d2.append(res.duration)
    fig2 = plots.trend_figure(inv, d2, "1/μ", "t_지속 ∝ 1/μ")
    return fig1, fig2


# ---------------------------------------------------------------------------
# 슬라이더 범위 갱신(탭 전환 시)
# ---------------------------------------------------------------------------
def preset_updates(preset_key):
    pr = PRESETS[preset_key]
    def upd(r):
        return gr.update(minimum=r.lo, maximum=r.hi, value=r.default)
    drive_label = {"whip": "채찍(반복 재가속)", "string": "줄(단발 고속)",
                   "both": "채찍+줄 모두"}[pr.drive]
    whip_visible = pr.drive in ("whip", "both")
    return (
        upd(pr.AR), upd(pr.mass_g), upd(pr.cm_low), upd(pr.f_rim),
        upd(pr.mu), upd(pr.a_mm), upd(pr.omega0),
        f"**구동:** {drive_label}",
        gr.update(visible=whip_visible),
        gr.update(visible=whip_visible),
    )


# ===========================================================================
# UI 빌드
# ===========================================================================
def build_app():
    with gr.Blocks(title="한·일 팽이 회전 안정성 시뮬레이션") as demo:
        gr.Markdown("# 🌀 한·일 팽이 회전 안정성 연구 & 물리 시뮬레이션\n"
                    "대전과학고 × 고마쯔고 국제교류 A조 · 구조 → 물리량 → 회전 안정성")

        with gr.Tabs():
            # ---------------- 페이지 1: 연구 소개 ----------------
            with gr.Tab("📖 연구 소개 (Research)"):
                lang = gr.Radio(["ko", "en", "ja"], value="ko", label="언어 / Language / 言語")
                research_md = gr.Markdown(RESEARCH["ko"], latex_delimiters=LATEX)
                lang.change(lambda l: RESEARCH[l], inputs=lang, outputs=research_md)

            # ---------------- 페이지 2: 시뮬레이션 ----------------
            with gr.Tab("🧪 물리 시뮬레이션 (Simulation)"):
                preset = gr.Radio(
                    [("한국 팽이", "korean"), ("일본 코마", "japanese"), ("하이브리드", "hybrid")],
                    value="korean", label="팽이 종류 (탭에 따라 구조 변수 범위가 제한됩니다)")

                with gr.Row():
                    # ===== 좌: 구조 변수 + 파생 물리량 =====
                    with gr.Column(scale=5):
                        with gr.Row():
                            # 구조/구동 변수
                            with gr.Column(scale=1):
                                gr.Markdown("### 구조 변수")
                                kr = PRESETS["korean"]
                                AR = gr.Slider(kr.AR.lo, kr.AR.hi, kr.AR.default, step=0.05,
                                               label="종횡비 AR", info="폭/높이 · 클수록 납작(편구)")
                                mass_g = gr.Slider(kr.mass_g.lo, kr.mass_g.hi, kr.mass_g.default, step=1,
                                                   label="질량 (g)")
                                cm_low = gr.Slider(kr.cm_low.lo, kr.cm_low.hi, kr.cm_low.default, step=0.02,
                                                   label="무게중심 낮춤", info="쇠심 효과 · 클수록 l↓")
                                f_rim = gr.Slider(kr.f_rim.lo, kr.f_rim.hi, kr.f_rim.default, step=0.02,
                                                  label="테두리 질량 f_rim", info="클수록 I₃↑ (안정↑)")
                                mu = gr.Slider(kr.mu.lo, kr.mu.hi, kr.mu.default, step=0.01,
                                               label="마찰 μ", info="작을수록 오래 돔")
                                a_mm = gr.Slider(kr.a_mm.lo, kr.a_mm.hi, kr.a_mm.default, step=0.1,
                                                 label="팁 곡률 a (mm)")
                                gr.Markdown("### 구동·초기조건")
                                omega0 = gr.Slider(kr.omega0.lo, kr.omega0.hi, kr.omega0.default, step=5,
                                                   label="초기 스핀 ω₀ (rad/s)")
                                theta0 = gr.Slider(1, 15, 5, step=0.5, label="초기 기울기 θ₀ (°)")
                                whip_count = gr.Slider(0, 6, 2, step=1, label="채찍질 횟수")
                                whip_delta = gr.Slider(20, 200, 80, step=10, label="채찍 세기 (rad/s)")
                                with gr.Row():
                                    precise = gr.Checkbox(True, label="정밀 마찰")
                                    steady = gr.Checkbox(True, label="정상세차 시작")
                                drive_info = gr.Markdown(f"**구동:** 채찍(반복 재가속)")
                                run_btn = gr.Button("▶ 시뮬레이션 실행", variant="primary", size="lg")
                            # 파생 물리량 패널
                            with gr.Column(scale=1):
                                gr.Markdown("### 파생 물리량 (구조 → 물리)")
                                panel = gr.Markdown()

                    # ===== 우: 회전 애니메이션 + 그래프 + 결과 =====
                    with gr.Column(scale=5):
                        d3 = gr.Image(label="🌀 팽이 회전 (초기 → 쓰러짐, 자동재생)",
                                      type="filepath", height=340)
                        summary = gr.Markdown("왼쪽에서 변수를 조절하고 **시뮬레이션 실행**을 누르세요.")
                        charts = gr.Plot(label="θ(t) / ω(t) / Ω(t)")

                with gr.Accordion("📊 비교 모드 · 검증 모드", open=False):
                    with gr.Row():
                        cmp_btn = gr.Button("세 팽이 기본값 지속시간 비교")
                        ver_btn = gr.Button("사전실험 경향 검증 (t∝I₃, t∝1/μ)")
                    cmp_plot = gr.Plot()
                    with gr.Row():
                        ver1 = gr.Plot(); ver2 = gr.Plot()

                # ----- 상태 & 이벤트 배선 -----
                prev_state = gr.State(None)
                struct_inputs = [preset, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, precise]

                def _panel(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, precise, prev):
                    return panel_markdown(preset_key, AR, mass_g, cm_low, f_rim, mu,
                                          a_mm, omega0, precise, prev)

                # 슬라이더 변경 → 패널 즉시 갱신(실행 전에도)
                for comp in [AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, precise]:
                    comp.change(_panel, inputs=struct_inputs + [prev_state],
                                outputs=[panel, prev_state])

                # 탭 전환 → 슬라이더 범위 갱신 후 패널 갱신
                preset.change(preset_updates, inputs=preset,
                              outputs=[AR, mass_g, cm_low, f_rim, mu, a_mm, omega0,
                                       drive_info, whip_count, whip_delta]).then(
                    _panel, inputs=struct_inputs + [prev_state],
                    outputs=[panel, prev_state])

                run_btn.click(
                    launch,
                    inputs=[preset, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, theta0,
                            precise, steady, whip_count, whip_delta],
                    outputs=[charts, d3, summary])

                cmp_btn.click(compare_defaults, outputs=cmp_plot)
                ver_btn.click(verify_mode, outputs=[ver1, ver2])

                # 초기 패널 렌더
                demo.load(_panel, inputs=struct_inputs + [prev_state],
                          outputs=[panel, prev_state])

        gr.Markdown("---\n<sub>물리 엔진은 무거운 대칭 팽이(Heavy Symmetric Top) 운동방정식을 "
                    "RK4 로 직접 적분하며, 관성모멘트는 회전체 적분으로 계산합니다. "
                    "PRD §6.1·§6.2 / 검증 §7 준수.</sub>")
    return demo


demo = build_app()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860,
                theme=gr.themes.Soft(primary_hue="amber"))
