"""수업 영상에서 '춤 시작' 장면 후보 찾기 (원장님 2026-11-17 "자동으로 춤 시작장면을 찾을 수 있는가")
사용: python find_start.py --video 수업.mp4 [--dur 15] [--n 3] [--song 음원 파일 또는 음원 폴더]
결과: 마지막 줄에 JSON {"cands": [{"t": 초, "why": 설명, "score": 동작 크기}], "period": 반복 길이}

수업 영상의 흔한 모양 (NOFF·BEI·AD LA 원본으로 확인):
  쌤이 같은 노래 구간을 몇 번씩 반복해서 틀고 춤도 처음부터 다시 춤 → 춤 시작 = '반복이 새로 시작되는 지점'
찾는 순서
  1) 음원이 있으면(파일 또는 음원 폴더에서 자동으로 고름): 영상 속 노래가 음원 몇 초인지 조각마다 찾아서, 노래가 처음부터 다시 시작되는 영상 시각
  2) 음원이 없으면: 영상 소리끼리 비교해서 반복 길이를 찾고, 반복마다 동작이 가장 작은 순간(준비 자세)을 시작으로
  3) 반복이 없으면: 가만히 있다가 움직임이 확 커지는 순간
각 후보는 '그 뒤 dur초 동안 동작 크기'로 점수 → 가장 큰 것이 추천
"""
import argparse, json, os, subprocess, sys
import numpy as np
from audiomatch import load, dur as fdur, Song, windows, match_folder, candidates

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True); ap.add_argument("--dur", type=float, default=15.0); ap.add_argument("--n", type=int, default=3)
ap.add_argument("--song", help="음원 파일 또는 음원 폴더 (없어도 됨)")
a = ap.parse_args()
SR, MF = 8000, 5          # 소리 8kHz, 움직임 초당 5장
D = fdur(a.video)
say = lambda s: print(s, flush=True)

# ── 움직임: 작은 흑백 화면으로 앞뒤 장면 차이 ──────────────
say("움직임 보는 중…")
r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-hwaccel", "auto", "-i", a.video, "-vf", f"fps={MF},scale=96:54,format=gray", "-f", "rawvideo", "-"],
                   capture_output=True, stdin=subprocess.DEVNULL)
v = np.frombuffer(r.stdout, np.uint8)
if len(v) < 96 * 54 * 10:   # 하드웨어 디코딩이 안 되는 맥이면 일반 방식으로
    v = np.frombuffer(subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", a.video, "-vf", f"fps={MF},scale=96:54,format=gray", "-f", "rawvideo", "-"],
                                     capture_output=True, stdin=subprocess.DEVNULL).stdout, np.uint8)
v = v[:len(v) // (96 * 54) * 96 * 54].reshape(-1, 54, 96).astype(np.float32)
mo = np.r_[0, np.abs(np.diff(v, axis=0)).mean((1, 2))]
sm = lambda y, k: np.convolve(y, np.ones(k) / k, "same")
mo1 = sm(mo, MF)                       # 1초 평균
def motion(t0, t1): i0, i1 = int(max(0, t0) * MF), int(min(D, t1) * MF); return float(mo[i0:i1].mean()) if i1 > i0 else 0.0

def settle(t, back=1.5, fwd=1.5):
    """t 근처에서 동작이 가장 작은 순간(준비 자세) → 그 순간이 시작"""
    i0, i1 = int(max(0, t - back) * MF), int(min(D, t + fwd) * MF)
    if i1 <= i0: return t
    return (i0 + int(np.argmin(sm(mo, 3)[i0:i1]))) / MF

x = load(a.video, SR)
cands, period, how = [], None, ""

# ── 1) 음원으로 ──────────────────────────────────────────
song = a.song
if song and os.path.isdir(song):
    say("음원 폴더에서 같은 곡 찾는 중…")
    song, n1, n2, _ = match_folder(a.video, song, log=say)
    if song: say(f"곡: {os.path.basename(song)}")
if song and os.path.isfile(song):
    sx = load(song, SR); S = Song(sx, SR, 3.0); HOP = 1.5
    pts = [(t, t - S.find(w)[0]) for t, w in windows(x, SR, 0.0, 3.0, HOP)]     # (영상 시각, 노래 0:00이 영상 몇 초)
    runs = []
    for o, n in candidates(x, sx, SR, 0.0, min_votes=4):
        ts = sorted(t for t, oo in pts if abs(oo - o) <= 0.08)
        if len(ts) < 4: continue
        # 진짜 반복: 조각들이 끊기지 않고 이어짐 (가끔 섞이는 엉뚱한 표는 띄엄띄엄)
        span = ts[-1] - ts[0] + 3; dens = len(ts) / (span / HOP)
        if dens < 0.6: continue
        t0 = o if -0.5 <= o <= ts[0] + 0.5 else ts[0]; pos = max(0.0, t0 - o)
        runs.append((span * dens + (15 if pos < 1 else 0), max(0.0, t0), "노래 처음(0:00)부터" if pos < 1 else f"노래 {int(pos // 60)}:{int(pos % 60):02d} 지점부터"))
    runs.sort(reverse=True)
    cands = [(t, why) for _, t, why in runs[:a.n]]
    if cands: how = "음원"

# ── 2) 반복 길이로 ───────────────────────────────────────
if not cands and D > 20:
    say("반복 구간 찾는 중…")
    S = Song(x, SR, 3.0); lags = []
    for t in np.arange(0, D - 3, 1.0):
        w = x[int(t * SR):int((t + 3) * SR)]
        if np.sqrt((w ** 2).mean()) < 0.01: continue
        X = S.F * np.conj(np.fft.rfft(w, S.n)); X /= np.abs(X) + 1e-9
        cc = np.fft.irfft(X, S.n)[:len(x) - len(w) + 1]; m = np.abs(cc).mean() + 1e-9
        j0 = int(t * SR); cc[max(0, j0 - 5 * SR):j0 + 5 * SR] = -1
        j = int(np.argmax(cc))
        if cc[j] / m > 60: lags.append(abs(j / SR - t))
    if len(lags) >= max(6, 0.25 * (D - 3)):
        L = np.array(lags); best = None
        for P in np.unique(np.round(L, 1)):
            if P < 6 or P > D / 1.6: continue
            k = np.round(L / P); hit = ((k >= 1) & (np.abs(L - k * P) < 0.2)).mean()
            if best is None or hit > best[0] + 0.05: best = (hit, P)
        if best and best[0] > 0.6:
            P = float(np.median([l / round(l / best[1]) for l in L if round(l / best[1]) >= 1 and abs(l - round(l / best[1]) * best[1]) < 0.2]))
            period = P
            # 반복마다 같은 위상에서 동작이 가장 작은 순간 = 준비 자세 → 그 위상이 춤 시작
            ph = np.arange(0, P, 1 / MF); f = []
            for p in ph:
                ks = [p + k * P for k in range(int(D / P) + 1) if p + k * P < D - 0.5]
                f.append(np.mean([mo1[int(t * MF)] for t in ks]) if ks else 9e9)
            phi = ph[int(np.argmin(f))]
            for k in range(int(D / P) + 1):
                t = phi + k * P
                if t < D - 3: cands.append((settle(t), f"{k + 1}번째 반복 시작 (반복 {P:.1f}초)"))
            how = "반복"

# ── 3) 노래가 시작되는 순간 · 장면이 바뀌는 순간 · 움직임이 확 커지는 순간 ────────────
def beatness():
    """0.5초마다 '박자가 규칙적인 정도'(노래면 높고 말소리·잡음이면 낮음)와 소리 크기"""
    W, H = 512, 128; fps = SR / H
    fr = np.lib.stride_tricks.sliding_window_view(x, W)[::H] * np.hanning(W)
    L = np.log1p(np.abs(np.fft.rfft(fr, axis=1)) * 10); flux = np.r_[0, np.maximum(0, np.diff(L, axis=0)).sum(1)]
    rms = np.sqrt((fr ** 2).mean(1)); win = int(fps * 4); lo, hi = int(fps * 0.28), int(fps * 1.0); out = []
    for i in range(0, len(flux) - win, int(fps * 0.5)):
        e = flux[i:i + win] - flux[i:i + win].mean(); ac = np.correlate(e, e, "full")[win - 1:]; ac /= ac[0] + 1e-9
        out.append((i / fps, float(ac[lo:hi].max()), float(rms[i:i + win].mean())))
    return np.array(out)
if len(cands) < 2:   # 반복으로 찾은 게 1개 이하면 다른 방법 후보도 같이
    n0 = len(cands); B = beatness()
    if len(B) > 8:
        t, per, rm = B[:, 0], sm(B[:, 1], 3), B[:, 2]
        for i in range(4, len(B) - 4):   # 앞 2초보다 뒤 4초가 확실히 '노래'인 순간
            jump = per[i:i + 8].mean() - per[i - 4:i].mean()
            if jump > 0.12 and per[i:i + 8].mean() > 0.3 and rm[i:i + 8].mean() > rm[i - 4:i].mean() * 0.9 and all(abs(t[i] - c[0]) > 8 for c in cands):
                cands.append((settle(t[i] + 1.0, 1.0, 1.5), "노래가 시작되는 순간"))
        mus = [c for c in cands[n0:]][:2]; cands = cands[:n0] + mus
    # 편집된 영상: 장면이 확 바뀌는 순간 (앞뒤보다 화면 차이가 몇 배 큼)
    med = np.median(mo) + 1e-6
    for i in np.argsort(mo)[::-1][:20]:
        nb = np.r_[mo[max(0, i - 10):max(0, i - 2)], mo[i + 3:i + 11]]
        if len(nb) and mo[i] > 4 * np.median(nb) and mo[i] > 3 * med and i / MF < D - 5 and all(abs(i / MF - c[0]) > 6 for c in cands):
            cands.append((i / MF + 0.4, "장면이 바뀌는 순간"))
    rise = np.array([motion(t, t + 2.5) - motion(t - 2.5, t) for t in np.arange(0, D, 0.2)])
    for i in np.argsort(rise)[::-1]:
        t = i * 0.2
        if rise[i] <= 0 or len(cands) >= a.n + 2: break
        if all(abs(t - c[0]) > 6 for c in cands): cands.append((settle(t, 1.0, 0.5), "가만히 있다가 움직이기 시작"))
    how = "섞음" if n0 else "움직임"

# 점수: 시작부터 dur초 동안 동작 크기. 영상 끝이 모자라면 깎음
out = []
for t, why in cands:
    t = round(max(0.0, t), 1); room = min(1.0, (D - t) / a.dur)
    out.append({"t": t, "why": why, "score": round(motion(t, t + a.dur) * room, 2)})
out.sort(key=lambda c: c["t"])
# 너무 많으면 점수 높은 n개 (시간 순서 유지)
if how == "반복": out = out[:a.n]
elif len(out) > a.n:   # 많으면: '노래 시작'은 꼭 넣고 나머지는 동작 큰 순
    must = [c for c in out if c["why"] == "노래가 시작되는 순간"][:2]
    rest = sorted([c for c in out if c not in must], key=lambda c: -c["score"])
    out = sorted(must + rest[:max(0, a.n - len(must))], key=lambda c: c["t"])
if out: max(out, key=lambda c: c["score"])["best"] = True
print(json.dumps({"cands": out, "period": period, "how": how, "dur": round(D, 2)}, ensure_ascii=False))
