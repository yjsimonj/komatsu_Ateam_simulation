"""페이지 1 — 연구 소개 (PRD §5). 한국어/영어/일본어 본문.

수식은 KaTeX 로 렌더링한다(gr.Markdown latex_delimiters). §5.1 의 모든 섹션 포함.
"""

from __future__ import annotations

# 좌측 목차용 섹션 키
SECTIONS = [
    ("intro", "인트로 / Intro"),
    ("topic", "주제 소개·선정 배경"),
    ("compare", "팽이 비교"),
    ("theory", "이론적 배경"),
    ("prior", "선행연구 분석"),
    ("design", "실험 설계"),
    ("control", "변인 설정 및 통제"),
    ("pre", "사전실험"),
    ("sim", "실제 실험·시뮬레이션"),
    ("roles", "역할 분담·일정"),
    ("outro", "아웃트로"),
]

RESEARCH_KO = r"""
# 한·일 팽이 회전 안정성 연구
### 한국 팽이와 일본 코마 비교를 통한 회전 안정성 최적화 하이브리드 팽이 설계
**대전과학고 × 고마쯔고 국제교류 A조** — 김묘경 · 이담비 · 주영준 · 이지호 · 발표 2026년 7월 말, 일본

---

## 1. 인트로
대전과학고와 고마쯔고가 국제교류 공동연구를 진행합니다. 일본 방문 **전에** 한국팀이 단독으로
수행하는 부분은 **"팽이의 회전 안정성(넘어질 때까지 걸린 시간)에 영향을 주는 물리적 요인"** 규명입니다.
이 물리적 요인은 **회전관성 $I_3$** 와 **바닥–팁 사이 마찰 $\mu$** 이며, 이 변수들과 지속시간 사이의
상관관계를 찾습니다. 일본 방문 **후에는** 양국이 합동으로 그 물리적 변인에 영향을 주는 구조들을 찾아
**하이브리드 팽이**를 제작합니다.

## 2. 주제 소개·선정 배경
같은 물리(회전 안정성)를 서로 다른 형태로 구현한 두 전통 — 한국 팽이와 일본 코마 — 를 비교하면
"형태 → 물리량 → 안정성" 의 인과 구조를 깨끗하게 분리해 최적화할 수 있습니다.

**연구질문 3개**
1. 회전 안정성을 결정하는 물리량은 무엇인가? ($I_3$, $\mu$, $l$ …)
2. 어떤 형태에서 유리한가? 한국형(편장) vs 일본형(편구)
3. 두 전통을 융합하면 더 안정한가?

**인과구조 다이어그램**

> **구조(형태)** ⟶ **물리량** ⟶ **회전 안정성**
>
> 종횡비·질량분포·무게중심·팁 ⟶ $I_3,\ I_1,\ l,\ \mu$ ⟶ 지속시간·$\omega_{crit}$·세차·$\theta(t)$

## 3. 팽이 비교
| 항목 | 한국 전통 팽이 | 일본 베이고마/코마 |
| --- | --- | --- |
| 재질 | 나무 중심 (하부 쇠심) | 금속 중심 (주철 등 고밀도) |
| 몸체 형태 | 원뿔/원통/말뚝형 (**편장 prolate**) | 납작한 원반형 (**편구 oblate**) |
| 종횡비(폭/높이) | 작음 (길쭉) | 큼 (납작·넓음) |
| 질량 분포 | 축 중심 집중 → $I_3$ 작음 | 외곽(rim) 집중 → $I_3$ 큼 |
| 무게중심 $l$ | 아래쪽(낮음) | 낮게 형성 |
| 팁/마찰 | 상대적 고마찰 | 저마찰·장시간 지향 |
| 구동 방식 | 채찍으로 **반복 에너지 공급** | 줄을 감아 **한 번에 고속** |
| $I_3/I_1$ 비 | 작음 (sleeping 불리) | 큼 (sleeping 유리) |

> ⚠️ 형태 변이가 크므로, 실제 표본의 $m,\,l,\,I_3,\,I_1,\,$팁형상을 직접 측정해 설계공간에
> 점으로 비교합니다. "형태가 다르면 물리량도 다르다."

**대표 종류** — 한국: **말팽이**(평평한 머리 → 원뿔 → 뾰족한 끝, 가장 잘·오래 도는 형) · **장구팽이**(양끝 뾰족) · **줄팽이**(허리 잘록, 끈으로 던짐) · **바가지팽이**(손으로 비빔). 일본: **나게고마**(투げごま, 끈으로 던져 단발 고속) · **베이고마**(ベーゴマ, 금속·안정) · **철테/싸움 코마**(鉄輪·喧嘩ごま, 바깥 쇠테로 $I_3$ 극대화) · **박다/곡예 코마**(博多·曲ごま, 가는 쇠심 목재, 회전 수명 매우 김) · **역립 코마**(逆立ちごま, 돌다 스스로 뒤집히는 **tippe top**, 세차·구름마찰과 직결).

> 💡 팽이가 오래 똑바로 도는 상태를 물리학에서 **sleeping top**($\omega>\omega_{crit}$)이라 부릅니다. (한국에서도 이를 *"잠을 잔다"*고 표현한다는 이야기가 있으나 **출처 확인 필요**.)

## 4. 이론적 배경
**(1) 자이로 안정화** — 정지 팽이는 불안정 평형이라 쓰러집니다. 빠르게 자전하면 각운동량
$L = I_3\omega$ 가 생기고, 중력 토크 $\tau = mgl\sin\theta$ 가 $L$ 과 수직으로 작용해 $L$ 의 *방향*만
천천히 돌립니다 → **세차운동**.

**(2) 임계 각속도 (Sleeping 조건)**
$$\omega_{crit} = \frac{2\sqrt{m\,g\,l\,I_1}}{I_3}$$
$\omega < \omega_{crit}$ 가 되면 $\theta$ 가 급증하며 쓰러집니다.

**(3) 세차 각속도**
$$\Omega = \frac{m\,g\,l}{I_3\,\omega}$$
자전이 느려질수록 세차가 빨라집니다 ($\Omega \propto 1/\omega$).

**(4) 마찰 토크 (자전 감쇠의 주원인)** — 정밀형 / 단순형
$$\tau_{fric} = -\tfrac{2}{3}\,\mu\,m\,g\,a\,\cos\theta \qquad \tau_{fric}\approx -\mu\,m\,g\,a$$

**(5) 공기저항 토크** $\;\tau_{visc} = -b\,\omega_3,\quad \tau_{turb} = -c\,\omega_3^2$

**(6) 자전 감쇠 & 지속시간 (사전실험 핵심)** — 지속시간 $t_{life}$
$$I_3\frac{d\omega}{dt} = -\mu\,m\,g\,a \;\Rightarrow\; \omega(t)=\omega_0 - \frac{\mu m g a}{I_3}t \;\Rightarrow\; t_{life}\approx \frac{I_3\,\omega_0}{\mu\,m\,g\,a}$$

⟹ $t_{life}\propto I_3$ (양의 선형), $\;t_{life}\propto 1/\mu$ (반비례)

**(7) 관성모멘트 & 평행축 정리** $\;I=\int r^2\,dm,\quad I_1 = I_{1,cm} + m\,l^2$

**(8) 2선식 진자 측정식** $\;I = \dfrac{m\,g\,b^2\,T^2}{4\pi^2 L}$

> **예상 Q&A** — Q: 왜 빠르면 안 쓰러지나? A: 각운동량이 커서 중력 토크가 방향만 돌릴 뿐
> 쓰러뜨리지 못합니다($\omega>\omega_{crit}$). Q: 왜 결국 쓰러지나? A: 마찰이 $\omega$ 를 줄여
> $\omega<\omega_{crit}$ 가 되기 때문입니다.

## 5. 선행연구 분석
| # | 선행연구 | 핵심 |
| --- | --- | --- |
| 1 | 문미옥(2012), 유아교육연구 32(4), 445–464 | 한국 전통 팽이 구조: 나무 몸체+하부 쇠심, 축 중심 질량 |
| 2 | 문미옥·이지예(2011), 유아교육연구 31(4), 361–379 | 말팽이 편장(prolate)·하부 질량 집중·채찍 지속가속 |
| 3 | Kaaronen 외 (출처확인중) | 베이고마 동역학 — 저자·연도 확인 후 정식 기재 |
| 4 | 김세연 외(2012), 제주과학고 | 세차 이론·실험 비교 방법론(초고속카메라·Logger Pro) |
| 5 | Rod Cross(2013), *Am. J. Phys.* 81(4), 280–289, DOI 10.1119/1.4776195 | 팁/바닥 형상 → 세차·안정성, rising/tippe top |
| 6 | Bächer·Whiting·Bickel·Sorkine-Hornung, *Spin-It* (ACM TOG 33(4), SIGGRAPH 2014) | 내부 질량 재분배로 관성모멘트 최적화 |

> **선행연구 공백:** 한·일 팽이의 *정량 비교* + *하이브리드 검증* 을 함께 다룬 연구가 드뭅니다.
> 본 연구는 이 공백을 시뮬레이션 + 실측으로 메웁니다.

## 6. 실험 설계
인과사슬을 두 고리로 분리합니다.
- **물리 → 안정성 (사전실험):** 물리량을 직접 측정/조작하여 지속시간과의 관계 규명.
- **구조 → 물리 (보정실험):** 구조 변수를 바꿔 물리량이 어떻게 변하는지 측정.

3단계 계획: ① 반응표면 탐색 → ② 보정지도 작성 → ③ 하이브리드 역설계·검증.
**종속변수 5지표:** 회전 지속시간 · 임계각속도 · 세차 주기/진폭 · 기울임각 $\theta(t)$ · 직립시간.

## 6b. 변인 설정 및 통제
- **조작변인:** $I_3,\,m,\,l,\,a,\,\mu$
- **통제변인:** $\omega_0$ (가장 중요) · $\theta_0$ · 바닥 · 무풍 등
- **종속변인:** 위 5지표
- **모듈형 시험팽이:** 축 위 질량($m\cdot l$ 손잡이) + 반경 위 질량($I_3$ 손잡이)을 분리.
  외형을 고정한 채 $I_3$ 만 바꾸는 3가지 방법(테두리 추가·내부 재분배·재질 교체).
- **측정·검증:** 저울(질량) · 칼날 균형(무게중심) · 2선식 진자(관성모멘트).

> ⚠️ 반경 재배치($f_{rim}$, AR)는 $I_1$ 도 함께 바꿉니다. 지속시간·세차는 $I_3$ 만 들어가
> 깨끗하지만, 임계각속도는 $I_1\,I_3$ 결합이므로 결합량 $mgl\,I_1/I_3^2$ 도 함께 봅니다.

## 7. 사전실험
- 예측: $t\propto I_3$ (선형), $t\propto 1/\mu$ (반비례).
- 마찰계수 측정: 빗면법 $\mu=\tan\theta$ (블록=팁재질, 면=바닥재).
- 가정·한계: 쿨롱 마찰 근사, 공기저항은 부차적.
- **쓰러짐 정의:** 팽이를 놓은 순간부터 **팁을 제외한 밑면이 바닥에 닿기 시작한 순간**까지를 회전 지속시간으로 본다. (이 웹앱의 시뮬레이션도 동일하게, 대칭축이 수평이 되는 90°가 아니라 *몸체 바깥면이 바닥에 닿는 각*을 쓰러짐으로 판정합니다.)
- **초기 각속도 통제:** 모터 + 3D펜으로 만든 '모터 꽂는 모자'로 같은 시간 돌린 뒤 수직으로 분리해 $\omega_0$ 를 일정하게 맞춤(고무줄·수동 감기 방식의 편차 극복).

**각속도 측정 — 레이저 + 아두이노 + 푸리에 변환** (→ 세 번째 탭에서 원리를 애니메이션으로 확인)
팽이 옆면을 **절반은 알루미늄 호일(밝음), 절반은 검은 절연테이프(어두움)**로 감고 회전시키며 **레이저**를 쏴, 반사광을 **광센서+아두이노**로 측정한다. 한 바퀴마다 밝음/어둠이 1회 반복되므로 신호 주파수 $f$ 가 곧 회전수이고, **(단시간) 푸리에 변환(STFT)**의 봉우리에서 $\omega = 2\pi f$ 를 얻는다. 분해능 $\Delta f = f_s/N$, 나이퀴스트 $f_s>2f_{max}$. 우리 장치에서는 센서값이 *어두울수록 높게* 나왔다.
> ⚠️ 현재 한계: 팁 고정 측정이라 **세차운동을 레이저가 따라가지 못해 오차가 큼**. 2학기에 3D프린터·과학상자로 측정 리그를 정밀화하고 레이저 정렬·STFT로 개선 예정. 현재는 **경향성**만 해석.

## 8. 실제 실험·시뮬레이션
3단계 통합: 반응표면 → 보정지도 → 하이브리드 역설계·검증.
$\theta(t)$ 수치적분(이 웹앱의 물리 엔진), Monte Carlo 설계공간 탐색, 예측 vs 실측 비교.
→ **[시뮬레이션 페이지]에서 직접 조작해 보세요.**

## 9. 역할 분담·일정
| 시기 | 내용 |
| --- | --- |
| ~7월 초 | 안정성 정의·지표 확정 |
| 7월 중 | 모듈형 팽이·측정 리그 제작, 사전실험 ($t$–$I_3$, $t$–$\mu$) |
| 7월 말 | 발표 자료·시뮬레이션 정리, **일본 발표**·합동 공동연구(하이브리드 제작) |

## 10. 아웃트로
**기대결과:** $I_3,\,l,\,\mu$ 의 정량 관계, 한·일 형태–물리량 비교, 하이브리드 설계·검증.
**의의:** 문화 교류 + 물리·공학 융합. **향후 과제:** 팁 형상·재질 독립변수화, 팽이 충돌 안정성,
설계공간 확장.

> 감사합니다 · Thank you · ありがとうございました
"""

RESEARCH_EN = r"""
# Korea–Japan Spinning-Top Rotational Stability Study
### Designing a stability-optimized hybrid top by comparing the Korean *paengi* and the Japanese *koma*
**Daejeon Science HS × Komatsu HS, Exchange Team A** — Kim Myo-gyeong · Lee Dam-bi · Joo Young-jun · Lee Ji-ho · Presented late July 2026, Japan

---

## 1. Intro
Daejeon Science HS and Komatsu HS run a joint international-exchange study. **Before** the visit to Japan, the Korean team works alone to identify the **physical factors that govern a top's rotational stability** (the time until it falls). Those factors are the **spin moment of inertia $I_3$** and the **tip–floor friction $\mu$**; we look for the relationship between these variables and the spin lifetime. **After** the visit, both teams jointly find the structures that drive those physical variables and build a **hybrid top**.

## 2. Topic & Motivation
Two traditions realize the *same physics* (rotational stability) with *different shapes*. Comparing them lets us cleanly separate and optimize the causal chain **shape → physical quantity → stability**.

**Three research questions**
1. Which physical quantities decide rotational stability? ($I_3$, $\mu$, $l$ …)
2. Which shape is favorable — Korean (prolate) vs Japanese (oblate)?
3. Does fusing the two traditions give greater stability?

**Causal-structure diagram**

> **Shape** ⟶ **Physical quantity** ⟶ **Rotational stability**
>
> aspect ratio · mass distribution · center of mass · tip ⟶ $I_3,\ I_1,\ l,\ \mu$ ⟶ lifetime · $\omega_{crit}$ · precession · $\theta(t)$

## 3. Korean vs Japanese tops
| Item | Korean traditional top | Japanese beigoma / koma |
| --- | --- | --- |
| Material | wood-based (lower iron core) | metal-based (cast iron, high density) |
| Body shape | cone / cylinder / peg (**prolate**) | flat disk (**oblate**) |
| Aspect ratio (width/height) | small (tall) | large (flat, wide) |
| Mass distribution | concentrated on axis → small $I_3$ | concentrated at rim → large $I_3$ |
| Center of mass $l$ | low | formed low |
| Tip / friction | relatively high friction | low friction, long-spin oriented |
| Drive | whip — **repeated energy input** | string — **single high-speed launch** |
| $I_3/I_1$ ratio | small (sleeping unfavorable) | large (sleeping favorable) |

> ⚠️ Because shapes vary widely, we directly measure each real sample's $m,\,l,\,I_3,\,I_1,$ and tip shape and compare them as points in the design space. "Different shape ⇒ different physical quantities."

**Representative types** — Korea: **malpaengi** (flat head → cone → sharp tip; the best, longest spinner) · **janggu-paengi** (pointed at both ends) · **jul-paengi** (waisted, string-thrown) · **bagaji-paengi** (finger-spun). Japan: **nage-goma** (投げごま, string-thrown single high-speed launch) · **beigoma** (ベーゴマ, metal, stable) · **iron-rim / fighting koma** (鉄輪·喧嘩ごま, an outer iron ring maximizes $I_3$) · **Hakata / performance koma** (博多·曲ごま, wooden with a thin iron core, very long spin life) · **tippe top** (逆立ちごま, spins then flips itself over — tied to precession and rolling friction).

> 💡 A long, upright spin is the **sleeping top** state in physics ($\omega>\omega_{crit}$). (A Korean expression *"jameul janda"* — "it sleeps" — is sometimes cited for this; **source to be confirmed**.)

## 4. Theoretical background
**(1) Gyroscopic stabilization** — a non-spinning top is in unstable equilibrium and falls. Spinning fast creates angular momentum $L = I_3\omega$; the gravitational torque $\tau = mgl\sin\theta$ acts perpendicular to $L$ and only slowly turns its *direction* → **precession**.

**(2) Critical angular velocity (sleeping condition)**
$$\omega_{crit} = \frac{2\sqrt{m\,g\,l\,I_1}}{I_3}$$
Once $\omega < \omega_{crit}$, the tilt $\theta$ grows rapidly and the top falls.

**(3) Precession rate**
$$\Omega = \frac{m\,g\,l}{I_3\,\omega}$$
The slower the spin, the faster the precession ($\Omega \propto 1/\omega$).

**(4) Friction torque (main cause of spin decay)** — precise / simple form
$$\tau_{fric} = -\tfrac{2}{3}\,\mu\,m\,g\,a\,\cos\theta \qquad \tau_{fric}\approx -\mu\,m\,g\,a$$

**(5) Air-drag torque** $\;\tau_{visc} = -b\,\omega_3,\quad \tau_{turb} = -c\,\omega_3^2$

**(6) Spin decay & lifetime (core of the pre-experiment)** — lifetime $t_{life}$
$$I_3\frac{d\omega}{dt} = -\mu\,m\,g\,a \;\Rightarrow\; \omega(t)=\omega_0 - \frac{\mu m g a}{I_3}t \;\Rightarrow\; t_{life}\approx \frac{I_3\,\omega_0}{\mu\,m\,g\,a}$$

⟹ $t_{life}\propto I_3$ (positive linear), $\;t_{life}\propto 1/\mu$ (inverse)

**(7) Moment of inertia & parallel-axis theorem** $\;I=\int r^2\,dm,\quad I_1 = I_{1,cm} + m\,l^2$

**(8) Bifilar-pendulum measurement** $\;I = \dfrac{m\,g\,b^2\,T^2}{4\pi^2 L}$

> **Expected Q&A** — Q: Why doesn't a fast top fall? A: Its angular momentum is large, so gravity only redirects it ($\omega>\omega_{crit}$). Q: Why does it fall eventually? A: Friction reduces $\omega$ until $\omega<\omega_{crit}$.

## 5. Prior research
| # | Study | Key point |
| --- | --- | --- |
| 1 | Moon (2012), *J. Early Childhood Educ.* 32(4), 445–464 | Korean top structure: wood body + lower iron core, axis-centered mass |
| 2 | Moon & Lee (2011), *J. Early Childhood Educ.* 31(4), 361–379 | malpaengi prolate, lower-mass concentration, whip sustained drive |
| 3 | Kaaronen et al. (source TBC) | beigoma dynamics — authors/year to be confirmed |
| 4 | Kim et al. (2012), Jeju Science HS | precession theory–experiment methodology (high-speed camera, Logger Pro) |
| 5 | Rod Cross (2013), *Am. J. Phys.* 81(4), 280–289, DOI 10.1119/1.4776195 | tip/floor shape → precession & stability, rising/tippe top |
| 6 | Bächer, Whiting, Bickel, Sorkine-Hornung, *Spin-It* (ACM TOG 33(4), SIGGRAPH 2014) | optimizing moment of inertia by internal mass redistribution |

> **Research gap:** few studies *quantitatively compare* Korean and Japanese tops **and** validate a hybrid. We fill this gap with simulation + measurement.

## 6. Experimental design
We split the causal chain into two links.
- **Physics → stability (pre-experiment):** directly measure/manipulate physical quantities and relate them to lifetime.
- **Structure → physics (calibration experiment):** change structure variables and measure how the physical quantities respond.

Three-stage plan: ① response-surface exploration → ② calibration map → ③ hybrid reverse-design & validation.
**Five dependent metrics:** spin lifetime · critical angular velocity · precession period/amplitude · tilt $\theta(t)$ · upright time.

## 6b. Variables & control
- **Manipulated:** $I_3,\,m,\,l,\,a,\,\mu$
- **Controlled:** $\omega_0$ (most important) · $\theta_0$ · floor · no wind, etc.
- **Dependent:** the five metrics above
- **Modular test top:** separate an on-axis mass ($m\cdot l$ knob) from an on-radius mass ($I_3$ knob). Three ways to change only $I_3$ at fixed appearance (add a rim · internal redistribution · material swap).
- **Measurement/validation:** scale (mass) · knife-edge balance (center of mass) · bifilar pendulum (moment of inertia).

> ⚠️ Radius redistribution ($f_{rim}$, AR) also changes $I_1$. Lifetime and precession involve only $I_3$ (clean), but the critical angular velocity couples $I_1 I_3$, so we also track the combined quantity $mgl\,I_1/I_3^2$.

## 7. Pre-experiment
- Prediction: $t\propto I_3$ (linear), $t\propto 1/\mu$ (inverse).
- Friction-coefficient measurement: incline method $\mu=\tan\theta$ (block = tip material, surface = floor material).
- Assumptions/limits: Coulomb-friction approximation; air drag is secondary.
- **Fall definition:** spin lifetime = from release until **the body (excluding the tip) first touches the floor**. (This web app's simulation uses the same criterion — fall is judged at the angle where the *body's outer surface meets the floor*, not at 90° where the symmetry axis is horizontal.)
- **Initial-spin control:** a motor + a 3D-pen "motor cap" spins the top for a fixed time, then lifts off vertically, giving a consistent $\omega_0$ (avoiding the scatter of rubber-band / manual winding).

**Measuring ω — laser + Arduino + Fourier transform** (→ see the third tab for an animated explanation)
Half of the top's side is wrapped in **aluminium foil (bright)** and half in **black insulating tape (dark)**; while it spins a **laser** is aimed at it and a **light sensor + Arduino** record the reflected light. Bright/dark repeats once per revolution, so the signal frequency $f$ is the rotation rate, and the peak of a **short-time Fourier transform (STFT)** gives $\omega = 2\pi f$. Resolution $\Delta f = f_s/N$; Nyquist $f_s>2f_{max}$. In our rig the sensor read *higher when darker*.
> ⚠️ Current limitation: with the tip held in place, **the laser cannot follow the precession, so the error is large**. In the second semester we will refine the rig with a 3D printer / science-kit parts and improve laser alignment + STFT. For now we read **trends** only.

## 8. Real experiment & simulation
Three-stage integration: response surface → calibration map → hybrid reverse-design & validation.
$\theta(t)$ numerical integration (this web app's physics engine), Monte-Carlo design-space search, prediction vs measurement.
→ **Try it yourself on the [Simulation page].**

## 9. Roles & schedule
| When | What |
| --- | --- |
| ~early July | fix the stability definition & metrics |
| mid July | build the modular top & measurement rig; pre-experiment ($t$–$I_3$, $t$–$\mu$) |
| late July | finalize slides & simulation, **present in Japan**, joint study (build the hybrid) |

## 10. Outro
**Expected results:** quantitative relations of $I_3,\,l,\,\mu$; Korea–Japan shape–physics comparison; hybrid design & validation.
**Significance:** cultural exchange + physics/engineering fusion. **Future work:** make tip shape/material independent variables, top-collision stability, design-space expansion.

> 감사합니다 · Thank you · ありがとうございました
"""

RESEARCH_JA = r"""
# 韓日コマ回転安定性の研究
### 韓国のコマ（ペンイ）と日本のこまの比較による回転安定性最適化ハイブリッドコマの設計
**大田科学高 × 小松高 国際交流 Aチーム** — キム・ミョギョン · イ・ダムビ · チュ・ヨンジュン · イ・ジホ · 2026年7月末 日本にて発表

---

## 1. はじめに
大田科学高と小松高が国際交流の共同研究を行います。日本訪問の**前**に、韓国チームが単独で行うのは「**コマの回転安定性（倒れるまでの時間）に影響する物理的要因**」の解明です。その要因は**回転慣性 $I_3$** と**接地点–床の摩擦 $\mu$** で、これらと持続時間の相関を調べます。訪問**後**は両国合同で、その物理量に影響する構造を見つけ、**ハイブリッドコマ**を製作します。

## 2. テーマ紹介・選定背景
同じ物理（回転安定性）を異なる形で実現した二つの伝統 — 韓国のコマと日本のこま — を比べると、「**形 → 物理量 → 安定性**」という因果構造をきれいに分離して最適化できます。

**研究課題（3つ）**
1. 回転安定性を決める物理量は何か？（$I_3$, $\mu$, $l$ …）
2. どの形が有利か？ 韓国型（扁長）vs 日本型（扁球）
3. 二つの伝統を融合するとより安定するか？

**因果構造ダイアグラム**

> **形（構造）** ⟶ **物理量** ⟶ **回転安定性**
>
> 縦横比・質量分布・重心・接地点 ⟶ $I_3,\ I_1,\ l,\ \mu$ ⟶ 持続時間・$\omega_{crit}$・歳差・$\theta(t)$

## 3. コマの比較
| 項目 | 韓国の伝統コマ | 日本のベーゴマ／こま |
| --- | --- | --- |
| 材質 | 木が中心（下部に鉄芯） | 金属が中心（鋳鉄など高密度） |
| 形状 | 円錐・円筒・杭型（**扁長 prolate**） | 平たい円盤型（**扁球 oblate**） |
| 縦横比（幅/高さ） | 小さい（細長い） | 大きい（平たく広い） |
| 質量分布 | 軸中心に集中 → $I_3$ 小 | 外周に集中 → $I_3$ 大 |
| 重心 $l$ | 低い | 低く設計 |
| 接地点／摩擦 | 比較的高摩擦 | 低摩擦・長時間志向 |
| 駆動方式 | むちで**繰り返しエネルギー供給** | ひもを巻いて**一度に高速** |
| $I_3/I_1$ 比 | 小（sleeping に不利） | 大（sleeping に有利） |

> ⚠️ 形のばらつきが大きいため、実物試料の $m,\,l,\,I_3,\,I_1,$ 接地形状を直接測定し、設計空間上の点として比較します。「形が違えば物理量も違う」。

**代表的な種類** — 韓国：**マルペンイ**（平らな頭 → 円錐 → 尖った先端。最もよく長く回る型）· **チャングペンイ**（両端が尖る）· **チュルペンイ**（くびれ、ひもで投げる）· **パガジペンイ**（手でこする）。日本：**投げごま**（ひもで投げ単発高速）· **ベーゴマ**（金属・安定）· **鉄輪・喧嘩ごま**（外側の鉄輪で $I_3$ を最大化）· **博多・曲ごま**（細い鉄芯の木製、回転寿命が非常に長い）· **逆立ちごま**（回ると自ら反転する **tippe top**。歳差・転がり摩擦と直結）。

> 💡 コマが長く直立して回る状態を物理では **sleeping top**（$\omega>\omega_{crit}$）と呼びます。（韓国でもこれを「眠る」と表現するという話があるが**出典確認が必要**。）

## 4. 理論的背景
**(1) ジャイロ安定化** — 静止したコマは不安定平衡で倒れます。速く自転すると角運動量 $L = I_3\omega$ が生じ、重力トルク $\tau = mgl\sin\theta$ が $L$ に垂直に働いて $L$ の*向き*だけをゆっくり回す → **歳差運動**。

**(2) 臨界角速度（sleeping 条件）**
$$\omega_{crit} = \frac{2\sqrt{m\,g\,l\,I_1}}{I_3}$$
$\omega < \omega_{crit}$ になると $\theta$ が急増して倒れます。

**(3) 歳差角速度**
$$\Omega = \frac{m\,g\,l}{I_3\,\omega}$$
自転が遅いほど歳差は速くなります（$\Omega \propto 1/\omega$）。

**(4) 摩擦トルク（自転減衰の主因）** — 精密形／簡易形
$$\tau_{fric} = -\tfrac{2}{3}\,\mu\,m\,g\,a\,\cos\theta \qquad \tau_{fric}\approx -\mu\,m\,g\,a$$

**(5) 空気抵抗トルク** $\;\tau_{visc} = -b\,\omega_3,\quad \tau_{turb} = -c\,\omega_3^2$

**(6) 自転減衰と持続時間（事前実験の核心）** — 持続時間 $t_{life}$
$$I_3\frac{d\omega}{dt} = -\mu\,m\,g\,a \;\Rightarrow\; \omega(t)=\omega_0 - \frac{\mu m g a}{I_3}t \;\Rightarrow\; t_{life}\approx \frac{I_3\,\omega_0}{\mu\,m\,g\,a}$$

⟹ $t_{life}\propto I_3$（正の線形）, $\;t_{life}\propto 1/\mu$（反比例）

**(7) 慣性モーメントと平行軸の定理** $\;I=\int r^2\,dm,\quad I_1 = I_{1,cm} + m\,l^2$

**(8) 二線式振り子の測定式** $\;I = \dfrac{m\,g\,b^2\,T^2}{4\pi^2 L}$

> **想定 Q&A** — Q: なぜ速いと倒れない？ A: 角運動量が大きく、重力トルクは向きを変えるだけ（$\omega>\omega_{crit}$）。 Q: なぜ最後は倒れる？ A: 摩擦が $\omega$ を減らし $\omega<\omega_{crit}$ になるから。

## 5. 先行研究
| # | 先行研究 | 要点 |
| --- | --- | --- |
| 1 | ムン・ミオク(2012), 幼児教育研究 32(4), 445–464 | 韓国コマの構造：木の本体＋下部鉄芯、軸中心の質量 |
| 2 | ムン・ミオク／イ・ジイェ(2011), 幼児教育研究 31(4), 361–379 | マルペンイ扁長・下部質量集中・むち持続駆動 |
| 3 | Kaaronen 他（出典確認中） | ベーゴマ動力学 — 著者・年を確認後に正式記載 |
| 4 | キム・セヨン他(2012), 済州科学高 | 歳差の理論・実験比較の方法論（高速カメラ・Logger Pro） |
| 5 | Rod Cross(2013), *Am. J. Phys.* 81(4), 280–289, DOI 10.1119/1.4776195 | 接地点／床の形状 → 歳差・安定性、rising/tippe top |
| 6 | Bächer・Whiting・Bickel・Sorkine-Hornung, *Spin-It* (ACM TOG 33(4), SIGGRAPH 2014) | 内部の質量再配分による慣性モーメント最適化 |

> **先行研究の空白：** 韓日コマを*定量比較*し、さらにハイブリッドを検証した研究は少ない。本研究はシミュレーション＋実測でこの空白を埋める。

## 6. 実験設計
因果の鎖を二つの環に分けます。
- **物理 → 安定性（事前実験）：** 物理量を直接測定・操作し持続時間との関係を解明。
- **構造 → 物理（較正実験）：** 構造変数を変え物理量がどう変わるかを測定。

3段階計画：① 応答曲面の探索 → ② 較正マップ作成 → ③ ハイブリッドの逆設計・検証。
**従属変数5指標：** 回転持続時間 · 臨界角速度 · 歳差周期/振幅 · 傾き $\theta(t)$ · 直立時間。

## 6b. 変数の設定と統制
- **操作変数：** $I_3,\,m,\,l,\,a,\,\mu$
- **統制変数：** $\omega_0$（最重要）· $\theta_0$ · 床 · 無風 など
- **従属変数：** 上記5指標
- **モジュール式試験コマ：** 軸上質量（$m\cdot l$ つまみ）と半径上質量（$I_3$ つまみ）を分離。外形を固定して $I_3$ だけ変える3手法（縁の追加・内部再配分・材質交換）。
- **測定・検証：** 秤（質量）· ナイフエッジ平衡（重心）· 二線式振り子（慣性モーメント）。

> ⚠️ 半径の再配置（$f_{rim}$, AR）は $I_1$ も変えます。持続時間・歳差は $I_3$ のみで清浄ですが、臨界角速度は $I_1 I_3$ の結合なので結合量 $mgl\,I_1/I_3^2$ も併せて見ます。

## 7. 事前実験
- 予測：$t\propto I_3$（線形）, $t\propto 1/\mu$（反比例）。
- 摩擦係数の測定：斜面法 $\mu=\tan\theta$（ブロック＝接地材、面＝床材）。
- 仮定・限界：クーロン摩擦近似、空気抵抗は二次的。
- **倒れの定義：** コマを離した瞬間から**接地点を除いた底面が床に触れ始めた瞬間**までを回転持続時間とする。（本ウェブアプリのシミュレーションも同様に、対称軸が水平になる90°ではなく*本体の外面が床に触れる角*で倒れと判定します。）
- **初期角速度の統制：** モーター＋3Dペンで作った「モーター差込キャップ」で一定時間回した後、垂直に分離して $\omega_0$ を一定に揃える（ゴム・手巻き方式のばらつきを克服）。

**角速度の測定 — レーザー＋Arduino＋フーリエ変換**（→ 3番目のタブでアニメーション解説）
コマの側面を**半分はアルミ箔（明）、半分は黒い絶縁テープ（暗）**で覆い、回転させながら**レーザー**を当て、反射光を**光センサー＋Arduino**で測定する。1回転ごとに明暗が1回繰り返されるので信号周波数 $f$ が回転数であり、**（短時間）フーリエ変換(STFT)** のピークから $\omega = 2\pi f$ を得る。分解能 $\Delta f = f_s/N$、ナイキスト $f_s>2f_{max}$。本装置ではセンサー値が*暗いほど高く*出た。
> ⚠️ 現状の限界：接地点を固定した測定のため**レーザーが歳差に追従できず誤差が大きい**。2学期に3Dプリンター・科学キットで測定リグを精密化し、レーザー整列＋STFTで改善予定。現時点では**傾向**のみ解釈。

## 8. 本実験・シミュレーション
3段階の統合：応答曲面 → 較正マップ → ハイブリッドの逆設計・検証。
$\theta(t)$ の数値積分（本ウェブアプリの物理エンジン）、モンテカルロ設計空間探索、予測 vs 実測。
→ **[シミュレーションページ]で直接操作してみてください。**

## 9. 役割分担・日程
| 時期 | 内容 |
| --- | --- |
| ～7月初 | 安定性の定義・指標を確定 |
| 7月中 | モジュール式コマ・測定リグ製作、事前実験（$t$–$I_3$, $t$–$\mu$） |
| 7月末 | 発表資料・シミュレーション整理、**日本で発表**・合同共同研究（ハイブリッド製作） |

## 10. アウトロ
**期待される結果：** $I_3,\,l,\,\mu$ の定量関係、韓日の形–物理量比較、ハイブリッドの設計・検証。
**意義：** 文化交流＋物理・工学の融合。**今後の課題：** 接地点形状・材質の独立変数化、コマ衝突の安定性、設計空間の拡張。

> 감사합니다 · Thank you · ありがとうございました
"""

RESEARCH = {"ko": RESEARCH_KO, "en": RESEARCH_EN, "ja": RESEARCH_JA}
