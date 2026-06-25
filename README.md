---
title: 한일 팽이 회전 안정성 시뮬레이션
emoji: 🌀
colorFrom: yellow
colorTo: gray
sdk: gradio
sdk_version: 6.19.0
app_file: app.py
pinned: false
license: mit
---

# 🌀 한·일 팽이 회전 안정성 연구 & 물리 시뮬레이션

대전과학고 × 고마쯔고 국제교류 A조의 공동연구 발표용 인터랙티브 시뮬레이션입니다.
**구조(형태) → 물리량(I₃·I₁·l·μ) → 회전 안정성** 의 인과 구조를 직접 조작하며 탐구합니다.

> 원본 PRD 는 React/Vite/Three.js 스택을 제안했으나, 배포 환경(**HuggingFace Spaces ·
> Gradio · CPU basic**)에 맞춰 **물리 엔진을 Python 으로 충실히 이식**하고 UI 를 Gradio 로
> 구현했습니다. 물리 공식·검증 오라클은 PRD §6.1·§6.2·§7 을 그대로 따릅니다.

## 페이지

1. **📖 연구 소개 (Research)** — 주제·이론·선행연구·실험설계·일정 (한국어/영어/일본어, 수식 KaTeX).
2. **🧪 물리 시뮬레이션 (Simulation)** — 한국/일본/하이브리드 팽이. 사이드바의 구조 변수를
   조절하면 물리량이 즉시 갱신되고, 발사 시 자전+세차+장동하는 3D 팽이와 θ(t)/ω(t)/Ω(t)
   그래프가 그려집니다.

## 물리 모델 (PRD §6.1)

무거운 대칭 팽이(Heavy Symmetric Top)의 라그랑지안 운동방정식을 **RK4 로 직접 적분**합니다
(범용 물리엔진 미사용 — 고속 자이로의 수치 안정성 확보).

```
θ̈ = sinθ·(I₁·φ̇²·cosθ - I₃·ω₃·φ̇ + m·g·l)/I₁
φ̇ = (p_φ - I₃·ω₃·cosθ)/(I₁·sin²θ)
I₃·dω₃/dt = -(2/3)μmga·cosθ - b·ω₃ - c·ω₃|ω₃|
dp_φ/dt = cosθ·τ_axis        # 스핀 감쇠의 연직성분이 L_z 도 감쇠 (물리 정확성 핵심)
ω_임계 = 2√(mgl·I₁)/I₃,   Ω = mgl/(I₃ω),   t ≈ I₃ω₀/((2/3)μmga)
```

관성모멘트는 팽이를 회전체로 보고 얇은 원판 적분으로 계산합니다 (단일 출처, PRD §6.2.1):
```
m=Σdm,  l=z_cm=Σz·dm/m,  I₃=Σ½dm·r²,  I₁,cm=Σdm(¼r²+(z-z_cm)²),  I₁=I₁,cm+ml²
```

## 실행

```bash
pip install -r requirements.txt
python app.py            # http://localhost:7860
```

## 검증 (PRD §7 오라클 — 필수)

```bash
pytest -q
```
- §7.1 관성 적분(균일 원판/원기둥/원뿔 해석해 대조, 평행축 정리, f_rim 단조성)
- §7.2 운동방정식(무마찰 에너지·p_ψ 보존, 정상세차율, sleeping, 세차-스핀 반비례)
- §7.3 사전실험 경향(t∝I₃, t∝1/μ, R²>0.98)
- §7.4 수치 안정성(θ→0 NaN 미발생, dt 수렴)

## 적대적 리뷰 (PRD §8)

`.claude/agents/physics-critic.md`, `.claude/agents/code-critic.md` 에 비판 전용
서브에이전트 정의가 포함되어 있습니다. 물리 변경 시 오라클 테스트로 검증을 강제합니다.

## 구조

```
app.py                 # Gradio 엔트리(2 페이지)
physics/               # 물리 엔진 (UI보다 먼저)
  constants · topmodel · inertia · equations · integrator · mapping
presets/               # 한국/일본/하이브리드 범위·기본값 (§6.3)
ui/                    # plots(plotly) · research(본문)
tests/test_oracles.py  # §7 검증 오라클
.claude/agents/        # 비판 서브에이전트 (§8)
```
