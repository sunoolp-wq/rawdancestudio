"""가로 수업 영상 → 세로 9:16, 선생님(맨 앞·가장 큰 사람)이 화면 가운데 오도록 따라가며 자르기.
사용: python3 follow_crop.py --video 원본.mp4 --start 5 --dur 15 --out 세로.mp4 [--debug 경로.png]
필요: opencv-python-headless, numpy, ffmpeg
"""
import argparse, subprocess, tempfile, os
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("--video"); ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=15)
ap.add_argument("--out"); ap.add_argument("--debug")
a = ap.parse_args()

cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cw = int(round(H * 9 / 16)) // 2 * 2
if W <= cw + 2:  # 이미 세로 영상
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-t", str(a.dur), "-i", a.video,
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-c:v", "libx264", "-crf", "17",
                    "-c:a", "aac", "-b:a", "192k", a.out], check=True)
    raise SystemExit

SW = 960; sc = SW / W; SH = int(H * sc)
hog = cv2.HOGDescriptor(); hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
cap.set(cv2.CAP_PROP_POS_MSEC, a.start * 1000)
n = int(a.dur * fps); step = max(1, int(round(fps / 8)))
ts, xs = [], []; prev = None; prev_gray = None; last = SW / 2
for i in range(n):
    ok, fr = cap.read()
    if not ok: break
    if i % step: continue
    small = cv2.resize(fr, (SW, SH)); gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    boxes, w = hog.detectMultiScale(small, winStride=(8, 8), padding=(8, 8), scale=1.05)
    cand = []
    for (x, y, bw, bh), s in zip(boxes, np.ravel(w) if len(w) else []):
        if bh < SH * 0.28 or s < 0.3: continue
        cx = x + bw / 2
        # 앞에 선 사람(큰 상자·아래쪽)일수록, 직전 위치와 가까울수록 점수
        if abs(cx - SW / 2) > SW * 0.32: continue  # 선생님은 보통 앞 가운데 → 양 끝 사람은 제외
        score = (bh / SH * 2.0 + (y + bh) / SH
                 - abs(cx - SW / 2) / SW * 3.0               # 가운데일수록
                 - (abs(cx - last) / SW * 2.5 if prev is not None else 0))  # 직전 위치와 가까울수록
        cand.append((score, cx))
    if cand:
        cx = max(cand)[1]
    elif prev_gray is not None:  # 사람을 못 찾으면 움직임 중심
        d = cv2.absdiff(gray, prev_gray); d = cv2.GaussianBlur(d, (21, 21), 0)
        m = (d > 18).astype(np.uint8)
        cols = m.sum(0).astype(float)
        if cols.sum() > SH * 3:
            k = np.arange(SW); win = np.exp(-((k - last) / (SW * 0.25)) ** 2)  # 직전 위치 근처 움직임 우선
            cx = float((cols * win * k).sum() / max((cols * win).sum(), 1))
        else:
            cx = last
    else:
        cx = SW / 2
    prev_gray = gray; prev = cx; last = cx
    ts.append(i / fps); xs.append(cx / sc)
cap.release()

ts = np.array(ts); xs = np.array(xs)
# 튀는 값 제거 + 부드럽게 (중앙값 → 이동평균), 너무 빨리 움직이지 않게
k = 5
med = np.array([np.median(xs[max(0, j - k // 2): j + k // 2 + 1]) for j in range(len(xs))])
win = 11  # 약 1.4초 이동평균 (8장/초)
pad = np.pad(med, (win // 2, win // 2), mode="edge")
sm = np.convolve(pad, np.ones(win) / win, mode="valid")
tf = np.arange(0, a.dur, 1 / fps)
cxf = np.interp(tf, ts, sm)
maxv = W * 0.22 / fps  # 초당 최대 이동(화면 폭의 22%)
for j in range(1, len(cxf)):
    cxf[j] = cxf[j - 1] + np.clip(cxf[j] - cxf[j - 1], -maxv, maxv)
xpos = np.clip(cxf - cw / 2, 0, W - cw).astype(int) // 2 * 2

cmd = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
for t, x in zip(tf, xpos): cmd.write(f"{t:.4f} crop@c x {x};\n")
cmd.close()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-t", str(a.dur), "-i", a.video,
                "-vf", f"sendcmd=f={cmd.name},crop@c=w={cw}:h={H}:x={xpos[0]}:y=0,scale=1080:1920",
                "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", a.out], check=True)
os.unlink(cmd.name)
print(a.out, f"crop {cw}x{H}, x {xpos.min()}~{xpos.max()}")
