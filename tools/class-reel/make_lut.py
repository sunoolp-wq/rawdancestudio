"""RAW 연습실 영상용 색감 LUT (색상은 그대로, 뿌연 느낌·벽 얼룩 줄이기, 피부 자연스럽게).
원장님 피드백(2026-11-05): 원본이 뿌옇다 / 빨간 조명을 다른 색으로 바꾸지 말 것 / 뒷벽(검정)의 발자국·얼룩이 안 보이게 /
사람이 너무 빨갛지 않게 자연스럽게.
python3 make_lut.py out.cube [--black 0.04] [--white 0.80] [--wall 1.0] [--sat 1.12] [--skin-amt 0.35] [--skin-tame 0.18]
"""
import argparse, numpy as np, colorsys
ap = argparse.ArgumentParser(); ap.add_argument("out")
ap.add_argument("--black", type=float, default=0.04)     # 뿌연 검정 걷기
ap.add_argument("--wall", type=float, default=1.0)      # 무채색 어두운 곳(검은 벽) 정리 강도
ap.add_argument("--white", type=float, default=0.80)
ap.add_argument("--sat", type=float, default=1.12)
ap.add_argument("--skin-amt", type=float, default=1.0)  # 보라빛·잿빛 피부를 살구색 쪽으로
ap.add_argument("--skin-tame", type=float, default=0.0) # 붉게 뜬 피부 채도 줄이기 (약하게)
a = ap.parse_args()

def pchip(xs, ys, x):  # 단조 곡선 (넘침 없이 부드럽게)
    xs, ys = np.asarray(xs, float), np.asarray(ys, float); h = np.diff(xs); d = np.diff(ys) / h
    m = np.zeros_like(ys); m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(xs) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]; m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    i = np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2); t = (x - xs[i]) / h[i]
    h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
    return h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1]

# 기본 밝기 곡선 (부드러운 S커브)
CX = [0, 0.10, 0.25, 0.50, 0.75, 1.0]
CY = [0, 0.08, 0.235, 0.52, 0.79, 1.0]   # 중간 톤 살짝 밝게 (사람이 칙칙하지 않게)
# 검은 벽용 추가 곡선: 무채색이고 어두운 곳만 더 눌러서 발자국·얼룩 차이를 없앰 (색 있는 파란 벽·조명·피부는 제외)
WX = [0, 0.05, 0.10, 0.15, 0.20, 0.26, 1.0]
WY = [0, 0.016, 0.040, 0.085, 0.165, 0.26, 1.0]   # 0.26 위(사람 피부·옷 밝은 쪽)는 건드리지 않음

def grade(rgb):
    Y0 = 0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2]
    L = np.clip((Y0 - a.black) / (a.white - a.black), 0, 1)
    Y1 = pchip(CX, CY, L)
    # 무채색 정도 (원본 채도 낮을수록 1)
    mx, mn = rgb.max(1), rgb.min(1); S0 = (mx - mn) / np.maximum(mx, 1e-4)
    neutral = np.clip(1 - (S0 - 0.18) / 0.17, 0, 1) * np.clip(1 - (Y1 - 0.22) / 0.08, 0, 1) * a.wall
    Y1 = Y1 + (pchip(WX, WY, Y1) - Y1) * neutral
    x = rgb * (Y1 / np.maximum(Y0, 1e-4))[:, None]          # 밝기만 바꾸고 색 비율 유지
    x = np.clip(np.nan_to_num(x), 0, None); over = x.max(1, keepdims=True); x = np.where(over > 1, x / np.maximum(over, 1e-6), x)
    Y = (0.2126 * x[:, 0] + 0.7152 * x[:, 1] + 0.0722 * x[:, 2])[:, None]
    x = np.clip(Y + (x - Y) * a.sat, 0, 1)
    hsv = np.array([colorsys.rgb_to_hsv(*q) for q in x]); H, S, V = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
    wv = np.clip((V - 0.12) / 0.12, 0, 1) * np.clip(1 - (V - 0.92) / 0.08, 0, 1)
    # (1) 보라 조명 아래 피부(연보라·분홍, 색상 240~45도, 채도 0.08~0.45, 밝음) → 살구색(22도) 쪽으로 확실히, 채도 채우기
    #     바닥·벽은 같은 보라빛이라도 어두워서(밝기 0.4 아래) 제외, 흰 옷은 채도가 아주 낮아서 제외
    d = (H - 327 + 180) % 360 - 180; wp = np.clip(1 - (np.abs(d) - 76) / 10, 0, 1)   # 251~43도 (파란빛 흰옷 230~245도는 제외)
    ws = np.clip((S - 0.07) / 0.06, 0, 1) * np.clip(1 - (S - 0.45) / 0.12, 0, 1)
    wb = np.clip((V - 0.38) / 0.12, 0, 1) * np.clip(1 - (V - 0.70) / 0.10, 0, 1)   # 아주 밝은 흰옷·간판 빛 제외
    w = np.clip(wp * ws * wb * a.skin_amt, 0, 1)
    dh = (22 - H + 180) % 360 - 180; H = (H + dh * 0.75 * w) % 360
    S = S + (np.maximum(S, 0.34) - S) * w * 0.85; V = np.clip(V * (1 + 0.04 * w), 0, 1)
    # (2) 붉게 뜬 피부(0~35도, 채도 0.30~0.75) → 채도 살짝 낮추고 약간 노랗게 (진한 빨간 조명·신발은 채도가 더 높아 제외)
    d2 = (H - 15 + 180) % 360 - 180; wr = np.clip(1 - (np.abs(d2) - 20) / 15, 0, 1)
    wsr = np.clip((S - 0.28) / 0.08, 0, 1) * np.clip(1 - (S - 0.72) / 0.10, 0, 1)
    t = wr * wsr * wv * a.skin_tame
    S = S * (1 - t); H = (H + 6 * t / max(a.skin_tame, 1e-6) * (d2 < 10)) % 360
    return np.array([colorsys.hsv_to_rgb(h / 360, s, v) for h, s, v in zip(H, np.clip(S, 0, 1), V)])

N = 33; g = np.linspace(0, 1, N)
pts = np.array([[r, gg, b] for b in g for gg in g for r in g])
out = np.clip(grade(pts), 0, 1)
with open(a.out, "w") as f:
    f.write('TITLE "RAW studio grade v3"\nLUT_3D_SIZE 33\n')
    for v in out: f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
print(a.out)
