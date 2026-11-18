"""유튜브용: 같은 곡·같은 구간을 A그룹 → B그룹 → 쌤 솔로 → 단체처럼 여러 영상으로 이어 붙이기 (원장님 2026-11-17)
- 가로(16:9) 원본 그대로, 영상마다 연습실 소리를 깨끗한 음원으로 맞춰 바꿈, 사이는 교차 디졸브(기본 0.5초) 또는 컷
사용
  맞추기: python yt_concat.py --align plan.json   → 1번 영상(기준)의 시작·길이와 같은 노래 구간을 다른 영상에서 찾아 JSON 출력
  만들기: python yt_concat.py --make plan.json    → 영상 하나로
plan.json: {"clips": [{"video": 경로, "start": 초, "dur": 초}, ...], "song": 음원 파일/폴더/"", "xfade": 0.5,
            "title": {"len": 1~5, "title": 강사, "name": 장르, "track": 곡명} 또는 없음 → 1번 영상 춤 시작 전 len초 동안 TRACKPAD 자막 (2026-11-17)
            "lut": .cube 경로/"", "strength": 100, "height": 0(원본)|1080, "out": 결과.mp4}
"""
import json, os, shutil, subprocess, sys, tempfile
import numpy as np
from audiomatch import load, dur as fdur, best_offset, candidates, match_folder

say = lambda s: print(s, flush=True)
SR = 22050

def pick_song(P):
    s = P.get("song") or ""
    if not s: return None
    if os.path.isdir(s):
        c = P["clips"][0]; say("음원 폴더에서 같은 곡 찾는 중…")
        f, n1, n2, _ = match_folder(c["video"], s, max(0, c["start"] - 10), c["start"] + c["dur"] + 10, log=say)
        if not f: say(f"확인필요: 음원 폴더에서 이 노래를 못 찾았어요 ({n1}표 대 {n2}표) → 연습실 소리 그대로"); return None
        say(f"곡: {os.path.basename(f)}"); return f
    return s if os.path.isfile(s) else None

def offset_in(video, song_x, a, b, near=None):
    """영상 a~b초 구간에서 '노래 0:00 = 영상 몇 초' (못 찾으면 None)
    near=(영상 시각 t, 기대 노래 위치 p): 애매하면 't초에 노래가 p초쯤'인 후보를 고름 (모든 그룹이 같은 구간이라서)"""
    x = load(video, SR, a, b - a)
    off, ok, how = best_offset(x, song_x, SR, a, log=lambda m: None)
    if ok: return off
    cs = candidates(x, song_x, SR, a, min_votes=2)
    if cs and near: cs = sorted(cs, key=lambda c: abs((near[0] - c[0]) - near[1]))
    if cs and near and abs((near[0] - cs[0][0]) - near[1]) < 0.5:
        say(f"{os.path.basename(video)}: 1번과 같은 노래 구간으로 맞춤"); return cs[0][0]
    if cs: say(f"확인필요: {os.path.basename(video)} 음원 위치가 확실하지 않아요 ({how}) → 표가 가장 많은 위치로"); return cs[0][0]
    return None

def align(P):
    """기준(1번) 영상의 노래 구간 [P0, P1]을 다른 영상에서 찾아 시작·길이를 맞춤"""
    f = pick_song(P); ref = P["clips"][0]
    if f:
        sx = load(f, SR)
        o = offset_in(ref["video"], sx, max(0, ref["start"] - 5), min(fdur(ref["video"]), ref["start"] + ref["dur"] + 5))
        if o is None: return {"error": "1번 영상에서 노래 위치를 못 찾았어요"}
        P0, P1 = ref["start"] - o, ref["start"] + ref["dur"] - o
        say(f"기준 구간: 노래 {P0:.2f}~{P1:.2f}초")
    else:
        # 음원이 없으면 프리미어 '오디오로 동기화'처럼: 1번 영상의 그 구간 연습실 소리를 기준으로 나머지 영상에서 같은 소리를 찾음 (원장님 2026-11-18)
        # 춤 시작 앞 4초(쌤 카운트·노래를 다시 트는 순간)도 같이 비교 → 노래가 8마디마다 반복돼도 엉뚱한 반복에 안 맞음 (2026-11-18 테스트)
        a0 = max(0.0, ref["start"] - 4.0)
        sx = load(ref["video"], SR, a0, ref["start"] + ref["dur"] - a0)
        if len(sx) < SR * 5: return {"error": "1번 영상 구간이 너무 짧아요 (5초 이상)"}
        P0, P1 = ref["start"] - a0, ref["start"] - a0 + ref["dur"]; f = None
        say("음원 없이 1번 영상 소리로 맞추는 중 (프리미어 '오디오로 동기화'와 같은 방식)")
    out = [{"start": round(ref["start"], 2), "dur": round(ref["dur"], 2), "ok": True}]
    for c in P["clips"][1:]:
        D = fdur(c["video"]); x = load(c["video"], SR)
        best = None
        for oo, n in candidates(x, sx, SR, 0.0, min_votes=3):       # 한 영상 안에서 노래를 여러 번 틀었을 수도 있음 → 이 구간이 통째로 들어 있는 후보 중 표 많은 것
            if oo + P0 >= -0.3 and oo + P1 <= D + 0.3 and (best is None or n > best[1]): best = (oo, n)
        if best: out.append({"start": round(max(0, best[0] + P0), 2), "dur": round(P1 - P0, 2), "ok": True})
        else: out.append({"start": c.get("start", 0), "dur": c.get("dur", ref["dur"]), "ok": False}); say(f"확인필요: {os.path.basename(c['video'])}에서 같은 구간을 못 찾았어요")
    return {"clips": out, "song": os.path.basename(f) if f else "(음원 없음 · 1번 영상 소리로 맞춤)"}

def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", f],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    s = json.loads(r.stdout)["streams"][0]; n, d = s["r_frame_rate"].split("/")
    return s["width"], s["height"], s["r_frame_rate"], float(n) / float(d or 1)

def has_audio(f):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", f],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL).stdout.strip() != ""

def make(P):
    C = [dict(c) for c in P["clips"]]; X = float(P.get("xfade", 0.5) or 0); n = len(C)
    DS = [c["start"] for c in C]          # 춤 시작 (자막 때문에 1번 시작이 앞당겨져도 음원 찾기는 춤 구간에서만)
    W, H, FR, FPS = probe(C[0]["video"])
    T = P.get("title") or None; tdir = None
    if T and (T.get("title") or "").strip():
        # 1번 영상을 자막 길이만큼 앞에서부터 (원본 앞이 모자라면 있는 만큼)
        N = min(5.0, max(1.0, float(T.get("len") or 5))); ns = max(0.0, C[0]["start"] - N); pre = C[0]["start"] - ns
        C[0]["start"], C[0]["dur"] = ns, C[0]["dur"] + pre
        tdir = tempfile.mkdtemp(prefix="raw-yt-title-"); say(f"TRACKPAD 자막 {max(1.0, pre):.1f}초 그리는 중…")
        cmd = ["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "add_title.js"), "--frames", tdir, "--fps", str(FPS), "--w", "1920", "--h", "1080",
               "--len", f"{max(1.0, pre):.2f}", "--title", T["title"], "--name", T.get("name") or ""]
        if T.get("track"): cmd += ["--track", T["track"]]
        if subprocess.run(cmd, stdin=subprocess.DEVNULL).returncode: sys.exit("자막 그리기 실패")
    OUT = float(P.get("outro") or 0); odir = None
    if OUT > 0:   # 끝 RAW 로고 (2026-11-17 "유튜브도"): 마지막 영상을 로고 길이만큼 더 써서 그 위를 덮음 → 음악이 끊기지 않음
        odir = tempfile.mkdtemp(prefix="raw-yt-outro-"); say("끝 로고 그리는 중…")
        if subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "add_title.js"), "--frames", odir, "--page", "outro",
                           "--fps", str(FPS), "--w", "1920", "--h", "1080", "--len", str(OUT)], stdin=subprocess.DEVNULL).returncode: sys.exit("끝 로고 그리기 실패")
    if P.get("height"): H2 = int(P["height"]); W, H = int(round(W * H2 / H / 2)) * 2, H2
    f = pick_song(P); sx = load(f, SR) if f else None
    # 영상마다: 디졸브가 겹치는 만큼 뒤를 X초 더 씀 (마지막 제외) → 각 그룹 춤이 디졸브에 잘리지 않음
    # 원장님 2026-11-18 "첫 영상 엔딩에 멈춰서 2분 8초까지 노래만": 길이가 원본 끝을 넘으면(디졸브용 0.5초 포함) 영상이 끊겨 멈춤
    # → 넣은 길이는 원본 끝까지로 줄이고, 디졸브·로고용 여분이 원본에 없으면 마지막 장면을 잠깐 유지
    for c in C:
        src = fdur(c["video"])
        if c["start"] + c["dur"] > src: say(f"{os.path.basename(c['video'])}: 길이가 원본보다 길어서 원본 끝({src - c['start']:.1f}초)까지로"); c["dur"] = max(0.5, src - c["start"])
    L = [c["dur"] + (X if i < n - 1 else OUT) for i, c in enumerate(C)]
    ins, fc = [], []
    lut = P.get("lut") or ""; s = max(0, min(100, int(P.get("strength") or 100))) / 100
    lpe = lut.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    for i, c in enumerate(C):
        ins += ["-ss", f"{c['start']:.3f}", "-t", f"{L[i]:.3f}", "-i", c["video"]]
        v = f"[{i}:v]fps={FR},scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1"
        if lut:
            v += (f",format=gbrp16le,lut3d=file='{lpe}':interp=tetrahedral" if s >= 0.999 else
                  f",format=gbrp16le,split[a{i}][b{i}];[b{i}]lut3d=file='{lpe}':interp=tetrahedral[l{i}];[a{i}][l{i}]blend=all_mode=normal:all_opacity={s:.2f}")
        v += f",tpad=stop_mode=clone:stop_duration={max(X, OUT) + 1},trim=0:{L[i]:.3f}"   # 모든 영상: 원본이 모자라면 마지막 장면 유지 → 길이가 정확히 L
        fc.append(v + f",format=yuv420p,setpts=PTS-STARTPTS[v{i}]")
    if tdir:   # 자막(1920x1080으로 그림 → 영상 크기에 맞춤)을 1번 영상 맨 앞에
        ins += ["-framerate", FR, "-i", os.path.join(tdir, "%05d.png")]
        fc.append(f"[{n}:v]scale={W}:{H},format=rgba[tt];[v0][tt]overlay=0:0:eof_action=pass,format=yuv420p[v0t]")
    # 소리: 영상마다 깨끗한 음원의 같은 위치, 못 찾으면 그 영상 연습실 소리
    k = n + (1 if tdir else 0); ref = None
    for i, c in enumerate(C):
        o = None
        if sx is not None:
            a0, b0 = max(0, DS[i] - 0.5), min(fdur(c["video"]), c["start"] + L[i] + 0.5)
            o = offset_in(c["video"], sx, a0, b0, near=(DS[i], ref) if ref is not None else None)
            if o is not None and ref is None: ref = DS[i] - o          # 1번 춤 시작 때 노래 위치 = 기준
        if o is not None:
            pos = c["start"] - o; say(f"{i + 1}번 {os.path.basename(c['video'])}: 노래 {pos:.2f}초부터")
            pre = ["-ss", f"{max(0, pos):.4f}"] if pos >= 0 else []
            ins += [*pre, "-t", f"{L[i] + 1:.3f}", "-i", f]
            d = int(round(-pos * 1000)) if pos < 0 else 0
            if d and has_audio(c["video"]):   # 노래가 영상 중간에 시작(자막 구간 등): 그 전까지 연습실 소리(카운트) → 노래 시작에 음원으로
                ds = d / 1000
                fc.append(f"[{i}:a]aresample=48000,atrim=0:{ds + 0.05:.3f},afade=t=out:st={max(0, ds - 0.3):.3f}:d=0.35,apad[r{i}];"
                          f"[{k}:a]aresample=48000,adelay={d}|{d},afade=t=in:st={max(0, ds - 0.05):.3f}:d=0.1,apad[m{i}];"
                          f"[r{i}][m{i}]amix=inputs=2:normalize=0:duration=longest,atrim=0:{L[i]:.3f},asetpts=PTS-STARTPTS[a{i}]")
            else:
                fc.append(f"[{k}:a]" + (f"adelay={d}|{d}," if d else "") + f"aresample=48000,apad,atrim=0:{L[i]:.3f},asetpts=PTS-STARTPTS[a{i}]")
            k += 1
        elif has_audio(c["video"]):
            if sx is not None: say(f"확인필요: {i + 1}번은 음원 위치를 못 찾아 연습실 소리 그대로")
            fc.append(f"[{i}:a]aresample=48000,apad,atrim=0:{L[i]:.3f},asetpts=PTS-STARTPTS[a{i}]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{L[i]:.3f}[a{i}]")
    # 이어 붙이기: 디졸브(xfade) + 소리 크로스페이드, 또는 그냥 컷(concat)
    V0 = "v0t" if tdir else "v0"
    if X > 0 and n > 1:
        cur, t = V0, L[0]
        for i in range(1, n):
            nxt = f"vx{i}" if i < n - 1 else "vcat"
            fc.append(f"[{cur}][v{i}]xfade=transition=fade:duration={X}:offset={t - X:.3f}[{nxt}]"); cur = nxt; t += L[i] - X
        cur = "a0"
        for i in range(1, n):
            nxt = f"ax{i}" if i < n - 1 else "am"
            fc.append(f"[{cur}][a{i}]acrossfade=d={X}:c1=tri:c2=tri[{nxt}]"); cur = nxt
        total = t
    else:
        fc.append("".join(f"[{V0 if i == 0 else f'v{i}'}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vcat][am]"); total = sum(L)
    fc.append("[vcat]null[vout]")
    fc.append(f"[am]afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, total - 1.5):.3f}:d=1.5[aout]")
    nf = int(total * FPS); say(f"총 {total:.1f}초 · {W}x{H} · 영상 {n}개")
    def ff(cmd, nf, label):
        if os.environ.get("RAW_DEBUG"): say(" ".join(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True); last = -1
        for line in p.stdout:
            if line.startswith("frame="):
                fr = int(line.split("=")[1] or 0)
                if fr - last >= max(60, nf // 20): last = fr; say(f"{label} {fr}/{nf}")
        return p.wait()
    head = ["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-nostats", "-progress", "pipe:1", "-y"]
    # 끝 로고는 따로 한 번 더 (같은 그래프에서 소리 크로스페이드와 같이 쓰면 ffmpeg가 멈춤, 2026-11-17 확인)
    # → 1단계는 거의 무손실(crf 10)로 이어 붙이고, 2단계에서 로고만 얹으며 최종 압축. 소리는 그대로 복사
    mid = P["out"] + ".tmp.mp4" if odir else P["out"]
    rc = ff([*head, *ins, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}", "-c:v", "libx264",
             "-crf", "10" if odir else "16", "-preset", "fast" if odir else "medium", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", mid], nf, "영상 합치는 중")
    if not rc and odir:
        rc = ff([*head, "-i", mid, "-framerate", FR, "-i", os.path.join(odir, "%05d.png"), "-filter_complex",
                 f"[1:v]scale={W}:{H},format=rgba,setpts=PTS+{max(0, total - OUT):.3f}/TB[oo];[0:v][oo]overlay=0:0:eof_action=repeat,format=yuv420p[vout]",
                 "-map", "[vout]", "-map", "0:a", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", P["out"]],
                nf, "끝 로고 넣는 중")
        try: os.remove(mid)
        except OSError: pass
    for d in (tdir, odir):
        if d: shutil.rmtree(d, ignore_errors=True)
    if rc: sys.exit("ffmpeg 실패 (영상 합치기)")
    say(P["out"])

# ── 3분할 (원장님 2026-11-18 "가끔 3분할도 필요", 예시: ARIN GIRLISH) ─────────────────────────────
# 세로 1080x1920을 1080x640 세 줄로: 위 = 1번, 가운데 = 2번, 아래 = 3번. 세 영상이 같은 노래 구간을 동시에 (음원 기준으로 맞춤)
# 가운데 줄 위에 TRACKPAD 자막(춤 시작 전 1~5초), 끝에 RAW 로고. 소리는 깨끗한 음원 하나
HERE = os.path.dirname(os.path.abspath(__file__))

def render_frames(page, fps, w, h, length, T=None):
    d = tempfile.mkdtemp(prefix=f"raw-{page}-")
    cmd = ["node", os.path.join(HERE, "add_title.js"), "--frames", d, "--fps", str(fps), "--w", str(w), "--h", str(h), "--len", f"{length:.2f}"]
    if page == "outro": cmd += ["--page", "outro"]
    if T: cmd += ["--title", T["title"], "--name", T.get("name") or ""] + (["--track", T["track"]] if T.get("track") else [])
    if subprocess.run(cmd, stdin=subprocess.DEVNULL).returncode: sys.exit(f"{'끝 로고' if page == 'outro' else '자막'} 그리기 실패")
    return d

def ff(cmd, nf, label):
    if os.environ.get("RAW_DEBUG"): say(" ".join(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True); last = -1
    for line in p.stdout:
        if line.startswith("frame="):
            fr = int(line.split("=")[1] or 0)
            if fr - last >= max(60, nf // 20): last = fr; say(f"{label} {fr}/{nf}")
    return p.wait()

def make_stack3(P):
    C = [dict(c) for c in P["clips"]]
    if len(C) != 3: sys.exit("3분할은 영상이 딱 3개 필요해요 (위 · 가운데 · 아래)")
    W, H, PH = 1080, 1920, 640
    _, _, FR, FPS = probe(C[0]["video"])
    DS = [c["start"] for c in C]; D = min(c["dur"] for c in C)       # 세 줄 길이는 같게 (가장 짧은 것 기준)
    T = P.get("title") or None; tdir = odir = None; pre = 0.0
    if T and (T.get("title") or "").strip():
        N = min(5.0, max(1.0, float(T.get("len") or 5))); pre = min(N, min(DS))      # 세 영상 모두 같은 만큼 앞에서부터 (동시에 움직이게)
        for c in C: c["start"] -= pre
        say(f"TRACKPAD 자막 {max(1.0, pre):.1f}초 그리는 중…"); tdir = render_frames("title", FPS, W, H, max(1.0, pre), T)
    OUT = float(P.get("outro") or 0)
    if OUT > 0: say("끝 로고 그리는 중…"); odir = render_frames("outro", FPS, W, H, OUT)
    L = pre + D + OUT
    f = pick_song(P); sx = load(f, SR) if f else None
    lut = P.get("lut") or ""; s = max(0, min(100, int(P.get("strength") or 100))) / 100
    lpe = lut.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    ins, fc = [], []
    for i, c in enumerate(C):
        ins += ["-ss", f"{c['start']:.3f}", "-t", f"{L:.3f}", "-i", c["video"]]
        v = f"[{i}:v]fps={FR},scale={W}:{PH}:force_original_aspect_ratio=increase,crop={W}:{PH},setsar=1"
        if lut:
            v += (f",format=gbrp16le,lut3d=file='{lpe}':interp=tetrahedral" if s >= 0.999 else
                  f",format=gbrp16le,split[a{i}][b{i}];[b{i}]lut3d=file='{lpe}':interp=tetrahedral[l{i}];[a{i}][l{i}]blend=all_mode=normal:all_opacity={s:.2f}")
        fc.append(v + f",tpad=stop_mode=clone:stop_duration={L + 1:.1f},trim=0:{L:.3f},format=yuv420p,setpts=PTS-STARTPTS[p{i}]")
    fc.append("[p0][p1][p2]vstack=inputs=3[vs]"); last = "vs"
    if tdir:
        ins += ["-framerate", FR, "-i", os.path.join(tdir, "%05d.png")]
        fc.append(f"[3:v]format=rgba[tt];[vs][tt]overlay=0:0:eof_action=pass,format=yuv420p[vt]"); last = "vt"
    fc.append(f"[{last}]null[vout]")
    # 소리: 가운데(전체) 영상 기준으로 깨끗한 음원. 못 찾으면 1·3번 순서로, 그래도 없으면 가운데 연습실 소리
    k = 3 + (1 if tdir else 0); done = False
    O = [None, None, None]; ref = None
    if sx is not None:
        for i in range(3):   # 1번에서 기준 노래 위치를 찾고, 나머지는 '같은 구간'인 후보로
            O[i] = offset_in(C[i]["video"], sx, max(0, DS[i] - 0.5), min(fdur(C[i]["video"]), DS[i] + D + 0.5), near=(DS[i], ref) if ref is not None else None)
            if O[i] is not None and ref is None: ref = DS[i] - O[i]
        for j in range(3):
            if O[j] is not None and abs((DS[j] - O[j]) - ref) > 0.15:
                say(f"확인필요: {j + 1}번 줄이 1번과 {((DS[j] - O[j]) - ref):+.2f}초 어긋나 있어요 → [같은 구간으로 맞추기]를 눌러 주세요")
    for i in [x for x in (1, 0, 2) if O[x] is not None][:1]:   # 소리는 가운데(전체) 영상 기준, 없으면 1·3번
        o = O[i]; pos = C[i]["start"] - o; say(f"음원: {i + 1}번 영상 기준, 노래 {pos:.2f}초부터")
        ins += (["-ss", f"{pos:.4f}"] if pos >= 0 else []) + ["-t", f"{L + 1:.3f}", "-i", f]
        d = int(round(-pos * 1000)) if pos < 0 else 0
        if d and has_audio(C[i]["video"]):
            ds = d / 1000
            fc.append(f"[{i}:a]aresample=48000,atrim=0:{ds + 0.05:.3f},afade=t=out:st={max(0, ds - 0.3):.3f}:d=0.35,apad[r];"
                      f"[{k}:a]aresample=48000,adelay={d}|{d},afade=t=in:st={max(0, ds - 0.05):.3f}:d=0.1,apad[m];"
                      f"[r][m]amix=inputs=2:normalize=0:duration=longest,atrim=0:{L:.3f}[am]")
        else:
            fc.append(f"[{k}:a]" + (f"adelay={d}|{d}," if d else "") + f"aresample=48000,apad,atrim=0:{L:.3f}[am]")
        done = True
    if not done:
        if sx is not None: say("확인필요: 음원 위치를 못 찾아 가운데 영상 연습실 소리 그대로")
        fc.append(f"[1:a]aresample=48000,apad,atrim=0:{L:.3f}[am]" if has_audio(C[1]["video"]) else f"anullsrc=r=48000:cl=stereo,atrim=0:{L:.3f}[am]")
    fc.append(f"[am]afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, L - 1.5):.3f}:d=1.5[aout]")
    nf = int(L * FPS); say(f"총 {L:.1f}초 · 3분할 {W}x{H}")
    head = ["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-nostats", "-progress", "pipe:1", "-y"]
    mid = P["out"] + ".tmp.mp4" if odir else P["out"]
    rc = ff([*head, *ins, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-t", f"{L:.3f}", "-c:v", "libx264",
             "-crf", "10" if odir else "16", "-preset", "fast" if odir else "medium", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", mid], nf, "영상 합치는 중")
    if not rc and odir:   # 끝 로고는 따로 (같은 그래프에 넣으면 ffmpeg가 멈출 수 있음, 2026-11-17)
        rc = ff([*head, "-i", mid, "-framerate", FR, "-i", os.path.join(odir, "%05d.png"), "-filter_complex",
                 f"[1:v]format=rgba,setpts=PTS+{max(0, L - OUT):.3f}/TB[oo];[0:v][oo]overlay=0:0:eof_action=repeat,format=yuv420p[vout]",
                 "-map", "[vout]", "-map", "0:a", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", P["out"]],
                nf, "끝 로고 넣는 중")
        try: os.remove(mid)
        except OSError: pass
    for d_ in (tdir, odir):
        if d_: shutil.rmtree(d_, ignore_errors=True)
    if rc: sys.exit("ffmpeg 실패 (3분할)")
    say(P["out"])

if __name__ == "__main__":
    mode, f = sys.argv[1], sys.argv[2]; P = json.load(open(f, encoding="utf-8"))
    if mode == "--align": print(json.dumps(align(P), ensure_ascii=False))
    elif P.get("layout") == "stack3": make_stack3(P)
    else: make(P)
