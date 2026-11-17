"""영상 속 소리(연습실에서 틀어 둔 노래)와 깨끗한 음원 파일을 맞춰서, 음원으로 바꿔 입히기.
사용: python music_sync.py --video 영상.mp4 --song 음원.mp3 --out 결과.mp4 [--trim-to-song] [--end 초] [--offset 초]
  --trim-to-song : 노래가 시작(0:00)하는 순간부터 영상을 자름 (원장님 2026-11-16 "선생님 시작부터")
  --start/--end  : 쓸 구간 (영상 시각, 초). 노래 찾기도 이 구간 안에서만 (같은 노래를 여러 번 튼 영상 대비)
  --offset       : 자동으로 못 찾을 때 직접 지정. '노래 0:00이 영상 몇 초인지'
찾는 방법 (2026-11-16 AD LA에서 배움): 노래는 8마디마다 같은 반주가 반복돼서 한 구간만 보면 엉뚱한 반복 지점에 맞을 수 있음
  → 영상 3초 구간 여러 개를 노래 전체에서 각각 찾고(PHAT 상호상관), 가장 많이 나온 지점을 씀
"""
import argparse, subprocess, sys, json
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True); ap.add_argument("--song", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--trim-to-song", action="store_true"); ap.add_argument("--start", type=float, default=0.0); ap.add_argument("--end", type=float); ap.add_argument("--offset", type=float)
a = ap.parse_args()
SR = 22050

def load(f, ss=None, t=None):
    cmd = ["ffmpeg", "-nostdin", "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + (["-t", str(t)] if t else []) + ["-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)

def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())

def phat(v, ref):
    n = 1 << int(np.ceil(np.log2(len(ref) + len(v))))
    X = np.fft.rfft(ref, n) * np.conj(np.fft.rfft(v, n)); X /= np.abs(X) + 1e-9
    return np.fft.irfft(X, n)[:len(ref) - len(v) + 1]

VD = dur(a.video)
if a.offset is not None:
    off, conf = a.offset, 1.0
else:
    S0 = a.start; S1 = a.end if a.end else VD
    song = load(a.song); vid = load(a.video, S0, S1 - S0)
    if len(vid) < SR * 3: sys.exit("영상 소리가 너무 짧아요 (3초 이상 필요)")
    cands = []
    for s in np.arange(0, len(vid) / SR - 3, 1.5):
        w = vid[int(s * SR):int((s + 3) * SR)]
        if np.sqrt((w ** 2).mean()) < 0.01: continue          # 조용한 구간은 건너뜀
        cc = phat(w, song); j = int(np.argmax(cc))
        cands.append(round(S0 + s - j / SR, 2))                    # '노래 0:00이 영상 몇 초인지'
    if not cands: sys.exit("영상에 소리가 거의 없어요. --offset 으로 직접 지정해 주세요")
    vals, cnt = np.unique(np.round(np.array(cands) / 0.04) * 0.04, return_counts=True)
    # 비슷한 값(±0.05초)끼리 묶어서 표 세기. 1등이 3표 이상이고 2등의 1.8배 이상이면 확실
    order = np.argsort(cnt)[::-1]; best = vals[order[0]]
    near = [c for c in cands if abs(c - best) <= 0.06]; n1 = len(near)
    n2 = max([sum(1 for c in cands if abs(c - v) <= 0.06) for v in vals[order[1:6]] if abs(v - best) > 0.1] or [0])
    off = float(np.median(near)); conf = n1 / max(1, n1 + n2)
    print(json.dumps({"song0_at_video": round(off, 4), "votes": n1, "second": n2, "windows": len(cands)}, ensure_ascii=False), flush=True)
    if n1 < 3 or n1 < 1.8 * n2:
        sys.exit(f"영상 속 소리에서 이 노래를 확실히 못 찾았어요 ({n1}표 대 {n2}표). 같은 노래·같은 버전인지 확인하거나 --offset 으로 직접 지정해 주세요")

T0 = max(a.start, off) if a.trim_to_song else a.start
T1 = min(a.end, VD) if a.end else VD
D = T1 - T0
s0 = T0 - off                                  # 결과 0초 때 노래 위치
pre = ["-ss", f"{s0:.4f}"] if s0 >= 0 else []
delay = int(round(-s0 * 1000)) if s0 < 0 else 0
af = (f"adelay={delay}|{delay}," if delay else "") + f"apad,atrim=0:{D:.3f},afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, D - 1.2):.3f}:d=1.2"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{T0:.4f}", "-t", f"{D:.4f}", "-i", a.video, *pre, "-i", a.song,
                "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "15", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-t", f"{D:.4f}", "-movflags", "+faststart", a.out], check=True)
print(json.dumps({"out": a.out, "video_start": round(T0, 3), "song_start": round(max(0, s0), 3), "length": round(D, 2)}, ensure_ascii=False))
