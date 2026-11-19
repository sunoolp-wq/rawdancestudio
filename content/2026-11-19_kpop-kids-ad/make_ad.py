"""유아·키즈 K-POP반 광고 릴스 (원장님 2026-11-19: 각 음원으로 하나씩 만들어 비교)
- 30초: MA_LucaFrancini_PrivateParty (120 BPM) / 15초: MA_IntoTheMusic_JustMadness (130 BPM)
- 컷은 박자에 맞춤. 영상은 원장님 드라이브 폴더 6개 (편집본은 앞 TRACKPAD 자막·끝 로고 구간 빼고 사용)
- 광고 규칙(docs/instagram-ads.md): 원곡 제목·가수명 미표기, 원음 0, 아이돌 안무 후렴은 1초 이하로 짧게 (원장님 확인 필요 메모)
사용: python make_ad.py <영상폴더> <음원폴더> <출력폴더> [30|15]
"""
import json, os, subprocess, sys, tempfile
import numpy as np

SRC, MUS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
WHICH = sys.argv[4] if len(sys.argv) > 4 else "30"
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "../.."))
FPS = 30
say = lambda s: print(s, flush=True)

# 영상: (파일, 반, 쓸 구간 시작, 끝 여유) — 편집본은 앞 5.5초(자막)·끝 3.5초(로고) 뺌
V = [("1021_kids.mp4", "키즈", 5.5, 3.5), ("1104_kpop.mp4", "키즈", 5.5, 3.5), ("1119_kids_insta.mp4", "키즈", 5.5, 3.5),
     ("clip3.mp4", "키즈", 5.5, 3.5), ("1118_yua.mp4", "유아", 2.0, 2.0), ("1112_yua_insta.mp4", "유아", 1.0, 1.0)]

def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
def size(f):
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip().split(",")
    return int(w), int(h)

def motion(f, a, b):
    """a~b초 동안 초당 5장 움직임 크기"""
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", f, "-vf", "fps=5,scale=64:-2,format=gray", "-f", "rawvideo", "-"], capture_output=True)
    w, h = size(f); hh = int(round(64 * h / w / 2)) * 2
    x = np.frombuffer(r.stdout, np.uint8); n = len(x) // (64 * hh); x = x[:n * 64 * hh].reshape(n, hh, 64).astype(np.float32)
    return np.r_[0, np.abs(np.diff(x, axis=0)).mean((1, 2))]

def picks(f, a0, tail, seg, k):
    """움직임이 큰 구간 k개 (서로 2초 이상 떨어지게) → 시작 시각 목록"""
    D = dur(f); a, b = a0, D - tail; m = motion(f, a, b); w = max(1, int(seg * 5))
    sc = np.convolve(m, np.ones(w) / w, "valid"); out = []
    for i in np.argsort(sc)[::-1]:
        t = a + i / 5
        if t + seg > b: continue
        if all(abs(t - u) >= 2.0 for u in out): out.append(t)
        if len(out) >= k: break
    return sorted(out)

_yolo = None
def center(f, t):
    """가로 원본: 그 장면에서 아이 위치 → (가운데 x, 가운데 y, 사람 키) 비율"""
    global _yolo
    from ultralytics import YOLO
    if _yolo is None: _yolo = YOLO(os.path.join(ROOT, "tools/class-reel/yolo11s.pt"), verbose=False)
    p = tempfile.mktemp(suffix=".jpg"); subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", f, "-frames:v", "1", p])
    r = _yolo(p, classes=[0], verbose=False)[0]; os.remove(p)
    if not len(r.boxes): return 0.5, 0.6, 0.5
    b = r.boxes.xyxyn.cpu().numpy(); a = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1]); x0, y0, x1, y1 = b[int(np.argmax(a))]
    return (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0

def clip(f, t, d, out):
    """1080x1920 세로로, 소리 없이"""
    w, h = size(f)
    if h >= w: vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    else:   # 가로 4K 유아 영상: 아이 중심으로 9:16 잘라 냄 (사람 키의 1.9배 높이)
        cx, cy, ph = center(f, t + d / 2); ch = min(h, max(h * 0.55, ph * h * 1.9)); cw = ch * 9 / 16
        x = min(max(0, cx * w - cw / 2), w - cw); y = min(max(0, cy * h - ch * 0.48), h - ch)
        vf = f"crop={int(cw)//2*2}:{int(ch)//2*2}:{int(x)}:{int(y)},scale=1080:1920"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t:.3f}", "-t", f"{d:.3f}", "-i", f, "-vf", f"{vf},fps={FPS},setsar=1,format=yuv420p",
                    "-an", "-c:v", "libx264", "-crf", "12", "-preset", "fast", out], check=True)

# ── 구성 (박자 단위) ──
if WHICH == "30":
    song, bpm, first = os.path.join(MUS, "party.wav"), 120.0, 0.029; B = 60 / bpm
    # 원장님 2026-11-19: 무료 체험 빼고, 쌤 이력 강조 → 훅 · 몽타주 · T.YUNI · T.MINKYUNG · 정보 · 로고 (64박 = 32초)
    plan = [("hook", 4)] + [("mont", 2)] * 12 + [("yuni", 4)] * 2 + [("mink", 4)] * 2 + [("info", 4)] * 3 + [("logo", 8)]
else:
    song, bpm, first = os.path.join(MUS, "madness.wav"), 130.0, 0.435; B = 60 / bpm
    plan = [("hook", 4)] + [("mont", 2)] * 5 + [("yuni", 4)] + [("mink", 4)] + [("info", 6)] + [("logo", 4)]
nmont = sum(1 for p in plan if p[0] == "mont"); nlong = sum(1 for p in plan if p[0] in ("hook", "info", "cta", "logo"))

# 영상마다 후보 구간
cand = {}
for f, cls, a0, tail in V:
    path = os.path.join(SRC, f); cand[f] = [(t, cls) for t in picks(path, a0, tail, 2.2, 4)]
    say(f"{f}: 후보 {', '.join(f'{t:.1f}' for t, _ in cand[f])}초")
# 번갈아 꺼내 쓰기 (키즈·유아 섞이게)
order = ["clip3.mp4", "1118_yua.mp4", "1119_kids_insta.mp4", "1112_yua_insta.mp4", "1021_kids.mp4", "1104_kpop.mp4"]   # 맨 앞(훅) = 밝고 동작 큰 clip3
queue = []
for r in range(4):
    for f in order:
        if r < len(cand[f]): queue.append((f,) + cand[f][r])
# 쌤 장면은 그 쌤 반 영상에서 (1021 = YUNI 반, 1119 = MINKYUNG 반 — 영상 앞 자막 기준)
pool = {"yuni": [("1021_kids.mp4",) + c for c in cand["1021_kids.mp4"]], "mink": [("1119_kids_insta.mp4",) + c for c in cand["1119_kids_insta.mp4"]]}
used = {"yuni": 0, "mink": 0}
queue = [q for q in queue if q[0] not in ("1021_kids.mp4", "1119_kids_insta.mp4")] + [q for q in queue if q[0] in ("1021_kids.mp4", "1119_kids_insta.mp4")]
tmp = tempfile.mkdtemp(prefix="raw-kpopad-"); segs = []; timeline = []; t = 0.0; qi = 0
for kind, beats in plan:
    d = beats * B
    if kind in pool: f, st, cls = pool[kind][used[kind] % len(pool[kind])]; used[kind] += 1
    else: f, st, cls = queue[qi % len(queue)]; qi += 1
    # 몽타주는 그 구간 가운데 1초 근처, 긴 장면은 시작부터
    s0 = st + (0.4 if kind == "mont" else 0)
    out = os.path.join(tmp, f"{len(segs):02d}.mp4"); clip(os.path.join(SRC, f), s0, d, out); segs.append(out)
    timeline.append({"kind": kind, "t0": round(t, 3), "t1": round(t + d, 3), "cls": cls}); t += d
total = t; say(f"총 {total:.2f}초, 컷 {len(segs)}개")
lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
base = os.path.join(tmp, "base.mp4")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base], check=True)

# 글자 장면 (ad.html) → 영상 위에 얹고 음원 깔기
sys.path.insert(0, os.path.join(ROOT, "tools"))
frames = os.path.join(tmp, "f"); os.makedirs(frames)
js = f"""const {{renderFrames}}=require('{os.path.join(ROOT, "tools/pw.js")}');
(async()=>{{await renderFrames({{file:'{os.path.join(HERE, "ad.html")}',n:{int(round(total * FPS))},fps:{FPS},dir:'{frames}',setupArg:{json.dumps({"tl": timeline, "ver": WHICH})}}});}})();"""
jp = os.path.join(tmp, "r.js"); open(jp, "w").write(js); subprocess.run(["node", jp], check=True)
os.makedirs(OUT, exist_ok=True); out = os.path.join(OUT, f"KPOP_ad_{WHICH}s.mp4")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", base, "-framerate", str(FPS), "-i", os.path.join(frames, "%05d.png"),
                "-ss", f"{first:.3f}", "-i", song,
                "-filter_complex", f"[1:v]format=rgba[o];[0:v][o]overlay=0:0:format=auto,format=yuv420p[v];[2:a]atrim=0:{total:.3f},afade=t=in:st=0:d=0.03,afade=t=out:st={total - 1.2:.3f}:d=1.2[a]",
                "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
json.dump({"timeline": timeline, "song": os.path.basename(song), "bpm": bpm}, open(os.path.join(OUT, f"KPOP_ad_{WHICH}s.json"), "w"), ensure_ascii=False, indent=1)
say(out)
