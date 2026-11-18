"""RAW 영상공장 — 원장님 맥에서 돌리는 영상 자동화 (2026-11-17)
브라우저 화면(index.html) ↔ 이 서버 ↔ 기존 도구(tools/daily-story, tools/class-reel)
실행: 저장소 맨 위 '2_RAW영상공장_열기.command' (또는 .venv/bin/python tools/raw-studio/server.py)
결과: ~/Movies/RAW 영상공장/날짜/
"""
import json, os, re, shutil, subprocess, sys, threading, time, uuid, datetime, platform, traceback
from flask import Flask, request, jsonify, send_file, abort

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable
CR = os.path.join(ROOT, "tools", "class-reel")
DS = os.path.join(ROOT, "tools", "daily-story")
LUTS = os.path.join(HERE, "luts")
WIN = platform.system() == "Windows"
# 윈도우: 결과는 '동영상(Videos)', 자식 프로그램 한글 출력이 깨지지 않게 UTF-8로 (2026-11-18 윈도우판)
os.environ["PYTHONUTF8"] = "1"; os.environ["PYTHONIOENCODING"] = "utf-8"
OUT = os.path.expanduser(os.environ.get("RAW_OUT", "~/Videos/RAW 영상공장" if WIN else "~/Movies/RAW 영상공장"))
WORK = os.path.join(OUT, ".작업중")
UP = os.path.join(WORK, "uploads")
# 음원 폴더: 원장님이 받은 음원(mp3 등)을 넣어 두면 영상 속 노래와 같은 곡을 자동으로 찾아 입힘 (2026-11-17)
MUSIC = os.path.expanduser(os.environ.get("RAW_MUSIC", "~/Music/RAW 음원"))
for d in (OUT, WORK, UP, MUSIC): os.makedirs(d, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "tools", "class-reel"))
from audiomatch import song_files
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
KR = dict(zip(DAYS, ["월", "화", "수", "목", "금", "토", "일"]))

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 ** 3   # 8GB까지 올리기

# ── 유틸 ─────────────────────────────────────────────
def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", f], capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stdout or "{}"); s = (j.get("streams") or [{}])[0]
    return {"w": s.get("width", 0), "h": s.get("height", 0), "dur": float(j.get("format", {}).get("duration", 0) or 0)}

def upath(uid):
    for f in os.listdir(UP):
        if f.startswith(uid + "_"): return os.path.join(UP, f)
    raise ValueError("올린 파일을 찾을 수 없어요. 다시 올려 주세요")

def safe(s): return re.sub(r"[^0-9A-Za-z가-힣._-]+", "_", str(s or "")).strip("_")[:40] or "영상"

def outfile(kind, name, ext="mp4"):
    d = os.path.join(OUT, datetime.date.today().isoformat()); os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{time.strftime('%H%M%S')}_{kind}_{safe(name)}.{ext}")

def lut_path(name):
    if not name: return None
    p = os.path.join(LUTS, os.path.basename(name))
    if not p.endswith(".cube"): p += ".cube"
    if not os.path.exists(p): raise ValueError(f"LUT 파일이 없어요: {name}")
    return p

# ── 작업(잡) ─────────────────────────────────────────
JOBS, QUEUE, LOCK = {}, [], threading.Lock()

class Job:
    def __init__(self, kind, params):
        self.id = uuid.uuid4().hex[:8]; self.kind = kind; self.params = params
        self.status = "대기"; self.log = []; self.outs = []; self.created = time.time(); self.err = ""; self.warn = ""
    def say(self, s):
        for line in str(s).splitlines():
            if line.strip(): self.log.append(line.rstrip())
        self.log = self.log[-200:]
    def run(self, cmd, cwd=ROOT):
        self.say("▶ " + " ".join(os.path.basename(c) if i == 0 else c for i, c in enumerate(cmd))[:300])
        # stdin 없음: ffmpeg 등이 검은 창 키보드 입력을 기다리며 멈추지 않게 (2026-11-17 맥 '장면 420/510' 멈춤)
        p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding="utf-8", errors="replace")
        last = [time.time()]; stuck = [False]
        def watch():   # 15분 동안 아무 진행 표시가 없으면 멈춘 것으로 보고 끔
            while p.poll() is None:
                if time.time() - last[0] > 900: stuck[0] = True; p.kill(); return
                time.sleep(5)
        threading.Thread(target=watch, daemon=True).start()
        for line in p.stdout: last[0] = time.time(); self.say(line)
        if p.wait() != 0:
            if stuck[0]: raise RuntimeError("15분 동안 진행이 없어 멈췄어요. 검은 창을 닫고 2_RAW영상공장_열기를 다시 실행한 뒤 다시 만들어 주세요")
            raise RuntimeError((self.log[-1] if self.log else "") or f"실패: {os.path.basename(cmd[0])}")
    def view(self):
        return {"id": self.id, "kind": self.kind, "status": self.status, "log": self.log[-12:], "outs": self.outs, "err": self.err,
                "title": self.params.get("_title", self.kind), "created": self.created}

def worker():
    while True:
        job = None
        with LOCK:
            if QUEUE: job = QUEUE.pop(0)
        if not job: time.sleep(0.5); continue
        job.status = "작업 중"
        try:
            PIPES[job.kind](job, job.params); job.status = "완료"
        except Exception as e:
            job.status = "실패"; job.err = str(e)[:400]; job.say(traceback.format_exc()[-800:])
threading.Thread(target=worker, daemon=True).start()

# ── 단계 ─────────────────────────────────────────────
def apply_lut(job, src, out, lut, strength=100):
    lp = lut_path(lut); s = max(0, min(100, int(strength or 100))) / 100
    lpe = lp.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    # 16비트로 계산 (어두운 그라데이션 계단 줄임, 원장님 2026-11-17 "화질 깨짐 없나") + 중간 파일은 crf 12로 거의 무손실
    vf = (f"format=gbrp16le,lut3d=file='{lpe}':interp=tetrahedral" if s >= 0.999 else
          f"format=gbrp16le,split[a][b];[b]lut3d=file='{lpe}':interp=tetrahedral[l];[a][l]blend=all_mode=normal:all_opacity={s:.2f}")
    job.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-filter_complex", f"[0:v]{vf},format=yuv420p[v]", "-map", "[v]", "-map", "0:a?",
             "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", out])

def track(job, src, start, dur, pickx, pickt, check=None):
    """가로 → 쌤 따라가며 세로로, 세로 원본이면 그 구간만 자름. 결과: 작업 폴더의 세로 영상"""
    info = probe(src); out = os.path.join(WORK, f"{job.id}_track.mp4")
    if info["h"] > info["w"]:
        job.say("세로 영상이라 따라가기 없이 그 구간만 잘라요")
        job.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", src, "-vf",
                 "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1", "-c:v", "libx264", "-crf", "14",
                 "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", out])
    else:
        cmd = [PY, os.path.join(CR, "follow_yolo.py"), "--video", src, "--start", str(start), "--dur", str(dur), "--pick-x", str(pickx),
               "--pick-t", str(pickt), "--denoise", "0", "--crf", "14", "--out", out]
        if check: cmd += ["--check", check]
        job.run(cmd)
    return out

def keep(job, path, label):
    job.outs.append({"path": path, "label": job.warn + label, "url": "/files/" + os.path.relpath(path, OUT)})

def music(job, src, out, P, auto_ok=False, orig=None, cs=0.0):
    """음원 입히기. 올린 음원이 있으면 그것, 없고 '음원 폴더에서 자동'이면 폴더에서 같은 곡을 찾음.
    orig/cs: 따라가기 전 원본과 자른 시작 시각. 주면 곡·위치를 원본에서 앞뒤 20초 넓혀 찾음 (짧은 영상도 확실하게, 2026-11-17)
    auto_ok: 못 찾으면 실패하지 않고 원래 소리 그대로 → False 돌려줌"""
    song = upath(P["song"]) if P.get("song") else (MUSIC if P.get("auto_song") else None)
    if not song: return False
    if song == MUSIC and not song_files(MUSIC):
        if auto_ok: job.say("음원 폴더가 비어 있어서 원래 소리 그대로 써요"); return False
        raise RuntimeError(f"음원 폴더가 비어 있어요: {MUSIC}")
    n0 = len(job.log); off = None
    try:
        if orig:
            cmd = [PY, os.path.join(CR, "music_sync.py"), "--video", orig, "--song", song, "--find-only", "--match-pad", "20",
                   "--start", f"{cs:.3f}", "--end", f"{cs + probe(src)['dur']:.3f}"]
            if str(P.get("offset", "")).strip() != "": cmd += ["--offset", str(float(P["offset"]))]
            job.run(cmd)
            f = next(json.loads(l) for l in reversed(job.log) if l.startswith('{"find"'))
            song, off = f["song"], f["offset"] - cs
        cmd = [PY, os.path.join(CR, "music_sync.py"), "--video", src, "--song", song, "--out", out]
        if P.get("trim"): cmd.append("--trim-to-song")
        if P.get("pre_room"): cmd.append("--pre-room")
        if P.get("fade_out") is not None: cmd += ["--fade-out", str(P["fade_out"])]
        if off is not None: cmd += ["--offset", f"{off:.4f}"]
        else:
            for k in ("start", "end", "offset"):
                if str(P.get(k, "")).strip() != "": cmd += ["--" + k, str(float(P[k]))]
        job.run(cmd)
    except (RuntimeError, StopIteration):
        if auto_ok: job.say("음원을 못 맞춰서 연습실 원래 소리 그대로 써요"); job.warn = "⚠️ 음원 못 찾음(연습실 소리) · "; return False
        raise
    if any(l.startswith("확인필요") for l in job.log[n0:]): job.warn = "⚠️ 음원 박자 확인필요 · "
    return True

# ── 파이프라인 4+1개 ──────────────────────────────────
def p_story(job, P):
    for d in P["dates"]:
        job.say(f"{d} 스토리 만드는 중…")
        job.run(["node", os.path.join(DS, "render.js"), d])
        src = os.path.join(ROOT, "content", f"{d}_daily-story", "story.mp4"); dst = outfile("스토리", d)
        shutil.copy(src, dst); keep(job, dst, f"{d} 스토리")

def p_teacher(job, P):
    src = upath(P["file"]); start, dur = float(P.get("start", 0)), float(P.get("dur", 15))
    base = f"{P['name']}_{P['genre']}"; chk = outfile("확인사진", base, "jpg")
    v = track(job, src, start, dur + 0.4, P.get("pickx", .5), P.get("pickt", .5), chk)
    if os.path.exists(chk): keep(job, chk, "쌤 확인 사진 (보라 상자 = 쌤)")
    if P.get("auto_song") or P.get("song"):
        mv = os.path.join(WORK, f"{job.id}_music.mp4")
        if music(job, v, mv, {"song": P.get("song"), "auto_song": P.get("auto_song"), "fade_out": 0}, auto_ok=True, orig=src, cs=start): v = mv
    if P.get("lut"):
        lv = os.path.join(WORK, f"{job.id}_lut.mp4"); apply_lut(job, v, lv, P["lut"], P.get("strength", 100)); v = lv
    out = outfile("쌤15초", base)
    cmd = ["node", os.path.join(CR, "make_reel2.js"), "--video", v, "--start", "0", "--dur", str(dur), "--name", P["name"], "--genre", P["genre"],
           "--when", P["when"], "--whenKr", P.get("whenKr") or P["when"], "--out", out]
    if P.get("hall"): cmd += ["--hall", P["hall"]]
    if P.get("popup"): cmd += ["--kicker", "POP-UP CLASS"]
    job.run(cmd); keep(job, out, "쌤 15초 영상")

def p_trackpad(job, P):
    """춤 시작 전 pre초(1~5) 동안 TRACKPAD 자막 → 춤(dur초) → RAW 로고 엔딩 OUTRO초 (원장님 2026-11-17)
    로고 엔딩 동안에도 영상은 계속 흘러가고 그 위를 로고가 덮음 → 연습실 소리·음원이 끊기지 않고 이어짐"""
    OUTRO = 2.5
    src = upath(P["file"]); start, dur = float(P.get("start", 0)), float(P.get("dur", 30))
    pre = min(5.0, max(1.0, float(P.get("pre", 5) or 5)))
    cs = max(0.0, start - pre)                                    # 실제로 자르기 시작하는 원본 시각
    total = (start - cs) + dur + (OUTRO if P.get("outro", True) else 0)
    base = f"{P['teacher']}_{P['genre']}"; chk = outfile("확인사진", base, "jpg")
    v = track(job, src, cs, total, P.get("pickx", .5), float(P.get("pickt", .5)) + (start - cs), chk)
    if os.path.exists(chk): keep(job, chk, "쌤 확인 사진 (보라 상자 = 쌤)")
    if P.get("song") or P.get("auto_song"):
        mv = os.path.join(WORK, f"{job.id}_music.mp4")
        off = str(P.get("offset", "")).strip()
        if music(job, v, mv, {"song": P.get("song"), "auto_song": P.get("auto_song"), "pre_room": True, "fade_out": 0, "offset": off},
                 auto_ok=True, orig=src, cs=cs): v = mv
    if P.get("lut"):
        lv = os.path.join(WORK, f"{job.id}_lut.mp4"); apply_lut(job, v, lv, P["lut"], P.get("strength", 100)); v = lv
    out = outfile("TRACKPAD", base)
    cmd = ["node", os.path.join(CR, "add_title.js"), "--video", v, "--title", P["teacher"], "--name", P["genre"], "--len", f"{max(1.0, start - cs):.2f}", "--at", "0", "--out", out]
    if P.get("outro", True): cmd += ["--outro", str(OUTRO)]
    if P.get("track"): cmd += ["--track", P["track"]]
    job.run(cmd); keep(job, out, "TRACKPAD 릴스")

def p_music(job, P):
    src = upath(P["file"]); out = outfile("음원싱크", P.get("name") or "영상")
    tmp = os.path.join(WORK, f"{job.id}_music.mp4") if P.get("lut") else out
    if not music(job, src, tmp, P): raise RuntimeError("음원을 올리거나 '음원 폴더에서 자동으로 찾기'를 골라 주세요")
    if P.get("lut"): apply_lut(job, tmp, out, P["lut"], P.get("strength", 100))
    keep(job, out, "음원 입힌 영상")

def p_lut(job, P):
    src = upath(P["file"]); orig = re.sub(r"^[0-9a-f]{10}_", "", os.path.splitext(os.path.basename(src))[0])
    out = outfile("LUT_" + os.path.splitext(P["lut"])[0], orig)
    apply_lut(job, src, out, P["lut"], P.get("strength", 100)); keep(job, out, "LUT 입힌 영상")

def yt_plan(P, out=None):
    song = upath(P["song"]) if P.get("song") else (MUSIC if P.get("auto_song") and song_files(MUSIC) else "")
    plan = {"clips": [{"video": upath(c["file"]), "start": float(c["start"]), "dur": float(c["dur"])} for c in P["clips"]], "song": song,
            "xfade": float(P.get("xfade", 0.5)), "lut": lut_path(P["lut"]) if P.get("lut") else "", "strength": P.get("strength", 100),
            "height": int(P.get("height") or 0), "out": out, "outro": 2.5 if P.get("outro", True) else 0, "layout": P.get("layout") or "concat",
            "title": ({"len": float(P.get("pre") or 5), "title": P["teacher"], "name": P.get("genre", ""), "track": P.get("track", "")}
                      if (P.get("teacher") or "").strip() and float(P.get("pre") or 0) > 0 else None)}
    f = os.path.join(WORK, f"yt_{uuid.uuid4().hex[:8]}.json"); json.dump(plan, open(f, "w", encoding="utf-8"), ensure_ascii=False); return f

def p_youtube(job, P):
    """유튜브용 이어 붙이기 (원장님 2026-11-17): 같은 곡·같은 구간 A그룹 → B그룹 → 쌤 솔로 → 단체, 가로, 깨끗한 음원, 교차 디졸브"""
    if len(P.get("clips") or []) < 1: raise RuntimeError("영상을 올려 주세요")
    s3 = P.get("layout") == "stack3"
    if s3 and len(P["clips"]) != 3: raise RuntimeError("3분할은 영상이 딱 3개 필요해요 (위 · 가운데 · 아래)")
    out = outfile("3분할" if s3 else "유튜브", P.get("name") or ("3분할" if s3 else "이어붙이기"))
    n0 = len(job.log); job.run([PY, os.path.join(CR, "yt_concat.py"), "--make", yt_plan(P, out)])
    if any(l.startswith("확인필요") for l in job.log[n0:]): job.warn = "⚠️ 음원 확인필요(작업 기록 보기) · "
    keep(job, out, "3분할 영상" if s3 else "유튜브 영상")

PIPES = {"youtube": p_youtube, "story": p_story, "teacher": p_teacher, "trackpad": p_trackpad, "music": p_music, "lut": p_lut}

# ── 시간표 (스토리) ───────────────────────────────────
def sched_for(date):
    y, m, _ = date.split("-"); f = os.path.join(DS, f"schedule-{y}-{m}.json")
    if not os.path.exists(f): return None
    return json.load(open(f, encoding="utf-8"))

def extra_all():
    f = os.path.join(DS, "extra.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}

def day_classes(date):
    s = sched_for(date)
    if s is None: return None, None
    dow = DAYS[datetime.date.fromisoformat(date).weekday()]
    base = [dict(c) for c in s["days"].get(dow, [])]
    return dow, base

# ── API ──────────────────────────────────────────────
@app.get("/")
def index(): return send_file(os.path.join(HERE, "index.html"))

@app.get("/api/info")
def info():
    teachers, genres = set(), set()
    for f in sorted(os.listdir(DS)):
        if f.startswith("schedule-") and f.endswith(".json"):
            for cs in json.load(open(os.path.join(DS, f), encoding="utf-8"))["days"].values():
                for c in cs:
                    if c.get("teacher"): teachers.add(c["teacher"])
                    if c.get("name") and "K-POP" not in c["name"]: genres.add(c["name"])
    luts = sorted(f for f in os.listdir(LUTS) if f.endswith(".cube"))
    return jsonify({"teachers": sorted(teachers), "genres": sorted(genres), "luts": luts, "out": OUT, "today": datetime.date.today().isoformat(),
                    "music": MUSIC, "songs": [os.path.relpath(f, MUSIC) for f in song_files(MUSIC)]})

@app.post("/api/align")
def align_api():
    """1번 영상의 노래 구간과 같은 구간을 나머지 영상에서 찾기"""
    P = request.get_json()
    r = subprocess.run([PY, os.path.join(CR, "yt_concat.py"), "--align", yt_plan(P)], capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=900)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    if r.returncode or not last.startswith("{"): return jsonify({"error": (r.stderr.strip().splitlines() or ["맞추다가 멈췄어요"])[-1]}), 500
    j = json.loads(last); j["log"] = [l for l in r.stdout.splitlines()[:-1] if l.startswith(("곡:", "확인필요", "기준"))]; return jsonify(j)

FS_CACHE = {}
@app.get("/api/findstart")
def findstart():
    """춤 시작 후보 (원장님 2026-11-17). 음원 폴더에 곡이 있으면 같이 써서 더 정확하게"""
    uid = request.args["id"]; d = float(request.args.get("dur", 15)); key = (uid, d, len(song_files(MUSIC)))
    if key not in FS_CACHE:
        cmd = [PY, os.path.join(CR, "find_start.py"), "--video", upath(uid), "--dur", str(d), "--n", "4"]
        if song_files(MUSIC): cmd += ["--song", MUSIC]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=900)
        last = (r.stdout.strip().splitlines() or [""])[-1]
        if r.returncode or not last.startswith("{"): return jsonify({"error": (r.stderr.strip().splitlines() or ["후보를 못 찾았어요"])[-1]}), 500
        j = json.loads(last); j["log"] = [l for l in r.stdout.splitlines()[:-1] if l.startswith(("곡:", "음원 폴더"))]; FS_CACHE[key] = j
    return jsonify(FS_CACHE[key])

@app.post("/api/upload")
def upload():
    f = request.files.get("file")
    if not f: return jsonify({"error": "파일이 없어요"}), 400
    uid = uuid.uuid4().hex[:10]; p = os.path.join(UP, f"{uid}_{safe(os.path.basename(f.filename))}")
    f.save(p); i = probe(p) if not p.lower().endswith((".mp3", ".wav", ".m4a", ".aac")) else {"w": 0, "h": 0, "dur": 0}
    return jsonify({"id": uid, "name": f.filename, **i})

@app.get("/api/frame")
def frame():
    p = upath(request.args["id"]); t = float(request.args.get("t", 0))
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", p, "-frames:v", "1", "-vf", "scale=960:-2", "-f", "image2", "-c:v", "mjpeg", "-"],
                       capture_output=True)
    if not r.stdout: abort(404)
    return app.response_class(r.stdout, mimetype="image/jpeg")

@app.get("/api/day")
def day_get():
    d = request.args["date"]; dow, base = day_classes(d)
    if base is None: return jsonify({"error": f"{d[:7]} 시간표 파일이 없어요 (tools/daily-story/schedule-{d[:7]}.json)"}), 404
    ex = extra_all().get(d, {})
    rows = []
    for c in base:
        r = next((x for x in ex.get("replace", []) if x["start"] == c["start"] and x["name"] == c["name"]), None)
        cur = {**c, **(r["set"] if r else {})}
        removed = any(x["start"] == c["start"] and x["name"] == c["name"] for x in ex.get("remove", []))
        rows.append({"start": c["start"], "end": c.get("end", ""), "baseName": c["name"], "baseTeacher": c.get("teacher", ""), "name": cur["name"],
                     "teacher": cur.get("teacher", ""), "hall": cur.get("hall", ""), "popup": cur.get("mark") == "popup", "removed": removed})
    return jsonify({"dow": dow, "kr": KR[dow], "rows": rows, "added": ex.get("add", [])})

@app.post("/api/day")
def day_save():
    P = request.get_json(); d = P["date"]; dow, base = day_classes(d)
    if base is None: return jsonify({"error": "시간표 파일이 없어요"}), 404
    rep, rem = [], []
    for r in P["rows"]:
        c = next(x for x in base if x["start"] == r["start"] and x["name"] == r["baseName"])
        if r.get("removed"): rem.append({"start": c["start"], "name": c["name"]}); continue
        st = {}
        if r["name"] != c["name"]: st["name"] = r["name"]
        if r["teacher"] != c.get("teacher", ""): st["teacher"] = r["teacher"]
        if r.get("popup"): st["mark"] = "popup"
        if st: rep.append({"start": c["start"], "name": c["name"], "set": st})
    add = [a for a in P.get("added", []) if a.get("start") and a.get("name")]
    ex = extra_all(); e = {}
    if rep: e["replace"] = rep
    if rem: e["remove"] = rem
    if add: e["add"] = add
    if e: ex[d] = e
    else: ex.pop(d, None)
    json.dump(ex, open(os.path.join(DS, "extra.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return jsonify({"ok": True, "saved": e})

@app.post("/api/run")
def run():
    P = request.get_json(); kind = P.pop("kind")
    if kind not in PIPES: return jsonify({"error": "모르는 작업"}), 400
    j = Job(kind, P); JOBS[j.id] = j
    with LOCK: QUEUE.append(j)
    return jsonify({"id": j.id})

@app.get("/api/jobs")
def jobs(): return jsonify([j.view() for j in sorted(JOBS.values(), key=lambda j: -j.created)][:30])

@app.get("/files/<path:p>")
def files(p):
    f = os.path.realpath(os.path.join(OUT, p))
    if not f.startswith(os.path.realpath(OUT)) or not os.path.exists(f): abort(404)
    return send_file(f, conditional=True)

@app.post("/api/reveal")
def reveal():
    p = request.get_json().get("path") or OUT
    if platform.system() == "Darwin": subprocess.Popen(["open", "-R", p] if os.path.isfile(p) else ["open", p])
    elif WIN: subprocess.Popen(f'explorer /select,"{os.path.normpath(p)}"' if os.path.isfile(p) else ["explorer", os.path.normpath(p)])
    return jsonify({"ok": True})

if __name__ == "__main__":
    import logging; logging.getLogger("werkzeug").setLevel(logging.ERROR)   # 3초마다 오는 진행 확인 기록은 터미널에 안 찍음 (원장님 2026-11-17)
    port = int(os.environ.get("RAW_PORT", 5577))
    print(f"RAW 영상공장: http://127.0.0.1:{port}  (결과 폴더: {OUT})", flush=True)
    app.run(host="127.0.0.1", port=port, threaded=True)
