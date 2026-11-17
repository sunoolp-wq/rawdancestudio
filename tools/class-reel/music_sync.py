"""영상 속 소리(연습실에서 틀어 둔 노래)와 깨끗한 음원 파일을 맞춰서, 음원으로 바꿔 입히기.
사용: python music_sync.py --video 영상.mp4 --song 음원.mp3(또는 음원 폴더) --out 결과.mp4 [--trim-to-song] [--end 초] [--offset 초]
  --trim-to-song : 노래가 시작(0:00)하는 순간부터 영상을 자름 (원장님 2026-11-16 "선생님 시작부터")
  --start/--end  : 쓸 구간 (영상 시각, 초). 노래 찾기도 이 구간 안에서만 (같은 노래를 여러 번 튼 영상 대비)
  --offset       : 자동으로 못 찾을 때 직접 지정. '노래 0:00이 영상 몇 초인지'
찾는 방법 (2026-11-16 AD LA에서 배움): 노래는 8마디마다 같은 반주가 반복돼서 한 구간만 보면 엉뚱한 반복 지점에 맞을 수 있음
  → 영상 3초 구간 여러 개를 노래 전체에서 각각 찾고(PHAT 상호상관), 가장 많이 나온 지점을 씀
"""
import argparse, sys, json, os, subprocess
import numpy as np
from audiomatch import load, dur, best_offset, candidates, match_folder

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True); ap.add_argument("--song", required=True, help="음원 파일 또는 음원 폴더(폴더면 맞는 곡을 자동으로 찾음)"); ap.add_argument("--out")
ap.add_argument("--pre-room", action="store_true", help="노래가 영상 중간에 시작되면 그 전까지는 연습실 원래 소리(카운트 등) → 노래 시작에 음원으로 자연스럽게")
ap.add_argument("--find-only", action="store_true", help="찾기만 하고 JSON {find, song, offset, sure} 출력 (영상은 안 만듦)")
ap.add_argument("--match-pad", type=float, default=0.0, help="음원 폴더에서 곡을 고를 때 쓸 구간을 앞뒤로 이만큼 넓힘 (짧은 영상 대비)")
ap.add_argument("--fade-out", type=float, default=1.2, help="끝 페이드아웃(초). 뒤에서 따로 처리하면 0")
ap.add_argument("--trim-to-song", action="store_true"); ap.add_argument("--start", type=float, default=0.0); ap.add_argument("--end", type=float); ap.add_argument("--offset", type=float)
a = ap.parse_args()
SR = 22050

VD = dur(a.video)
if os.path.isdir(a.song):
    if a.offset is not None: sys.exit("음원 폴더를 줄 때는 --offset 을 같이 쓸 수 없어요 (곡을 먼저 골라야 해서)")
    f, n1, n2, _ = match_folder(a.video, a.song, max(0.0, a.start - a.match_pad), min(VD, (a.end or VD) + a.match_pad), log=lambda s: print(s, flush=True))
    if not f: sys.exit(f"음원 폴더에서 이 영상 노래를 못 찾았어요 ({n1}표 대 {n2}표). 같은 곡·같은 버전(스피드업·리믹스 아님) 파일을 폴더에 넣어 주세요")
    print(json.dumps({"matched_song": os.path.basename(f), "votes": n1, "second_song": n2}, ensure_ascii=False), flush=True); a.song = f
ok = True
if a.offset is not None:
    off = a.offset
else:
    S0 = a.start; S1 = a.end if a.end else VD
    song = load(a.song, SR); vid = load(a.video, SR, S0, S1 - S0)
    if len(vid) < SR * 3: sys.exit("영상 소리가 너무 짧아요 (3초 이상 필요)")
    off, ok, how = best_offset(vid, song, SR, S0, log=lambda m: print(m, flush=True))
    print(json.dumps({"song0_at_video": None if off is None else round(off, 4), "how": how}, ensure_ascii=False), flush=True)
    if not ok:
        # 비기는 흔한 이유: 쌤이 영상 중간에 노래를 처음부터 다시 틈 (2026-11-17 AD LA 원본: 30초마다 다시 틂) → 두 위치 다 맞음
        cs = candidates(vid, song, SR, S0); inclip = sorted(o for o, n in cs if S0 <= o <= S1 - 5)
        ok = False
        if a.trim_to_song and inclip:
            off = inclip[0]; print(f"노래가 영상 {off:.1f}초에 처음부터 다시 시작돼요 → 그 지점부터 씀", flush=True)
        elif cs:
            off = cs[0][0]
            print(f"확인필요: 음원 위치가 확실하지 않아요 ({how}). 후보 '노래 0:00 = 영상 " + " / ".join(f"{o:.2f}초" for o, n in cs[:3])
                  + "'. 결과에서 박자가 어긋나면 '노래 0:00 = 영상 몇 초' 칸에 다른 후보를 넣어 다시 만들어 주세요", flush=True)
        else:
            sys.exit(f"영상 속 소리에서 이 노래를 못 찾았어요 ({how}). 같은 노래·같은 버전(스피드업·리믹스 아님)인지 확인하거나, '노래 0:00 = 영상 몇 초' 칸에 직접 넣어 주세요")

if a.find_only:
    print(json.dumps({"find": True, "song": a.song, "offset": round(off, 4), "sure": ok}, ensure_ascii=False)); sys.exit(0)
if not a.out: sys.exit("--out 이 필요해요")
T0 = max(a.start, off) if a.trim_to_song else a.start
T1 = min(a.end, VD) if a.end else VD
D = T1 - T0
s0 = T0 - off                                  # 결과 0초 때 노래 위치
pre = ["-ss", f"{s0:.4f}"] if s0 >= 0 else []
delay = int(round(-s0 * 1000)) if s0 < 0 else 0
fo = f",afade=t=out:st={max(0, D - a.fade_out):.3f}:d={a.fade_out}" if a.fade_out > 0 else ""
if delay and a.pre_room:
    # 노래 시작 0.3초 전부터 연습실 소리를 줄이고 음원을 올림 (원장님 2026-11-17 TRACKPAD 춤 시작 전 자막 구간)
    d = delay / 1000
    fc = (f"[0:a]atrim=0:{d + 0.05:.3f},afade=t=out:st={max(0, d - 0.3):.3f}:d=0.35,apad[r];"
          f"[1:a]adelay={delay}|{delay},afade=t=in:st={max(0, d - 0.05):.3f}:d=0.1,apad[m];"
          f"[r][m]amix=inputs=2:normalize=0:duration=longest,atrim=0:{D:.3f}{fo}[a]")
else:
    fc = "[1:a]" + (f"adelay={delay}|{delay}," if delay else "") + f"apad,atrim=0:{D:.3f},afade=t=in:st=0:d=0.05{fo}[a]"
whole = T0 <= 0.001 and abs(T1 - VD) < 0.05         # 자르지 않으면 영상은 다시 압축하지 않고 그대로 (화질 보존)
vin = ["-i", a.video] if whole else ["-ss", f"{T0:.4f}", "-t", f"{D:.4f}", "-i", a.video]
venc = ["-c:v", "copy"] if whole else ["-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p"]
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *vin, *pre, "-i", a.song,
                "-filter_complex", fc, "-map", "0:v", "-map", "[a]", *venc, "-c:a", "aac", "-b:a", "320k", "-t", f"{D:.4f}", "-movflags", "+faststart", a.out], check=True)
print(json.dumps({"out": a.out, "video_start": round(T0, 3), "song_start": round(max(0, s0), 3), "length": round(D, 2)}, ensure_ascii=False))
