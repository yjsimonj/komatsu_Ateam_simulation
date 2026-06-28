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
**대전과학고 × 고마쯔고 국제교류 A조** — 김묘경 · 이담비 · 주영준 · 이지호 · 발표 2026년 8월, 일본

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
| 7월 중 | 모듈형 팽이·측정 리그 제작 |
| 7월 말 | 사전실험 ($t$–$I_3$, $t$–$\mu$) |
| 8월 초 | 발표 자료·시뮬레이션 정리 |
| 8월 | 일본 발표·합동 공동연구(하이브리드 제작) |

## 10. 아웃트로
**기대결과:** $I_3,\,l,\,\mu$ 의 정량 관계, 한·일 형태–물리량 비교, 하이브리드 설계·검증.
**의의:** 문화 교류 + 물리·공학 융합. **향후 과제:** 팁 형상·재질 독립변수화, 팽이 충돌 안정성,
설계공간 확장.

> 감사합니다 · Thank you · ありがとうございました
"""

RESEARCH_EN = r"""
# Korea–Japan Spinning-Top Rotational Stability Study
### Designing a hybrid top by comparing the Korean *paengi* and the Japanese *koma*
**Daejeon Science HS × Komatsu HS, Team A** — Presented Aug 2026, Japan

## 1. Intro
Before visiting Japan, the Korean team independently identifies the **physical factors that govern a
top's rotational stability** (time-to-fall): the **spin moment of inertia $I_3$** and the
**tip–floor friction $\mu$**. After the visit, both teams jointly design a **hybrid top**.

## 2. Topic & Motivation
Two traditions realize the *same physics* with *different shapes*, letting us cleanly separate the
causal chain **shape → physical quantity → stability**.

$$\boxed{\text{Shape}}\to\boxed{\text{Physical quantity}}\to\boxed{\text{Stability}}$$

## 4. Theory (key equations)
$$\omega_{crit}=\frac{2\sqrt{mgl\,I_1}}{I_3},\qquad \Omega=\frac{mgl}{I_3\omega},\qquad
t_{life}\approx\frac{I_3\omega_0}{\tfrac23\mu mga}$$
$$\tau_{fric}=-\tfrac23\mu mga\cos\theta,\qquad \tau_{air}=-b\omega_3-c\omega_3^2$$
$$\Rightarrow\ t_{life}\propto I_3,\qquad t_{life}\propto 1/\mu$$

A fast top **sleeps** (stays upright) because its angular momentum $L=I_3\omega$ is large; gravity only
*reorients* $L$ (precession). Friction slowly reduces $\omega$; once $\omega<\omega_{crit}$, the tilt
$\theta$ grows rapidly and the top falls.

## 3. Korean vs Japanese
Korean: wooden, **prolate** (tall), axis-concentrated mass (small $I_3$), higher friction, whip-driven.
Japanese: metal, **oblate** (flat/wide), rim-concentrated mass (large $I_3$), low friction, string-driven.
A long upright spin is the physics *"sleeping top"* state ($\omega>\omega_{crit}$). (A Korean term "잠을 잔다" is sometimes cited for this — source to be confirmed.)
Japanese koma range from *beigoma* (metal) to the self-inverting *tippe top* (逆立ちごま).

## Measuring ω — laser + Arduino + FFT
Half of the top is wrapped in **aluminium foil** (bright) and half in **black tape** (dark); a **laser**
hits the edge while it spins and a **light-sensor + Arduino** record the reflected light (one cycle per
turn). A **short-time Fourier transform** of that signal peaks at the rotation frequency $f$, giving
$\omega=2\pi f$. *Fall* is defined as the moment the body (not the tip) first touches the floor — the
simulation uses the same criterion. See the **"How we measured ω" page** for an animated explanation.

## 5–10 Prior work, design, pre-experiment, simulation, schedule, outro
Prior work: Moon (2012, *J. Early Childhood Educ.* 32(4)), Moon & Lee (2011, 31(4)), Kaaronen et al.,
Kim et al. (2012), Rod Cross (2013, *Am. J. Phys.* 81(4), DOI 10.1119/1.4776195),
Bächer et al. *Spin-It* (ACM TOG 33(4), SIGGRAPH 2014). Gap: few studies *quantitatively compare*
Korea/Japan **and** validate a hybrid. We fill it with simulation + measurement.
**Try the Simulation page to manipulate the structure variables yourself.**
"""

RESEARCH_JA = r"""
# 韓日コマ回転安定性の研究
### 韓国のコマと日本のこまの比較によるハイブリッドコマ設計
**大田科学高 × 小松高 国際交流 Aチーム** — 2026年8月 日本にて発表

## はじめに
日本訪問の**前**に、韓国チームは「コマの回転安定性（倒れるまでの時間）を左右する物理的要因」を
明らかにします。その要因は**回転慣性 $I_3$** と**接地点–床の摩擦 $\mu$** です。訪問**後**は両チームで
**ハイブリッドコマ**を設計します。

## 主要な式
$$\omega_{crit}=\frac{2\sqrt{mgl\,I_1}}{I_3},\qquad \Omega=\frac{mgl}{I_3\omega},\qquad
t\approx\frac{I_3\omega_0}{\tfrac23\mu mga}$$
$$\Rightarrow\ t\propto I_3,\qquad t\propto 1/\mu$$

韓国＝木製・**扁長(prolate)**・軸集中・高摩擦・むち駆動。
日本＝金属・**扁球(oblate)**・外周集中・低摩擦・ひも駆動。
**シミュレーションページで構造変数を操作してみてください。**
"""

RESEARCH = {"ko": RESEARCH_KO, "en": RESEARCH_EN, "ja": RESEARCH_JA}
