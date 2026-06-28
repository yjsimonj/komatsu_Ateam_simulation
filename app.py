"""한·일 팽이 회전 안정성 — 물리 시뮬레이션 웹앱 (PRD 구현).

HuggingFace Spaces / Gradio / CPU basic 환경용. PRD 의 React/Vite 스택을 Gradio 로
이식했으며, 물리 엔진(physics/)·검증 오라클(tests/)은 PRD §6.1·§6.2·§7 을 그대로 따른다.

페이지 1: 연구 소개(Research)   페이지 2: 물리 시뮬레이션(Simulation)
"""

from __future__ import annotations

import math
import gradio as gr

from physics.topmodel import StructureParams, fall_angle
from physics.mapping import compute_physics
from physics.integrator import InitialConditions, simulate
from physics import constants as C
from presets import PRESETS
from ui import plots
from ui import concept
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
#### Physical quantities
| | |
|--|--|
| Mass m | **{_fmt(s.m*1000,'g',3)}**{A('m',s.m)} |
| Center of mass l | **{_fmt(s.l*1000,'mm',3)}**{A('l',s.l)} |
| Spin inertia I₃ | **{_fmt(s.I3*1e7,'g·cm²',3)}**{A('I3',s.I3)} |
| Transverse inertia I₁ | {_fmt(s.I1*1e7,'g·cm²',3)}{A('I1',s.I1)} |
| Friction μ | {_fmt(s.mu,'',2)} |

#### Stability
| | |
|--|--|
| Critical spin ω_crit | **{_fmt(s.omega_crit,'rad/s',3)}**{A('wc',s.omega_crit)} |
| | <sub>{rpm:.0f} rpm</sub> |
| Precession rate Ω₀ | {_fmt(s.Omega0,'rad/s',3)} |
| Predicted lifetime | **{_fmt(s.t_pred,'s',3)}**{A('t',s.t_pred)} |

<sub>🔺/🔻 = change vs. previous · at ω₀={omega0:.0f} rad/s</sub>
"""
    new_prev = dict(m=s.m, l=s.l, I3=s.I3, I1=s.I1, wc=s.omega_crit, t=s.t_pred)
    return md, new_prev


# ---------------------------------------------------------------------------
# 시뮬레이션 실행 → 그래프/3D/요약
# ---------------------------------------------------------------------------
def launch(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, theta0_deg,
           precise, steady):
    p = _structure(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm)
    model, inr, s = compute_physics(p, omega0, precise_friction=precise)

    ic = InitialConditions(omega0=omega0, theta0=math.radians(theta0_deg),
                           steady_precession=steady)
    res = simulate(inr, model.mu, model.a, model.b, model.c, ic,
                   dt=SIM_DT, t_max=SIM_TMAX, sample_dt=SIM_SAMPLE_DT,
                   precise_friction=precise, gamma=PIVOT_GAMMA,
                   theta_fall=fall_angle(model))

    ts_fig = plots.time_series_figure(res, preset_key)
    gif_path = make_top_gif(model, res, preset_key)   # auto-playing GIF

    status = "fell over ✅" if res.fell else f"stayed upright for {SIM_TMAX:.0f}s"
    cross = f"{res.t_cross_crit:.2f} s" if res.t_cross_crit is not None else "—"
    fall_deg = math.degrees(res.theta_fall)
    summary = f"""
### Result summary
- **Spin lifetime: {res.duration:.2f} s** ({status})
- Upright time (θ<{math.degrees(C.THETA_UPRIGHT):.0f}°): **{res.upright_time:.2f} s**
- Body touches floor at θ = **{fall_deg:.0f}°** (fall criterion)
- Crossed critical spin at: {cross}  ·  ω_crit = {res.omega_crit:.2f} rad/s
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
        model, inr, _ = compute_physics(p, pr.omega0.default)
        ic = InitialConditions(omega0=pr.omega0.default, theta0=math.radians(5))
        res = simulate(inr, p.mu, model.a, 0, 0, ic, dt=SIM_DT, t_max=SIM_TMAX,
                       sample_dt=0.1, gamma=PIVOT_GAMMA, theta_fall=fall_angle(model))
        durations[key] = res.duration
    return plots.comparison_bar(durations)


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
                       dt=SIM_DT, t_max=200, sample_dt=0.2, theta_fall=fall_angle(m))
        I3s.append(inr.I3 * 1e7); d1.append(res.duration)
    fig1 = plots.trend_figure(I3s, d1, "I₃ [g·cm²]", "lifetime t ∝ I₃")

    p0 = StructureParams(AR=2.0, mass_g=120, cm_low=0.6, f_rim=0.5, a_mm=1.5, mu=0.1)
    m0 = build_top(p0); inr0 = compute_inertia(m0)
    inv, d2 = [], []
    for mu in [0.10, 0.14, 0.20, 0.28, 0.40]:
        res = simulate(inr0, mu, m0.a, 0, 0, InitialConditions(omega0=300, theta0=math.radians(4)),
                       dt=SIM_DT, t_max=250, sample_dt=0.2, theta_fall=fall_angle(m0))
        inv.append(1.0 / mu); d2.append(res.duration)
    fig2 = plots.trend_figure(inv, d2, "1/μ", "lifetime t ∝ 1/μ")
    return fig1, fig2


# ---------------------------------------------------------------------------
# 슬라이더 범위 갱신(탭 전환 시)
# ---------------------------------------------------------------------------
def preset_updates(preset_key):
    pr = PRESETS[preset_key]
    def upd(r):
        return gr.update(minimum=r.lo, maximum=r.hi, value=r.default)
    return (
        upd(pr.AR), upd(pr.mass_g), upd(pr.cm_low), upd(pr.f_rim),
        upd(pr.mu), upd(pr.a_mm), upd(pr.omega0),
    )


# ===========================================================================
# Page 3 — Concept: measuring spin rate with a laser + Fourier transform
# ===========================================================================
def _build_concept_tab():
    with gr.Tab("🔦 How we measured ω (laser + FFT)"):
        gr.Markdown("## Measuring the spin rate ω with a laser and a Fourier transform\n"
                    "This page explains the **measurement method** from our real experiment — "
                    "it is a concept walkthrough, not a parametric simulation. Use **Prev / Next** "
                    "to step through the idea.")
        with gr.Row():
            # Left: stepper text + photo of the real setup
            with gr.Column(scale=1):
                step_state = gr.State(0)
                step_box = gr.Markdown(concept.step_md(0))
                with gr.Row():
                    prev_b = gr.Button("◀ Prev")
                    next_b = gr.Button("Next ▶", variant="primary")
                gr.Markdown("#### Real experiment photo")
                photo = gr.Image(value=concept.PHOTO_PATH, type="filepath",
                                 label="half foil / half black tape, laser + light sensor + Arduino",
                                 height=300, interactive=False)
                if concept.PHOTO_PATH is None:
                    gr.Markdown("<sub>📷 Place the photo at `assets/experiment_setup.jpg` "
                                "to show it here.</sub>")
            # Right: schematic + signal + FFT
            with gr.Column(scale=1):
                gr.Plot(concept.setup_diagram())
                gr.Plot(concept.illuminance_figure())
                gr.Plot(concept.fft_figure())

        def _step(cur, delta):
            nxt = max(0, min(cur + delta, len(concept.STEPS) - 1))
            return nxt, concept.step_md(nxt)

        prev_b.click(lambda c: _step(c, -1), inputs=step_state, outputs=[step_state, step_box])
        next_b.click(lambda c: _step(c, +1), inputs=step_state, outputs=[step_state, step_box])


# ===========================================================================
# UI build
# ===========================================================================
def build_app():
    with gr.Blocks(title="Korea–Japan Spinning-Top Rotational Stability") as demo:
        gr.Markdown("# 🌀 Korea–Japan Spinning-Top Stability — Research & Physics Simulation\n"
                    "Daejeon Science HS × Komatsu HS, Team A · structure → physical quantity → stability")

        with gr.Tabs():
            # ---------------- Page 1: Research (multilingual) ----------------
            with gr.Tab("📖 연구 소개 (Research)"):
                lang = gr.Radio(["ko", "en", "ja"], value="ko", label="언어 / Language / 言語")
                research_md = gr.Markdown(RESEARCH["ko"], latex_delimiters=LATEX)
                lang.change(lambda l: RESEARCH[l], inputs=lang, outputs=research_md)

            # ---------------- Page 2: Simulation (English) ----------------
            with gr.Tab("🧪 Physics Simulation"):
                preset = gr.Radio(
                    [("Korean Top", "korean"), ("Japanese Koma", "japanese"), ("Hybrid", "hybrid")],
                    value="korean", label="Top type (each preset limits the structure-variable ranges)")

                with gr.Row():
                    # ===== Left: structure variables + derived quantities =====
                    with gr.Column(scale=5):
                        with gr.Row():
                            # structure / launch variables
                            with gr.Column(scale=1):
                                gr.Markdown("### Structure variables")
                                kr = PRESETS["korean"]
                                AR = gr.Slider(kr.AR.lo, kr.AR.hi, kr.AR.default, step=0.05,
                                               label="Aspect ratio AR", info="width/height · larger = flatter (oblate)")
                                mass_g = gr.Slider(kr.mass_g.lo, kr.mass_g.hi, kr.mass_g.default, step=1,
                                                   label="Mass (g)")
                                cm_low = gr.Slider(kr.cm_low.lo, kr.cm_low.hi, kr.cm_low.default, step=0.02,
                                                   label="Lower the center of mass", info="metal-core effect · larger = lower l")
                                f_rim = gr.Slider(kr.f_rim.lo, kr.f_rim.hi, kr.f_rim.default, step=0.02,
                                                  label="Rim mass f_rim", info="larger = higher I₃ (more stable)")
                                mu = gr.Slider(kr.mu.lo, kr.mu.hi, kr.mu.default, step=0.01,
                                               label="Friction μ", info="smaller = spins longer")
                                a_mm = gr.Slider(kr.a_mm.lo, kr.a_mm.hi, kr.a_mm.default, step=0.1,
                                                 label="Tip curvature a (mm)")
                                gr.Markdown("### Launch / initial conditions")
                                omega0 = gr.Slider(kr.omega0.lo, kr.omega0.hi, kr.omega0.default, step=5,
                                                   label="Initial spin ω₀ (rad/s)")
                                theta0 = gr.Slider(1, 15, 5, step=0.5, label="Initial tilt θ₀ (°)")
                                with gr.Row():
                                    precise = gr.Checkbox(True, label="Precise friction")
                                    steady = gr.Checkbox(True, label="Start in steady precession")
                                run_btn = gr.Button("▶ Run simulation", variant="primary", size="lg")
                            # derived-quantities panel
                            with gr.Column(scale=1):
                                gr.Markdown("### Derived quantities (structure → physics)")
                                panel = gr.Markdown()

                    # ===== Right: rotation animation + graphs + result =====
                    with gr.Column(scale=5):
                        d3 = gr.Image(label="🌀 Top rotation (start → fall, auto-play)",
                                      type="filepath", height=340)
                        summary = gr.Markdown("Adjust the variables on the left and press **Run simulation**.")
                        charts = gr.Plot(label="θ(t) / ω(t) / Ω(t)")

                with gr.Accordion("📊 Comparison & validation modes", open=False):
                    with gr.Row():
                        cmp_btn = gr.Button("Compare default lifetimes of the three tops")
                        ver_btn = gr.Button("Validate pre-experiment trends (t∝I₃, t∝1/μ)")
                    cmp_plot = gr.Plot()
                    with gr.Row():
                        ver1 = gr.Plot(); ver2 = gr.Plot()

                # ----- state & event wiring -----
                prev_state = gr.State(None)
                struct_inputs = [preset, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, precise]

                def _panel(preset_key, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, precise, prev):
                    return panel_markdown(preset_key, AR, mass_g, cm_low, f_rim, mu,
                                          a_mm, omega0, precise, prev)

                # slider change → live panel refresh (before running too)
                for comp in [AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, precise]:
                    comp.change(_panel, inputs=struct_inputs + [prev_state],
                                outputs=[panel, prev_state])

                # preset change → refresh slider ranges, then refresh panel
                preset.change(preset_updates, inputs=preset,
                              outputs=[AR, mass_g, cm_low, f_rim, mu, a_mm, omega0]).then(
                    _panel, inputs=struct_inputs + [prev_state],
                    outputs=[panel, prev_state])

                run_btn.click(
                    launch,
                    inputs=[preset, AR, mass_g, cm_low, f_rim, mu, a_mm, omega0, theta0,
                            precise, steady],
                    outputs=[charts, d3, summary])

                cmp_btn.click(compare_defaults, outputs=cmp_plot)
                ver_btn.click(verify_mode, outputs=[ver1, ver2])

                # initial panel render
                demo.load(_panel, inputs=struct_inputs + [prev_state],
                          outputs=[panel, prev_state])

            # ---------------- Page 3: Concept — laser/FFT spin measurement ----------------
            _build_concept_tab()

        gr.Markdown("---\n<sub>The physics engine integrates the Heavy Symmetric Top equations of "
                    "motion directly with RK4; moments of inertia come from a solid-of-revolution "
                    "integral. Conforms to PRD §6.1·§6.2 / validation §7.</sub>")
    return demo


demo = build_app()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860,
                theme=gr.themes.Soft(primary_hue="amber"))
