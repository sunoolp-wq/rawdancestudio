"""완성 영상 검수 (원장님 2026-11-22 B2 광고: "중복영상이 너무 많이", "28~32초에 또 중복영상", "35초경에 로고가 갑자기", 검은 끝)
사용: python3 tools/video-kit/qa_video.py 결과.mp4 [--out 폴더] [--min-dup 0.8] [--ignore-end 3]
등급: fix = 고쳐야 함(중복·소리 트랙 없음) / check = 의도한 건지 눈으로 확인(검은 화면·무음·번쩍 — 글자 예고편은 일부러 검은 바탕·번쩍 효과를 씀)
찾는 것: ① 같은 장면이 두 번 나옴(중복 영상) ② 검은 화면 ③ 소리 끊김(무음) ④ 갑자기 확 바뀌는 밝기(번쩍·로고 튐 후보) ⑤ 길이·화면 크기·소리 유무
결과: <out>/qa-video.json + <out>/qa-video-sheet.jpg (0.5초마다, 문제 시각 빨간 테두리)
--ignore-end: 끝 몇 초(엔딩 로고 화면)는 중복 검사에서 뺌
"""
import argparse, json, os, re, subprocess, sys
import numpy as np
ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--out'); ap.add_argument('--min-dup', type=float, default=0.8); ap.add_argument('--ignore-end', type=float, default=0.0); ap.add_argument('--fps', type=float, default=4)
a = ap.parse_args(); out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.video)), 'qa'); os.makedirs(out, exist_ok=True)
pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height:format=duration', '-of', 'json', a.video], capture_output=True, text=True, check=True).stdout)
dur = float(pr['format']['duration']); vs = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]; has_audio = any(s['codec_type'] == 'audio' for s in pr['streams'])
W, H, F = 64, 112 if vs['height'] > vs['width'] else 36, a.fps
raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', a.video, '-vf', f'fps={F},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
n = len(raw) // (W * H); g = np.frombuffer(raw[:n * W * H], np.uint8).reshape(n, H, W).astype(np.float32); ts = np.arange(n) / F
lum = g.mean((1, 2)); z = (g - g.mean((1, 2), keepdims=True)) / (g.std((1, 2), keepdims=True) + 1e-3)
issues = []
# ① 중복: 서로 2초 넘게 떨어진 두 시각의 화면이 비슷하고, 그게 min-dup초 이상 이어지면. 그 사이가 계속 같은 화면(멈춘 장면)이면 제외
lim = n - int(a.ignore_end * F); k = max(2, int(a.min_dup * F))
flat = z[:lim].reshape(lim, -1); S = (flat @ flat.T) / flat.shape[1]   # 상관계수(-1~1)
step = np.abs(np.diff(g[:lim], axis=0)).mean((1, 2)) if lim > 1 else np.zeros(0)
seen = set()
for i in range(lim):
    for j in range(i + int(2 * F), lim - k + 1):
        if (i, j) in seen or S[i, j] < 0.93: continue
        m = 0
        while i + m < lim and j + m < lim and S[i + m, j + m] > 0.9 and lum[i + m] > 20: m += 1
        # 사이에 '다른 장면'이 0.75초 이상 있었어야 진짜 중복 (같은 장면이 이어지는 반복 동작·번쩍 효과·멈춘 끝 화면은 제외)
        if m >= k and step[i:j].max() > 18 and (S[i, i + 1:j] < 0.5).sum() >= 0.75 * F:
            issues.append({'lv': 'fix', 'kind': '중복 영상', 'first': [round(ts[i], 2), round(ts[i + m - 1] + 1 / F, 2)], 'again': [round(ts[j], 2), round(ts[j + m - 1] + 1 / F, 2)], 'sim': round(float(S[i:i + m, j:j + m].diagonal().mean()), 2)})
            for q in range(m): seen.add((i + q, j + q))
# ② 검은 화면
bd = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', a.video, '-vf', 'blackdetect=d=0.2:pix_th=0.08', '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
for s, e in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', bd): issues.append({'lv': 'check', 'kind': '검은 화면', 'at': [round(float(s), 2), round(float(e), 2)]})
# ③ 무음
if has_audio:
    sd = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', a.video, '-af', 'silencedetect=n=-45dB:d=0.6', '-vn', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = re.findall(r'silence_start: ([\d.]+)', sd); en = re.findall(r'silence_end: ([\d.]+)', sd)
    for i, s in enumerate(st): issues.append({'lv': 'check', 'kind': '소리 없음', 'at': [round(float(s), 2), round(float(en[i]), 2) if i < len(en) else round(dur, 2)]})
else: issues.append({'lv': 'fix', 'kind': '소리 트랙 없음'})
# ④ 밝기 급변 (컷 전환은 정상이라 '튐' 후보만: 0.25초 안에 확 밝아졌다 바로 돌아옴)
for i in range(1, n - 1):
    if lum[i] - lum[i - 1] > 45 and lum[i] - lum[i + 1] > 45: issues.append({'lv': 'check', 'kind': '번쩍 튐(한 장면만 밝음)', 'at': round(ts[i], 2)})
rep = {'video': a.video, 'duration': round(dur, 2), 'size': [vs['width'], vs['height']], 'audio': has_audio, 'ok': not any(x['lv'] == 'fix' for x in issues), 'issues': issues}
open(os.path.join(out, 'qa-video.json'), 'w').write(json.dumps(rep, ensure_ascii=False, indent=1))
# 미리보기: 0.5초마다
from PIL import Image, ImageDraw
bad = []
for x in issues:
    for key in ('first', 'again', 'at'):
        v = x.get(key)
        if isinstance(v, list): bad.append(tuple(v))
        elif v is not None: bad.append((v, v + 0.25))
raw2 = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', a.video, '-vf', 'fps=2,scale=135:-2', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
tw = 135; th = int(round(tw * vs['height'] / vs['width'] / 2) * 2); m2 = len(raw2) // (tw * th * 3); fr = np.frombuffer(raw2[:m2 * tw * th * 3], np.uint8).reshape(m2, th, tw, 3)
cols = 12; rows = (m2 + cols - 1) // cols; sh = Image.new('RGB', (cols * tw, rows * (th + 16)), '#111'); d = ImageDraw.Draw(sh)
for i, f in enumerate(fr):
    t = i / 2; x, y = (i % cols) * tw, (i // cols) * (th + 16); sh.paste(Image.fromarray(f), (x, y + 16))
    hit = any(s <= t + 0.25 and t <= e for s, e in bad); d.text((x + 3, y + 2), f'{t:.1f}', fill='#ff4d4d' if hit else '#ddd')
    if hit: d.rectangle([x, y + 16, x + tw - 1, y + 16 + th - 1], outline='#ff2d55', width=3)
sh.save(os.path.join(out, 'qa-video-sheet.jpg'), quality=85)
print(json.dumps({**{k: rep[k] for k in ('duration', 'size', 'audio', 'ok')}, 'issues': issues, 'sheet': os.path.join(out, 'qa-video-sheet.jpg')}, ensure_ascii=False, indent=1))
