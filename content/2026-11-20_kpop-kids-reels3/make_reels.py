"""유아·키즈 K-POP반 광고 릴스 재구성 3종 (원장님 2026-11-20: 새로 올린 쌤 수업 진행 영상·티저 영상 활용, 30~40초, 3개)
A  TEACHER  : 쌤 티저(YUNI·MINKYUNG)로 시작 → 쌤 이력 카드 → 그 쌤 반 수업 → 유아·키즈 → 정보 → 로고   (Private Party 120 BPM)
B  CLASS LOG: 수업 진행 순서 STEP 1 쌤이 먼저 → STEP 2 따라 하고 → STEP 3 한 곡 완성 → 쌤 2명 → 정보 → 로고 (Street Fighters 129 BPM)
C  SPLIT    : 위는 쌤 티저, 아래는 그 쌤 반 아이들 (위아래 2분할) → 유아 → 정보 → 로고                    (Just Madness 130 BPM)
- 컷은 박자에 맞춤. 소리는 음원만 (영상 원음 0). 걸스힙합(금 20:10) 영상 2개는 성인·청소년 반이라 키즈 광고에서 뺌
사용: python make_reels.py <예전 영상 폴더> <새 영상 폴더> <음원 폴더> <출력 폴더> A|B|C
"""
import json, os, subprocess, sys, tempfile
import numpy as np

OLD, NEW, MUS, OUT, WHICH = sys.argv[1:6]
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "../.."))
FPS = 30
say = lambda s: print(s, flush=True)
P = lambda f: os.path.join(NEW if f.startswith("n") else OLD, f)

def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
def size(f):
    """화면에 보이는 크기 (아이폰 세로 영상은 회전 정보 반영)"""
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip().split(",")[:2])
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream_side_data=rotation", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
    return (h, w) if r and abs(int(float(r.split(",")[0] or 0))) == 90 else (w, h)

def motion(f, a, b):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", f, "-vf", "fps=5,scale=64:64,format=gray", "-f", "rawvideo", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.uint8); n = len(x) // 4096; x = x[:n * 4096].reshape(n, 64, 64).astype(np.float32)
    return np.r_[0, np.abs(np.diff(x, axis=0)).mean((1, 2))]

def picks(f, a, b, seg, k, gap=2.0):
    """a~b초 안에서 움직임이 큰 seg초 구간 k개 (서로 gap초 이상 떨어지게), 시간 순"""
    m = motion(f, a, b); w = max(1, int(seg * 5)); sc = np.convolve(m, np.ones(w) / w, "valid"); out = []
    for i in np.argsort(sc)[::-1]:
        t = a + i / 5
        if t + seg > b: continue
        if all(abs(t - u) >= gap for u in out): out.append(t)
        if len(out) >= k: break
    return sorted(out)

_yolo = None
def center(f, t):
    global _yolo
    from ultralytics import YOLO
    if _yolo is None: _yolo = YOLO(os.path.join(ROOT, "tools/class-reel/yolo11s.pt"), verbose=False)
    p = tempfile.mktemp(suffix=".jpg"); subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", f, "-frames:v", "1", p])
    r = _yolo(p, classes=[0], verbose=False)[0]; os.remove(p)
    if not len(r.boxes): return 0.5, 0.6, 0.5
    b = r.boxes.xyxyn.cpu().numpy(); a = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1]); x0, y0, x1, y1 = b[int(np.argmax(a))]
    return (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0

def fit(f, t, d, W, H):
    """원본을 W×H로 꽉 채우는 필터 (가로 4K 유아 영상은 아이 중심으로 자름)"""
    w, h = size(f)
    if w / h <= W / H + 0.05 or w == h:
        return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    cx, cy, ph = center(f, t + d / 2); ch = min(h, max(h * 0.55, ph * h * 1.9)); cw = min(w, ch * W / H); ch = cw * H / W
    x = min(max(0, cx * w - cw / 2), w - cw); y = min(max(0, cy * h - ch * 0.48), h - ch)
    return f"crop={int(cw)//2*2}:{int(ch)//2*2}:{int(x)}:{int(y)},scale={W}:{H}"

def enc(args, out):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args + ["-an", "-r", str(FPS), "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", out], check=True)

def seg(spec, d, out):
    lay = spec[0]
    if lay == "fill":       # 세로 꽉 채우기
        _, f, t = spec; f = P(f)
        enc(["-ss", f"{t:.3f}", "-t", f"{d:.3f}", "-i", f, "-vf", f"{fit(f, t, d, 1080, 1920)},fps={FPS},setsar=1"], out)
    elif lay == "square":   # 정사각 티저: 뒤는 같은 영상 흐리게, 앞은 정사각 그대로 (티저 속 'K-POP 쌤이름' 글자 살림)
        _, f, t, Y = spec; f = P(f)
        enc(["-ss", f"{t:.3f}", "-t", f"{d:.3f}", "-i", f, "-filter_complex",
             f"[0:v]fps={FPS},split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=40:2,eq=brightness=-0.32[bg];[b]scale=1080:1080[fg];[bg][fg]overlay=0:{Y},setsar=1"], out)
    elif lay == "split":    # 위아래 2분할 (각 1080×960)
        _, (f1, t1), (f2, t2) = spec; f1, f2 = P(f1), P(f2)
        top = "crop=1080:960:0:40" if size(f1)[0] == size(f1)[1] else fit(f1, t1, d, 1080, 960)
        enc(["-ss", f"{t1:.3f}", "-t", f"{d:.3f}", "-i", f1, "-ss", f"{t2:.3f}", "-t", f"{d:.3f}", "-i", f2, "-filter_complex",
             f"[0:v]fps={FPS},scale=1080:-2,{top}[a];[1:v]fps={FPS},{fit(f2, t2, d, 1080, 960)}[b];[a][b]vstack,setsar=1"], out)

# ── 쓸 구간 고르기 ──
YT, MT = "n2_talk.mp4", "n4_talk.mp4"            # 티저: YUNI(0~35초 춤, 뒤 로고) · MINKYUNG(0~37초 춤, 뒤 로고)
CLS = "n6_img1053.mov"                            # 쌤이 앞에서 시범, 아이들이 뒤에서 따라 하는 수업 장면 (쌤 이름은 확인 전이라 안 씀)
TWO = "n5_img0316.mov"                            # 쌤 2명이 먼저 맞춰 보는 장면 (이름 안 씀)
KIDS = {"1021_kids.mp4": ("키즈", 5.5, 3.5), "1104_kpop.mp4": ("키즈", 5.5, 3.5), "1119_kids_insta.mp4": ("키즈", 5.5, 3.5),
        "clip3.mp4": ("키즈", 5.5, 3.5), "1118_yua.mp4": ("유아", 2.0, 2.0), "1112_yua_insta.mp4": ("유아", 1.0, 1.0)}
cache = {}
def pk(f, k, segd=2.2, a=None, b=None, gap=2.0):
    key = (f, k, segd, gap)
    if key not in cache:
        if f in KIDS: _, a0, tail = KIDS[f]; a, b = a0, dur(P(f)) - tail
        cache[key] = picks(P(f), a if a is not None else 0.3, b if b is not None else dur(P(f)) - 0.3, segd, k, gap)
        say(f"{f}: {', '.join(f'{t:.1f}' for t in cache[key])}초")
    return cache[key]
yt = lambda k, s=2.2, g=2.0: pk(YT, k, s, 0.5, 35.0, g)
mt = lambda k, s=2.2, g=2.0: pk(MT, k, s, 0.5, 36.8, g)

def hook(title, band, k="RAW DANCE STUDIO · SUWON"): return {"kind": "hook", "k": k, "t": title, "band": band}
INFO = [{"kind": "info", "i": 0}, {"kind": "info", "i": 1}]
LOGO = {"kind": "logo"}
TY = {"d": "MON · WED", "n": "T. YUNI", "a": "대형 기획사 연습생 출신", "b": "", "s": "월·수 유아 · 키즈 K-POP"}
TM = {"d": "TUE · THU", "n": "T. MINKYUNG", "a": "현장 경험 많은 현역 댄서", "b": "아이돌 백업 등 무대 경력 다수", "s": "화·목 유아 · 키즈 K-POP"}

# plan: (박자 수, 화면, 글자)
if WHICH == "A":
    song, bpm, first = "party.wav", 120.0, 0.029
    Y = 200; y4, m4 = yt(4, 1.2), mt(4, 1.2); y2, m2 = yt(3, 5.2, 4), mt(3, 5.2, 4)
    H = hook("K-POP\nKIDZ", "유아 · 키즈 K-POP반 모집", "우리 아이 쌤을 소개합니다")
    k1021, k1119 = pk("1021_kids.mp4", 2), pk("1119_kids_insta.mp4", 2)
    plan = [(2, ("square", YT, y4[0], Y), H), (2, ("square", MT, m4[1], Y), H), (2, ("square", YT, y4[2], Y), H), (2, ("square", MT, m4[3], Y), H),
            (10, ("square", YT, y2[1], Y), dict(kind="card", **TY)),
            (4, ("fill", "1021_kids.mp4", k1021[0] + 0.3), {"kind": "cap", "tag": "T. YUNI 반", "e": "MON · WED", "ko": "월·수 YUNI 쌤 반"}),
            (4, ("fill", "1021_kids.mp4", k1021[1] + 0.3), {"kind": "cap", "tag": "T. YUNI 반", "e": "MON · WED", "ko": "월·수 YUNI 쌤 반"}),
            (10, ("square", MT, m2[1], Y), dict(kind="card", **TM)),
            (4, ("fill", "1119_kids_insta.mp4", k1119[0] + 0.3), {"kind": "cap", "tag": "T. MINKYUNG 반", "e": "TUE · THU", "ko": "화·목 MINKYUNG 쌤 반"}),
            (4, ("fill", "1119_kids_insta.mp4", k1119[1] + 0.3), {"kind": "cap", "tag": "T. MINKYUNG 반", "e": "TUE · THU", "ko": "화·목 MINKYUNG 쌤 반"}),
            (2, ("fill", "1118_yua.mp4", pk("1118_yua.mp4", 2)[0] + 0.4), {"kind": "cap", "tag": "유아 5–8세", "e": "DANCE", "ko": "아이돌 안무로 신나게"}),
            (2, ("fill", "clip3.mp4", pk("clip3.mp4", 2)[0] + 0.4), {"kind": "cap", "tag": "키즈 9–12세", "e": "DANCE", "ko": "아이돌 안무로 신나게"}),
            (2, ("fill", "1112_yua_insta.mp4", pk("1112_yua_insta.mp4", 2)[0] + 0.4), {"kind": "cap", "tag": "유아 5–8세", "e": "BASICS", "ko": "기본기까지 탄탄하게"}),
            (2, ("fill", CLS, pk(CLS, 3)[1]), {"kind": "cap", "tag": "", "e": "BASICS", "ko": "기본기까지 탄탄하게"}),
            (8, ("fill", "1104_kpop.mp4", pk("1104_kpop.mp4", 2)[0]), INFO[0]), (8, ("fill", "1118_yua.mp4", pk("1118_yua.mp4", 2)[1]), INFO[1]),
            (8, ("fill", "clip3.mp4", 0), LOGO)]
elif WHICH == "B":
    song, bpm, first = "street.wav", 129.25, 0.453
    c = pk(CLS, 3, 3.0, gap=3.0); t2 = pk(TWO, 2, 3.0, gap=4.0)
    H = hook("CLASS\nLOG", "유아 · 키즈 K-POP반 수업 현장", "RAW K-POP · SUWON")
    S1 = {"kind": "step", "no": "STEP 1", "e": "SHOW", "ko": "쌤이 먼저 보여주고"}
    S2 = {"kind": "step", "no": "STEP 2", "e": "FOLLOW", "ko": "하나씩 따라 하고"}
    S3 = {"kind": "step", "no": "STEP 3", "e": "PERFORM", "ko": "한 곡 완성까지"}
    ys, ms = yt(1, 4.6), mt(1, 4.6)
    plan = [(8, ("fill", CLS, c[0]), H),
            (8, ("fill", TWO, t2[0]), S1),
            (6, ("fill", CLS, c[1]), S2), (6, ("fill", "1104_kpop.mp4", pk("1104_kpop.mp4", 2)[0]), S2),
            (3, ("fill", "clip3.mp4", pk("clip3.mp4", 2)[0] + 0.3), dict(S3, tag="키즈 9–12세")), (3, ("fill", "1118_yua.mp4", pk("1118_yua.mp4", 2)[0] + 0.3), dict(S3, tag="유아 5–8세")),
            (3, ("fill", "1119_kids_insta.mp4", pk("1119_kids_insta.mp4", 2)[0] + 0.3), dict(S3, tag="키즈 9–12세")), (3, ("fill", "1112_yua_insta.mp4", pk("1112_yua_insta.mp4", 2)[0] + 0.3), dict(S3, tag="유아 5–8세")),
            (10, ("split", (YT, ys[0]), (MT, ms[0])), {"kind": "pair"}),
            (8, ("fill", CLS, c[2]), INFO[0]), (8, ("fill", "1021_kids.mp4", pk("1021_kids.mp4", 2)[1]), INFO[1]),
            (8, ("fill", "clip3.mp4", 0), LOGO)]
else:
    song, bpm, first = "madness.wav", 130.0, 0.435
    ys, ms = yt(3, 3.8, 3), mt(3, 3.8, 3); k1021, k1119 = pk("1021_kids.mp4", 3, 3.8), pk("1119_kids_insta.mp4", 3, 3.8)
    H = hook("K-POP\nKIDZ", "쌤의 춤 · 우리 아이 수업", "TEACHER ↑   CLASS ↓")
    BY = {"kind": "band", "d": "MON · WED", "n": "T. YUNI", "a": "대형 기획사 연습생 출신", "b": ""}
    BM = {"kind": "band", "d": "TUE · THU", "n": "T. MINKYUNG", "a": "현장 경험 많은 현역 댄서", "b": "아이돌 백업 등 무대 경력 다수"}
    plan = [(8, ("split", (YT, ys[0]), ("1021_kids.mp4", k1021[0])), dict(H, split=1)),
            (8, ("split", (YT, ys[1]), ("1021_kids.mp4", k1021[1])), BY), (8, ("split", (YT, ys[2]), ("1021_kids.mp4", k1021[2])), BY),
            (8, ("split", (MT, ms[0]), ("1119_kids_insta.mp4", k1119[0])), BM), (8, ("split", (MT, ms[1]), ("1119_kids_insta.mp4", k1119[1])), BM),
            (4, ("fill", "1118_yua.mp4", pk("1118_yua.mp4", 2)[0] + 0.3), {"kind": "cap", "tag": "유아 5–8세", "e": "FIRST DANCE", "ko": "첫 춤을 재밌게"}),
            (4, ("fill", "1112_yua_insta.mp4", pk("1112_yua_insta.mp4", 2)[0] + 0.3), {"kind": "cap", "tag": "유아 5–8세", "e": "FIRST DANCE", "ko": "첫 춤을 재밌게"}),
            (4, ("fill", CLS, pk(CLS, 3)[0]), {"kind": "cap", "tag": "", "e": "BASICS", "ko": "아이돌 안무로 기본기까지"}),
            (8, ("fill", "1104_kpop.mp4", pk("1104_kpop.mp4", 2)[1]), INFO[0]), (8, ("fill", "1118_yua.mp4", pk("1118_yua.mp4", 2)[1]), INFO[1]),
            (8, ("fill", "clip3.mp4", 0), LOGO)]

B = 60 / bpm; tmp = tempfile.mkdtemp(prefix="raw-reels3-"); segs = []; tl = []; t = 0.0
for i, (beats, spec, txt) in enumerate(plan):
    d = beats * B; out = os.path.join(tmp, f"{i:02d}.mp4")
    if txt.get("kind") != "logo": seg(spec, d, out)
    else: enc(["-f", "lavfi", "-i", f"color=c=0x0b0a0f:s=1080x1920:r={FPS}", "-t", f"{d:.3f}"], out)
    segs.append(out); tl.append(dict(txt, t0=round(t, 3), t1=round(t + d, 3), src=spec[1] if spec[0] != "split" else f"{spec[1][0]} / {spec[2][0]}")); t += d
# 같은 글자가 이어지는 장면은 한 묶음 (글자 애니메이션이 컷마다 다시 시작하지 않게)
g0 = 0
for i, s in enumerate(tl):
    same = i and {k: v for k, v in s.items() if k not in ("t0", "t1", "src", "tag")} == {k: v for k, v in tl[i - 1].items() if k not in ("t0", "t1", "src", "tag", "g0")}
    if not same: g0 = s["t0"]
    s["g0"] = g0
total = t; say(f"{WHICH}: 총 {total:.2f}초, 컷 {len(segs)}개")
lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
base = os.path.join(tmp, "base.mp4")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base], check=True)

frames = os.path.join(tmp, "f"); os.makedirs(frames)
js = f"""const {{renderFrames}}=require('{os.path.join(ROOT, "tools/pw.js")}');
(async()=>{{await renderFrames({{file:'{os.path.join(HERE, "reels.html")}',n:{int(round(total * FPS))},fps:{FPS},dir:'{frames}',setupArg:{json.dumps({"tl": tl, "ver": WHICH}, ensure_ascii=False)}}});}})();"""
jp = os.path.join(tmp, "r.js"); open(jp, "w").write(js); subprocess.run(["node", jp], check=True)
os.makedirs(OUT, exist_ok=True); out = os.path.join(OUT, f"KPOP_reel_{WHICH}.mp4")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", base, "-framerate", str(FPS), "-i", os.path.join(frames, "%05d.png"),
                "-ss", f"{first:.3f}", "-i", os.path.join(MUS, song),
                "-filter_complex", f"[1:v]format=rgba[o];[0:v][o]overlay=0:0:format=auto,format=yuv420p[v];[2:a]atrim=0:{total:.3f},afade=t=in:st=0:d=0.03,afade=t=out:st={total - 1.5:.3f}:d=1.5[a]",
                "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
json.dump({"timeline": tl, "song": song, "bpm": bpm, "total": round(total, 2)}, open(os.path.join(OUT, f"KPOP_reel_{WHICH}.json"), "w"), ensure_ascii=False, indent=1)
say(out)
