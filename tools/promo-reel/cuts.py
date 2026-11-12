#!/usr/bin/env python3
"""광고 릴스 컷 만들기: 4K 가로 원본 → 9:16 세로 조각 (박자 그리드에 정확한 프레임 수)
사용: .venv/bin/python tools/promo-reel/cuts.py --plan plan.json --src 원본폴더 --out 조각폴더
plan.json: {"fps": [24000,1001], "segments": [{"t0":0, "t1":2.382, "mode":"full|tall|wide|yolo", "src":"C2128.MP4", "ss":1.118, "cx":0.5, "pick_t":0.5, "shape":"tall"}]}
- full: 16:9 전체를 가운데에, 위아래는 같은 영상 흐리게
- tall: 9:16 고정 자르기 (cx = 가로 중심 0~1)
- wide: 4:5 고정 자르기를 가운데에 + 흐린 배경
- yolo: 선생님 따라가기 (tools/class-reel/follow_yolo.py, cx = 처음 선생님 위치)
원본 소리는 넣지 않는다 (음악은 마지막에 한 번에)."""
import argparse, json, os, subprocess, sys

ap = argparse.ArgumentParser(); ap.add_argument("--plan"); ap.add_argument("--src"); ap.add_argument("--out"); ap.add_argument("--only", default="")
a = ap.parse_args(); P = json.load(open(a.plan)); os.makedirs(a.out, exist_ok=True)
FN, FD = P.get("fps", [24000, 1001]); FPS = FN / FD; RATE = f"{FN}/{FD}"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = os.path.join(ROOT, ".venv", "bin", "python")
ENC = ["-c:v", "libx264", "-crf", "15", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", RATE, "-an"]

def frames(seg): return round(seg["t1"] * FPS) - round(seg["t0"] * FPS)

def bg(cx):  # 9:16 같은 영상을 흐리고 어둡게
    return (f"crop=ih*9/16:ih:max(0\\,min(iw-ih*9/16\\,iw*{cx}-ih*9/32)):0,scale=1080:1920,"
            f"boxblur=40:2,eq=brightness=-0.12:saturation=0.9")

for i, s in enumerate(P["segments"]):
    if a.only and str(i) not in a.only.split(","): continue
    n = frames(s); out = os.path.join(a.out, f"{i:02d}.mp4"); src = os.path.join(a.src, s["src"]); cx = s.get("cx", 0.5)
    if s["mode"] == "yolo":
        tmp = os.path.join(a.out, f"{i:02d}_y.mp4")
        subprocess.run([PY, os.path.join(ROOT, "tools/class-reel/follow_yolo.py"), "--video", src, "--start", str(s["ss"]),
                        "--dur", f"{n / FPS + 0.4:.3f}", "--pick-x", str(cx), "--pick-t", str(s.get("pick_t", 0.3)),
                        "--shape", s.get("shape", "tall"), "--denoise", "0", "--crf", "15", "--out", tmp], check=True)
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-frames:v", str(n), "-vf", "scale=1080:1920,setsar=1"] + ENC + [out]
    else:
        if s["mode"] == "tall":
            vf = f"[0:v]crop=ih*9/16:ih:max(0\\,min(iw-ih*9/16\\,iw*{cx}-ih*9/32)):0,scale=1080:1920,setsar=1[v]"
        elif s["mode"] == "wide":
            vf = (f"[0:v]split[a][b];[a]{bg(cx)}[g];[b]crop=ih*4/5:ih:max(0\\,min(iw-ih*4/5\\,iw*{cx}-ih*2/5)):0,scale=1080:1350[f];"
                  f"[g][f]overlay=0:285,setsar=1[v]")
        else:  # full
            vf = f"[0:v]split[a][b];[a]{bg(cx)}[g];[b]scale=1080:608[f];[g][f]overlay=0:656,setsar=1[v]"
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(s["ss"]), "-i", src, "-frames:v", str(n),
               "-filter_complex", vf, "-map", "[v]"] + ENC + [out]
    subprocess.run(cmd, check=True)
    print(f"{i:02d} {s['mode']:5s} {s['src']} {s['ss']}s → {n}프레임", flush=True)
