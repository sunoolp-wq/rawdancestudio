"""가로 수업 영상 → 세로 9:16, 선생님을 YOLO로 찾아 끝까지 따라가며 자르기.
사용: python follow_yolo.py --video 원본.mp4 --start 5 --dur 15 --out 세로.mp4 \
        [--pick-x 0.5] [--pick-t 0.5] [--check 확인.jpg]
  --pick-x : 선생님이 --pick-t 초에 화면 가로 어디쯤 있는지 (0=왼쪽, 0.5=가운데, 1=오른쪽). 기본 가운데
  --check  : 선생님으로 잡은 사람(보라 상자)과 자른 창(흰 선)을 표시한 확인용 사진
필요: ultralytics(YOLO11), opencv, numpy, ffmpeg. 모델 yolo11s.pt (처음 실행 때 자동 다운로드)
"""
import argparse, subprocess, tempfile, os
import numpy as np, cv2
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--video"); ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=15)
ap.add_argument("--out"); ap.add_argument("--pick-x", type=float, default=0.5); ap.add_argument("--pick-t", type=float, default=0.5)
ap.add_argument("--check"); ap.add_argument("--lut"); ap.add_argument("--denoise", type=float, default=1.0); ap.add_argument("--shape", default="auto", choices=["auto", "tall", "wide"]); ap.add_argument("--model", default=os.path.join(os.path.dirname(__file__), "yolo11s.pt"))
a = ap.parse_args()

# 먼저 쓸 구간만 H.264로 잘라 둔다 (AV1 등 OpenCV가 못 읽는 코덱 대비, 이후 시작 0초 기준)
seg = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-t", str(a.dur), "-i", a.video,
                "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", seg], check=True)
a.video, a.start = seg, 0.0
cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cw = int(round(H * 9 / 16)) // 2 * 2
SW = 1280; sc = SW / W; SH = int(round(H * sc))
model = YOLO(a.model if os.path.exists(a.model) else "yolo11s.pt")

def hist(img, b):  # 상체 색 분포 (옷 색으로 같은 사람 다시 찾기)
    x1, y1, x2, y2 = [int(v) for v in b]
    y2 = int(y1 + (y2 - y1) * 0.6); x1, x2 = int(x1 + (x2 - x1) * .2), int(x2 - (x2 - x1) * .2)
    roi = img[max(y1, 0):max(y2, 1), max(x1, 0):max(x2, 1)]
    if roi.size == 0: return None
    h = cv2.calcHist([cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [12, 6, 6], [0, 180, 0, 256, 0, 256])
    return cv2.normalize(h, h).flatten()

cap.set(cv2.CAP_PROP_POS_MSEC, a.start * 1000)
n = int(a.dur * fps); step = max(1, int(round(fps / 10)))
rec = []  # (t, boxes[N,4], ids[N], frame_small)
for i in range(n):
    ok, fr = cap.read()
    if not ok: break
    if i % step: continue
    small = cv2.resize(fr, (SW, SH))
    r = model.track(small, persist=True, classes=[0], imgsz=1280, conf=0.25, verbose=False, tracker="bytetrack.yaml")[0]
    bx = r.boxes.xyxy.cpu().numpy() if r.boxes is not None else np.zeros((0, 4))
    ids = r.boxes.id.cpu().numpy().astype(int) if (r.boxes is not None and r.boxes.id is not None) else -np.ones(len(bx), int)
    rec.append((i / fps, bx, ids, small))
cap.release()

# 1) 선생님 정하기: pick-t 근처 프레임에서 pick-x에 가깝고 크게(앞에) 보이는 사람
j0 = int(np.argmin([abs(t - a.pick_t) for t, *_ in rec]))
t0, bx0, id0, im0 = rec[j0]
px = a.pick_x * SW
sc0 = [((b[3] - b[1]) / SH) * 1.5 - abs((b[0] + b[2]) / 2 - px) / SW * 3 for b in bx0]
k = int(np.argmax(sc0)); tid = id0[k]; tb = bx0[k]; th = hist(im0, tb)
cx = [None] * len(rec); cx[j0] = (tb[0] + tb[2]) / 2; boxes_for_check = {j0: tb}; bw_list = [(tb[2] - tb[0]) / sc]

def follow(order):
    global tid, th
    last_b = tb.copy(); cur = tid; hcur = th
    for j in order:
        t, bx, ids, im = rec[j]
        if not len(bx): continue
        if cur in ids:
            b = bx[list(ids).index(cur)]
        else:  # 번호를 잃으면 옷 색 + 위치 + 크기로 다시 찾기
            lc = (last_b[0] + last_b[2]) / 2; lh = last_b[3] - last_b[1]
            best, bs = None, -1e9
            for b, i_ in zip(bx, ids):
                h = hist(im, b); sim = cv2.compareHist(hcur, h, cv2.HISTCMP_CORREL) if h is not None else 0
                s = sim * 2 - abs((b[0] + b[2]) / 2 - lc) / SW * 4 - abs((b[3] - b[1]) - lh) / SH * 2
                if s > bs: best, bs, bid = b, s, i_
            if bs < -0.6: continue
            b, cur = best, bid
        cx[j] = (b[0] + b[2]) / 2; last_b = b; boxes_for_check[j] = b; bw_list.append((b[2] - b[0]) / sc)
        h = hist(im, b)
        if h is not None: hcur = 0.9 * hcur + 0.1 * h
follow(range(j0 + 1, len(rec))); follow(range(j0 - 1, -1, -1))

# 바닥 동작처럼 선생님이 옆으로 넓게 누우면 4:5 넓은 창 + 위아래 흐린 배경 (몸이 잘리지 않게)
wide = a.shape == "wide" or (a.shape == "auto" and np.percentile(bw_list, 75) > cw * 0.8)
if wide: cw = int(round(H * 0.8)) // 2 * 2
ts = np.array([r[0] for r in rec]); xs = np.array([np.nan if v is None else v / sc for v in cx])
good = ~np.isnan(xs); xs = np.interp(ts, ts[good], xs[good])
# 2) 카메라맨처럼: 튀는 값 제거 → 앞뒤로 부드럽게 → 속도 제한
med = np.array([np.median(xs[max(0, j - 2): j + 3]) for j in range(len(xs))])
def ema(v, al):
    o = v.copy()
    for j in range(1, len(o)): o[j] = o[j - 1] + al * (o[j] - o[j - 1])
    return o
sm = (ema(med, .25) + ema(med[::-1], .25)[::-1]) / 2
tf = np.arange(0, a.dur, 1 / fps); cxf = np.interp(tf, ts, sm)
maxv = W * 0.5 / fps
for j in range(1, len(cxf)): cxf[j] = cxf[j - 1] + np.clip(cxf[j] - cxf[j - 1], -maxv, maxv)
xpos = (np.clip(cxf - cw / 2, 0, W - cw)).astype(int) // 2 * 2

# 색 보정은 4K 원본에서 16비트로(계단·노이즈 덜 생김) → 축소 → 가벼운 노이즈 제거
GRADE = f",format=gbrp16le,lut3d={a.lut}:interp=tetrahedral,format=yuv420p10le" if a.lut else ""
# 어두운 바닥·벽 얼룩(노이즈)은 자르기 전 원본에서 시간축으로 먼저 걸러야 깨끗함 (자른 뒤 거르면 화면 이동 때 번짐)
PRE = f"hqdn3d={2*a.denoise}:{1.5*a.denoise}:{9*a.denoise}:{7*a.denoise}," if (a.lut and a.denoise > 0) else ""
DN = f",hqdn3d={1.5*a.denoise}:{1.2*a.denoise}:{5*a.denoise}:{4*a.denoise}" if a.denoise > 0 else ""
f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
for t, x in zip(tf, xpos): f.write(f"{t:.4f} crop@c x {x};\n")
f.close()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-t", str(a.dur), "-i", a.video,
                *(["-filter_complex", f"[0:v]sendcmd=f={f.name},crop@c=w={cw}:h={H}:x={xpos[0]}:y=0,split[a][b];"
                   "[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.18[bg];"
                   "[a]scale=1080:1350,setsar=1[fg];[bg][fg]overlay=0:150,setsar=1[v]", "-map", "[v]", "-map", "0:a?"] if wide else
                  ["-vf", f"{PRE}sendcmd=f={f.name},crop@c=w={cw}:h={H}:x={xpos[0]}:y=0{GRADE},scale=1080:1920:flags=lanczos,setsar=1{DN}"]),
                "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", a.out], check=True)
os.unlink(f.name); os.unlink(seg)

if a.check:  # 확인용: 8장 (보라 상자 = 선생님, 흰 선 = 자른 창)
    pick = np.linspace(0, len(rec) - 1, 8).astype(int); tiles = []
    for j in pick:
        t, bx, ids, im = rec[j]; im = im.copy()
        for b in bx: cv2.rectangle(im, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), (120, 120, 120), 1)
        if j in boxes_for_check:
            b = boxes_for_check[j]; cv2.rectangle(im, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), (255, 120, 185), 4)
        x = int(np.interp(t, tf, xpos) * sc); cv2.rectangle(im, (x, 0), (x + int(cw * sc), SH - 1), (255, 255, 255), 3)
        cv2.putText(im, f"{t:.1f}s", (12, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        tiles.append(cv2.resize(im, (640, int(640 * SH / SW))))
    cv2.imwrite(a.check, np.vstack([np.hstack(tiles[i:i + 2]) for i in range(0, 8, 2)]))
print(a.out, f"teacher id {tid}, x {xpos.min()}~{xpos.max()}, {'wide 4:5' if wide else 'tall 9:16'}")
