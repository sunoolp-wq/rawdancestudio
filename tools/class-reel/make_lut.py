"""RAW 연습실 영상용 색감 LUT 만들기 (색상은 그대로 두고 뿌연 느낌만 걷어내는 보정).
원장님 피드백(2026-11-05): 원본은 뿌옇다 / 빨간 조명을 다른 색으로 바꾸지 말 것 / 피부톤은 살아 있게.
python3 make_lut.py out.cube [--black 0.04] [--white 0.80] [--gamma 1.08] [--sat 1.25] [--skin-amt 1.0]
"""
import argparse, numpy as np, colorsys
ap = argparse.ArgumentParser(); ap.add_argument("out")
ap.add_argument("--black", type=float, default=0.040)   # 이 밝기 이하는 검정으로 (뿌연 검정 걷기)
ap.add_argument("--white", type=float, default=0.80)    # 이 밝기를 흰색 쪽으로 늘림
ap.add_argument("--gamma", type=float, default=1.08)    # 1보다 크면 중간 톤 살짝 깊게
ap.add_argument("--sat", type=float, default=1.25)      # 채도 (색상은 그대로)
ap.add_argument("--skin-amt", type=float, default=1.0)  # 피부톤 살리기 강도 (0=끔)
a = ap.parse_args()

def grade(rgb):
    # 1) 레벨: 세 채널 같은 비율로 → 색상 안 바뀜
    x = np.clip((rgb - a.black) / (a.white - a.black), 0, 1)
    # 2) 부드러운 S커브 + 감마 (밝기만)
    s = x * x * (3 - 2 * x); x = 0.65 * x + 0.35 * s
    x = np.power(np.clip(x, 0, 1), a.gamma)
    # 3) 채도: 밝기 기준으로 색 차이만 키움 (색상 유지)
    Y = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    k = a.sat
    x = Y + (x - Y) * k
    # 4) 피부톤 살리기: 연습실 보라·파랑 조명 아래 피부는 연보라~분홍(색상 250~360~50도, 채도 낮음~중간)으로 찍힘.
    #    그 영역만 색상을 살구색(20도) 쪽으로 조금 돌리고, 채도를 살짝 채우고, 조금 밝게. 진한 조명색(채도 높음)·검정·흰색은 건드리지 않음.
    flat = np.clip(x.reshape(-1, 3), 0, 1)
    hsv = np.array([colorsys.rgb_to_hsv(*q) for q in flat])
    H, S, V = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
    d = (H - 330 + 180) % 360 - 180                                   # 330도 기준 거리 (250~50도 포함)
    wh = np.clip(1 - (np.abs(d) - 60) / 25, 0, 1)
    ws = np.clip((S - 0.04) / 0.06, 0, 1) * np.clip(1 - (S - 0.40) / 0.15, 0, 1)
    wv = np.clip((V - 0.15) / 0.12, 0, 1) * np.clip(1 - (V - 0.92) / 0.08, 0, 1)
    w = wh * ws * wv * a.skin_amt
    dh = (20 - H + 180) % 360 - 180                                    # 살구색 쪽으로
    H2 = (H + dh * 0.45 * w) % 360
    S2 = S + (np.maximum(S, 0.20) - S) * w * 0.8
    V2 = np.clip(V * (1 + 0.07 * w), 0, 1)
    x = np.array([colorsys.hsv_to_rgb(h / 360, s_, v) for h, s_, v in zip(H2, S2, V2)]).reshape(x.shape)
    return np.clip(x, 0, 1)

N = 33; g = np.linspace(0, 1, N)
pts = np.array([[r, gg, b] for b in g for gg in g for r in g])   # .cube: R가 가장 빨리 변함
out = grade(pts.reshape(N, N, N, 3)).reshape(-1, 3)
with open(a.out, "w") as f:
    f.write('TITLE "RAW studio grade"\nLUT_3D_SIZE 33\n')
    for v in out: f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
print(a.out)
