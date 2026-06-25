from vpython import *

scene = canvas(title='팽이 세차운동 — 슬라이더로 조절',
               width=860, height=560, background=color.gray(0.12),
               center=vector(0,1.6,0), forward=vector(-0.4,-0.3,-1))

# ════════ 조절 가능한 파라미터 (슬라이더로 변경) ════════
P = {
    'spin0':  30.0,   # 초기 자전 속도
    'theta0': 25.0,   # 초기 기울기(도)
    'I1':     1.0,    # 가로축 관성모멘트
    'I3':     0.4,    # 자전축 관성모멘트
    'fric_spin': 0.06,# 받침점 마찰
    'fric_air':  0.04,# 공기저항
}
m, g, L = 1.0, 9.8, 1.0   # 고정값

# ── 시뮬레이션 상태 (전역) ──
state = {}
def reset_sim():
    state['theta'] = radians(P['theta0'])
    state['phi'] = 0.0
    state['psi'] = 0.0
    state['theta_dot'] = 0.0
    state['phi_dot'] = 0.0
    state['psi_dot'] = P['spin0']
    state['t'] = 0.0
    state['done'] = False
    state['prev'] = (state['theta'], 0.0, 0.0)
    # 팽이를 초기 자세로 리셋
    top.axis = vector(0,1,0)        # 기준 자세로 되돌림
    top.up = vector(0,0,1)
    top.rotate(angle=state['theta'], axis=vector(0,0,1), origin=vector(0,0,0))
    tip.clear_trail()

def axis_dir(th, ph):
    return vector(sin(th)*sin(ph), cos(th), sin(th)*cos(ph))

# ════════ 슬라이더 UI ════════
sliders = {}

def make_slider(key, lo, hi, label_fmt):
    """슬라이더 한 줄 생성"""
    cap = wtext(text='')
    def update(s):
        P[key] = s.value
        cap.text = label_fmt.format(s.value)
    sld = slider(min=lo, max=hi, value=P[key], length=260, bind=update, right=15)
    cap.text = label_fmt.format(P[key])
    sliders[key] = sld
    scene.append_to_caption('\n\n')
    return cap

scene.append_to_caption('\n')
make_slider('spin0',  5,  60,  '초기 자전속도: {:.0f}')
make_slider('theta0', 5,  80,  '초기 기울기: {:.0f}°')
make_slider('I1',     0.3, 3.0,'I₁ (가로 관성): {:.2f}')
make_slider('I3',     0.1, 1.5,'I₃ (자전 관성): {:.2f}')
make_slider('fric_spin', 0.0, 0.3, '받침점 마찰: {:.3f}')
make_slider('fric_air',  0.0, 0.3, '공기저항: {:.3f}')

def on_restart(b):
    reset_sim()
scene.append_to_caption('\n')
button(text='▶ 새 값으로 다시 돌리기', bind=on_restart)
scene.append_to_caption('   ')

# ── 바닥 / 기준선 / 팽이 ──
cylinder(pos=vector(0,0,0), axis=vector(0,-0.15,0), radius=4, color=color.gray(0.35))
cylinder(pos=vector(0,0,0), axis=vector(0,4,0), radius=0.012, color=color.gray(0.5))

body = cone(pos=vector(0,2.4,0), axis=vector(0,-2.4,0), radius=1.2, color=vector(0.9,0.4,0.1))
disk = cylinder(pos=vector(0,2.1,0), axis=vector(0,0.5,0), radius=1.35, color=vector(0.85,0.1,0.1))
stem = cylinder(pos=vector(0,2.6,0), axis=vector(0,1.2,0), radius=0.09, color=color.gray(0.7))
mark = box(pos=vector(0,1.9,0.95), size=vector(0.45,0.32,0.95), color=color.cyan)
top = compound([body, disk, stem, mark])

tip = sphere(radius=0.06, color=color.yellow,
             make_trail=True, trail_color=color.yellow, retain=700)
info = label(pos=vector(0,4.4,0), text='', height=14, box=False, color=color.white)

dt = 0.002
reset_sim()

# ════════ 메인 루프 ════════
while True:
    rate(300)
    if state['done']:
        continue

    th, ph, ps = state['theta'], state['phi'], state['psi']
    thd, phd, psd = state['theta_dot'], state['phi_dot'], state['psi_dot']
    I1, I3 = P['I1'], P['I3']

    s, c = sin(th), cos(th)
    if s < 1e-4: s = 1e-4

    spin_term = psd + phd*c
    theta_ddot = ((I1*phd**2*c - I3*spin_term*phd)*s + m*g*L*s) / I1
    phi_ddot   = (I3*spin_term*thd - 2*I1*phd*thd*c) / (I1*s)
    psi_ddot   = -phi_ddot*c + phd*thd*s

    # 마찰
    psi_ddot   -= P['fric_spin'] * psd
    phi_ddot   -= P['fric_air']  * phd
    theta_ddot -= P['fric_air']  * thd

    # 적분
    thd += theta_ddot*dt; phd += phi_ddot*dt; psd += psi_ddot*dt
    th  += thd*dt;        ph  += phd*dt;       ps  += psd*dt

    if th >= radians(89):
        th = radians(89)
        state['done'] = True
        info.text = f'쓰러짐 — {state["t"]:.1f}초 버팀 (다시 돌리기 누르세요)'
        state.update(theta=th, phi=ph, psi=ps,
                     theta_dot=thd, phi_dot=phd, psi_dot=psd)
        continue

    # 화면 반영
    pth, pph, pps = state['prev']
    top.rotate(angle=(ps-pps), axis=axis_dir(th,ph), origin=vector(0,0,0))
    top.rotate(angle=(ph-pph), axis=vector(0,1,0),   origin=vector(0,0,0))
    tilt_axis = vector(cos(ph), 0, -sin(ph))
    top.rotate(angle=(th-pth), axis=tilt_axis, origin=vector(0,0,0))

    tip.pos = 3.6*axis_dir(th,ph)
    state['t'] += dt
    state.update(theta=th, phi=ph, psi=ps,
                 theta_dot=thd, phi_dot=phd, psi_dot=psd, prev=(th,ph,ps))
    info.text = (f't={state["t"]:4.1f}s   자전={psd:5.1f}   '
                 f'세차={phd:5.2f}   기울기={degrees(th):4.1f}°')