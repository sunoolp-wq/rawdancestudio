"""썸네일 자동 (원장님 2026-11-18): 춤이 가장 역동적인 순간 + TRACKPAD 글자가 다 켜진 상태
세로(1080x1920, 인스타 릴스) · 가로(1920x1080, 유튜브 풀버전) 두 장
사용: python thumb.py --video 결과.mp4 --a 시작초 --b 끝초 --title 강사 --name 장르 [--track 곡명] --out-v 세로.jpg --out-h 가로.jpg
      [--src-h 가로원본.mp4 --src-off 초]  : 결과가 세로(쌤 따라가기·3분할)일 때 가로 썸네일은 원본의 같은 순간에서 (원본 시각 = src-off + 결과 시각)
고르는 법: 움직임이 큰 순간 상위 몇 곳 → 그 주변 ±0.5초에서 가장 선명한(흔들림 적은) 장면. 너무 흐리면 다음 후보
"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
for k in ("video", "title", "name", "track", "out-v", "out-h", "src-h"): ap.add_argument("--" + k)
for k in ("a", "b", "src-off"): ap.add_argument("--" + k, type=float, default=0.0)
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
say = lambda s: print(s, flush=True)

def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "csv=p=0:s=x", f],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL).stdout.split()
    w, h = map(int, r[0].split("x")[:2]); return w, h, float(r[-1])

def frames(f, t0, dur, fps, w=160):
    """t0부터 dur초 동안 fps장/초 흑백 작은 장면들"""
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", f, "-vf", f"fps={fps},scale={w}:-2,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, stdin=subprocess.DEVNULL)
    W, H, _ = probe(f); h = int(round(W and H * w / W / 2)) * 2
    x = np.frombuffer(r.stdout, np.uint8); n = len(x) // (w * h)
    return x[:n * w * h].reshape(n, h, w).astype(np.float32)

def grab(f, t):
    p = tempfile.mktemp(suffix=".png")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{max(0, t):.3f}", "-i", f, "-frames:v", "1", p], stdin=subprocess.DEVNULL)
    im = Image.open(p).convert("RGB"); os.remove(p); return im

def sharp(g):   # 라플라시안 분산: 클수록 또렷
    l = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(l.var())

# 1) 움직임이 큰 순간 고르기
W0, H0, VD = probe(a.video)
A, B = max(0.0, a.a), min(VD - 0.2, a.b if a.b > a.a else VD)
MF = 5; g = frames(a.video, A, B - A, MF)
mo = np.r_[0, np.abs(np.diff(g, axis=0)).mean((1, 2))]
mo = np.convolve(mo, np.ones(MF) / MF, "same")
peaks = []
for i in np.argsort(mo)[::-1]:
    t = A + i / MF
    if t < A + 0.5 or t > B - 0.5: continue
    if all(abs(t - p) > 1.5 for p in peaks): peaks.append(t)
    if len(peaks) >= 4: break
if not peaks: peaks = [(A + B) / 2]
best = None
for rank, t in enumerate(peaks):
    gg = frames(a.video, t - 0.5, 1.0, 15, 480)
    if not len(gg): continue
    sh = [sharp(x) for x in gg]; j = int(np.argmax(sh))
    cand = (sh[j] * (1 - 0.12 * rank), t - 0.5 + j / 15)       # 움직임 순위가 높을수록 조금 우대
    if best is None or cand[0] > best[0]: best = cand
T = best[1]; say(f"썸네일 장면: {T:.2f}초 (움직임 큰 순간 {', '.join(f'{p:.1f}' for p in peaks)}초 중 가장 또렷한 것)")

# 2) 장면 → 세로·가로
def cover(im, W, H):
    s = max(W / im.width, H / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2; return im.crop((x, y, x + W, y + H))

def people_center(im):
    """가로 장면에서 사람들이 모인 가운데 x (0~1). YOLO가 없거나 못 찾으면 가운데"""
    try:
        from ultralytics import YOLO
        r = YOLO(os.path.join(HERE, "yolo11s.pt"), verbose=False)(np.array(im), classes=[0], verbose=False)[0]
        bx = r.boxes.xyxy.cpu().numpy(); cf = r.boxes.conf.cpu().numpy()
        if len(bx):
            ar = (bx[:, 2] - bx[:, 0]) * (bx[:, 3] - bx[:, 1]) * cf
            k = int(np.argmax(ar)); return float((bx[k, 0] + bx[k, 2]) / 2 / im.width)   # 가장 크게 보이는 사람(보통 맨 앞 쌤)
    except Exception as e: say(f"(사람 찾기 건너뜀: {e})")
    return 0.5

fr = grab(a.video, T)
if fr.height > fr.width:     # 결과가 세로
    v = cover(fr, 1080, 1920)
    hsrc = grab(a.src_h, a.src_off + T) if a.src_h else None
    if hsrc is not None: h = cover(hsrc, 1920, 1080)
    else:   # 가로 원본이 없으면: 흐린 배경 + 가운데 세로 장면
        h = cover(fr, 1920, 1080).filter(ImageFilter.GaussianBlur(40)); fg = fr.resize((round(fr.width * 1080 / fr.height), 1080), Image.LANCZOS)
        h.paste(fg, ((1920 - fg.width) // 2, 0))
else:                         # 결과가 가로
    h = cover(fr, 1920, 1080)
    cx = people_center(fr); cw = fr.height * 9 / 16; x0 = int(min(max(0, cx * fr.width - cw / 2), fr.width - cw))
    v = cover(fr.crop((x0, 0, int(x0 + cw), fr.height)), 1080, 1920)

# 3) TRACKPAD 글자 (다 켜진 상태) 얹기
def overlay(bg, W, H):
    if not (a.title or "").strip(): return bg
    p = tempfile.mktemp(suffix=".png")
    cmd = ["node", os.path.join(HERE, "add_title.js"), "--still", p, "--w", str(W), "--h", str(H), "--title", a.title, "--name", a.name or ""]
    if a.track: cmd += ["--track", a.track]
    subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if not os.path.exists(p): say("자막 그리기 실패 → 글자 없이"); return bg
    t = Image.open(p).convert("RGBA"); os.remove(p)
    out = bg.convert("RGBA"); out.alpha_composite(t); return out.convert("RGB")

if a.out_v: overlay(v, 1080, 1920).save(a.out_v, quality=95); say(a.out_v)
if a.out_h: overlay(h, 1920, 1080).save(a.out_h, quality=95); say(a.out_h)
