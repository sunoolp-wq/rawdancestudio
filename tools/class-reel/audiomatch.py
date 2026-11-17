"""영상 속 소리 ↔ 음원 맞추기 공통 부품 (music_sync.py, find_start.py가 같이 씀)
- 영상 소리를 3초 조각으로 잘라 노래 전체에서 각각 위치를 찾음 (PHAT 상호상관, 노래 FFT는 한 번만 계산)
- 음원 폴더에서 맞는 곡 찾기: 곡마다 조각들이 같은 지점을 가리키는 표 수를 세서 1등 곡을 고름 (원장님 2026-11-17 "음원은 내가 받아서 줄게")
"""
import os, subprocess
import numpy as np

AUDIO_EXT = (".mp3", ".wav", ".m4a", ".aac", ".flac", ".aif", ".aiff", ".ogg")

def load(f, sr, ss=None, t=None):
    cmd = ["ffmpeg", "-nostdin", "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + (["-t", str(t)] if t else []) + ["-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL).stdout, np.float32)

def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return float(r.stdout.strip() or 0)

class Song:
    """노래 하나. 같은 길이 조각을 여러 번 찾을 때 노래 FFT를 다시 계산하지 않음"""
    def __init__(self, x, sr, win):
        self.x, self.sr, self.win = x, sr, int(win * sr)
        self.n = 1 << int(np.ceil(np.log2(len(x) + self.win)))
        self.F = np.fft.rfft(x, self.n)
    def find(self, w):
        """조각 w가 노래 몇 초에 있는지 → (위치 초, 확실한 정도: 1등 봉우리 / 평균 잡음)"""
        X = self.F * np.conj(np.fft.rfft(w, self.n)); X /= np.abs(X) + 1e-9
        cc = np.fft.irfft(X, self.n)[:max(1, len(self.x) - len(w) + 1)]
        j = int(np.argmax(cc)); return j / self.sr, float(cc[j] / (np.abs(cc).mean() + 1e-9))

def windows(vid, sr, start=0.0, win=3.0, hop=1.5, quiet=0.01, limit=None):
    """영상 소리에서 조각 시작 시각(영상 기준 초)과 조각들. 조용한 조각은 뺌. limit개 넘으면 고르게 줄임"""
    ts = [s for s in np.arange(0, len(vid) / sr - win, hop)]
    out = []
    for s in ts:
        w = vid[int(s * sr):int((s + win) * sr)]
        if np.sqrt((w ** 2).mean()) >= quiet: out.append((start + s, w))
    if limit and len(out) > limit: out = [out[i] for i in np.linspace(0, len(out) - 1, limit).round().astype(int)]
    return out

def vote(cands):
    """cands: '노래 0:00이 영상 몇 초인지' 값들 → (가장 많은 값, 그 표 수, 2등 표 수)"""
    if not cands: return None, 0, 0
    c = np.array(cands); vals, cnt = np.unique(np.round(c / 0.04) * 0.04, return_counts=True)
    order = np.argsort(cnt)[::-1]; best = vals[order[0]]
    near = c[np.abs(c - best) <= 0.06]; n1 = len(near)
    n2 = max([int((np.abs(c - v) <= 0.06).sum()) for v in vals[order[1:6]] if abs(v - best) > 0.1] or [0])
    return float(np.median(near)), n1, n2

def best_offset(vid, x, sr, start=0.0, log=print):
    """영상 소리 vid(영상 start초부터)와 노래 x → (노래 0:00 = 영상 몇 초, 확실한지, 설명)
    2026-11-17 원장님 ARIN TRACKPAD '5표 대 5표'로 멈춤: 노래에 같은 반주가 반복돼서 3초 조각은 두 군데에 똑같이 맞음
    → 3초로 결론이 안 나면 6초 · 12초 조각으로 다시 (길수록 반복 구간 밖의 차이까지 들어가 하나로 좁혀짐)
    → 그래도 비기면 두 후보 지점의 노래 소리 자체를 비교: 이 영상 길이만큼 똑같은 소리면 어느 쪽을 써도 같으니 앞쪽을 씀"""
    first = None; tried = []
    for win in (3.0, 6.0, 12.0):
        wins = windows(vid, sr, start, win, win / 2)
        if len(wins) < 3: break
        S = Song(x, sr, win); cands = [round(t - S.find(w)[0], 2) for t, w in wins]
        off, n1, n2 = vote(cands); tried.append(f"{win:g}초 조각 {n1}표 대 {n2}표")
        if first is None: first = cands
        if n1 >= 3 and n1 >= 1.8 * max(n2, 1): return off, True, " → ".join(tried)
    if not first: return None, False, "소리 조각이 부족해요"
    # 1·2등 후보의 노래 소리가 이 영상 길이만큼 같은지
    c = np.array(first); vals, cnt = np.unique(np.round(c / 0.04) * 0.04, return_counts=True); order = np.argsort(cnt)[::-1]
    tops = [float(np.median(c[np.abs(c - vals[i]) <= 0.06])) for i in order[:2]]
    if len(tops) == 2 and abs(tops[0] - tops[1]) > 0.1:
        L = len(vid) / sr; seg = []
        for o in tops:
            a = int(max(0, start - o) * sr); seg.append(x[a:a + int(L * sr)])
        n = min(len(seg[0]), len(seg[1]))
        if n > sr * 3:
            sa, sb = seg[0][:n] - seg[0][:n].mean(), seg[1][:n] - seg[1][:n].mean()
            r = float((sa * sb).sum() / (np.sqrt((sa ** 2).sum() * (sb ** 2).sum()) + 1e-9)); tried.append(f"두 후보 노래 소리 닮은 정도 {r:.2f}")
            if r > 0.8: return min(tops), True, " → ".join(tried) + " (같은 반복 구간이라 어느 쪽이든 같은 소리)"
    off, n1, n2 = vote(first)
    return off, False, " → ".join(tried)

def candidates(vid, x, sr, start=0.0, min_votes=3):
    """3초 조각 기준 후보들 [(노래 0:00 = 영상 몇 초, 표 수)] 표 많은 순. 수업 중 쌤이 노래를 처음부터 다시 틀면 후보가 여러 개"""
    wins = windows(vid, sr, start); S = Song(x, sr, 3.0); c = np.array([round(t - S.find(w)[0], 2) for t, w in wins])
    out = []
    while len(c):
        o, n1, _ = vote(list(c))
        if n1 < min_votes: break
        out.append((o, n1)); c = c[np.abs(c - o) > 0.06]
    return out

def offset(song, wins):
    """노래 하나와 영상 조각들 → (노래 0:00 = 영상 몇 초, 표 수, 2등 표 수)"""
    return vote([round(t - song.find(w)[0], 2) for t, w in wins])

def song_files(folder):
    out = []
    for dp, _, fs in os.walk(os.path.expanduser(folder)):
        out += [os.path.join(dp, f) for f in fs if f.lower().endswith(AUDIO_EXT) and not f.startswith(".")]
    return sorted(out)

def match_folder(video, folder, start=0.0, end=None, sr=8000, log=print):
    """음원 폴더에서 영상 속 노래와 같은 곡 찾기 → (파일, 표 수, 2등 곡 표 수) 또는 (None, ...)"""
    files = song_files(folder)
    if not files: return None, 0, 0, []
    D = (end or dur(video)) - start
    vid = load(video, sr, start, D); wins = windows(vid, sr, start, limit=30)
    if len(wins) < 3: return None, 0, 0, []
    res = []
    for f in files:
        x = load(f, sr)
        if len(x) < sr * 5: continue
        _, n1, _ = offset(Song(x, sr, 3.0), wins); res.append((n1, f))
    res.sort(reverse=True)
    log("음원 폴더 비교: " + " · ".join(f"{os.path.basename(f)} {n}표" for n, f in res[:4]))
    if not res: return None, 0, 0, []
    n1 = res[0][0]; n2 = res[1][0] if len(res) > 1 else 0
    return (res[0][1] if n1 >= 3 and n1 >= 1.8 * max(n2, 1) else None), n1, n2, res
