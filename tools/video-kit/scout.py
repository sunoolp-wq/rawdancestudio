"""소스 영상 훑기 + 쓴 구간 기록 (원장님 2026-11-22 B2 광고: "중복영상이 너무 많이", "35초경에 로고가 갑자기", 어두운 끝·검은 화면)
사용:
  python3 tools/video-kit/scout.py sheet 영상.mp4 [--every 1] [--start 0 --end 끝] [--out 미리보기.jpg] [--json 상태.json]
     → 장면 미리보기 한 장(시각 표시) + 초마다 밝기·선명도·움직임, 어두운(DARK)·흐린(BLUR)·멈춘(STILL) 구간을 빨간 글씨로 표시
  python3 tools/video-kit/scout.py used add  --project content/<폴더> --src 영상.mp4 --start 3.0 --end 5.5 [--note 장면]
  python3 tools/video-kit/scout.py used check --project content/<폴더> --src 영상.mp4 --start 3.0 --end 5.5
  python3 tools/video-kit/scout.py used list --project content/<폴더>
     → content/<폴더>/used-footage.json 에 '어느 영상 몇 초~몇 초를 썼는지' 기록. 같은 구간을 또 쓰면 check가 알려 줌
"""
import argparse, json, os, subprocess, sys
import numpy as np

def probe(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration', '-of', 'json', p], capture_output=True, text=True, check=True).stdout
    j = json.loads(o); s = j['streams'][0]; return float(j['format']['duration']), s['width'], s['height']

def frames(p, every, start, end, tw):
    dur, w, h = probe(p); end = min(end or dur, dur); th = int(round(tw * h / w / 2) * 2)
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(start), '-to', str(end), '-i', p, '-vf', f'fps=1/{every},scale={tw}:{th}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    n = len(raw) // (tw * th * 3); arr = np.frombuffer(raw[:n * tw * th * 3], np.uint8).reshape(n, th, tw, 3)
    return arr, [round(start + i * every, 2) for i in range(n)], dur, (w, h)

def stats(arr):
    g = arr.astype(np.float32) @ np.array([.299, .587, .114], np.float32)
    lum = g.mean((1, 2))
    lap = np.abs(4 * g[:, 1:-1, 1:-1] - g[:, :-2, 1:-1] - g[:, 2:, 1:-1] - g[:, 1:-1, :-2] - g[:, 1:-1, 2:]).mean((1, 2))
    mot = np.concatenate([[0], np.abs(np.diff(g, axis=0)).mean((1, 2))])
    return lum, lap, mot

def runs(ts, flags, every):
    out, s = [], None
    for t, f in zip(ts + [None], list(flags) + [False]):
        if f and s is None: s = t
        if not f and s is not None: out.append([s, round((t if t is not None else ts[-1] + every), 2)]); s = None
    return out

def cmd_sheet(a):
    arr, ts, dur, (W, H) = frames(a.video, a.every, a.start, a.end, 320)
    lum, lap, mot = stats(arr); sharp_ref = np.median(lap) if len(lap) else 1
    dark, blur, still = lum < 35, lap < 0.45 * sharp_ref, mot < 1.2
    info = {'video': a.video, 'duration': round(dur, 2), 'size': [W, H], 'orientation': 'vertical' if H > W else 'horizontal',
            'dark': runs(ts, dark, a.every), 'blurry': runs(ts, blur, a.every), 'still': runs(ts, still, a.every),
            'per_sec': [{'t': t, 'lum': round(float(l)), 'sharp': round(float(s), 1), 'motion': round(float(m), 1)} for t, l, s, m in zip(ts, lum, lap, mot)]}
    if a.json: open(a.json, 'w').write(json.dumps(info, ensure_ascii=False, indent=1))
    print(json.dumps({k: info[k] for k in ('duration', 'size', 'orientation', 'dark', 'blurry', 'still')}, ensure_ascii=False))
    from PIL import Image, ImageDraw
    th, tw = arr.shape[1], arr.shape[2]; cols = 8 if W > H else 10; tw2 = 240 if W > H else 160; th2 = int(tw2 * th / tw)
    rows = (len(arr) + cols - 1) // cols; sheet = Image.new('RGB', (cols * tw2, max(1, rows) * (th2 + 22)), '#111'); d = ImageDraw.Draw(sheet)
    for i, (f, t) in enumerate(zip(arr, ts)):
        x, y = (i % cols) * tw2, (i // cols) * (th2 + 22); sheet.paste(Image.fromarray(f).resize((tw2, th2)), (x, y + 22))
        tag = ' '.join(x for x, f in (('DARK', dark[i]), ('BLUR', blur[i]), ('STILL', still[i])) if f)
        d.text((x + 4, y + 4), f'{t:.1f}s' + (' ' + tag if tag else ''), fill='#ff6b6b' if tag else '#fff')
    out = a.out or os.path.splitext(a.video)[0] + '_sheet.jpg'; sheet.save(out, quality=85); print(out)

def ledger(project):
    p = os.path.join(project, 'used-footage.json')
    return p, (json.load(open(p)) if os.path.exists(p) else [])

def overlaps(L, src, s, e):
    b = os.path.basename(src)
    return [u for u in L if os.path.basename(u['src']) == b and u['start'] < e and s < u['end']]

def cmd_used(a):
    p, L = ledger(a.project)
    if a.op == 'list':
        for u in sorted(L, key=lambda u: (u['src'], u['start'])): print(f"{os.path.basename(u['src'])}  {u['start']:.2f}~{u['end']:.2f}  {u.get('note', '')}")
        return
    hit = overlaps(L, a.src, a.start, a.end)
    if a.op == 'check':
        print(json.dumps({'ok': not hit, 'overlaps': hit}, ensure_ascii=False)); sys.exit(1 if hit else 0)
    if hit and not a.force: print(json.dumps({'ok': False, 'overlaps': hit, 'msg': '이미 쓴 구간과 겹침 (일부러 다시 쓰면 --force)'}, ensure_ascii=False)); sys.exit(1)
    L.append({'src': a.src, 'start': a.start, 'end': a.end, 'note': a.note or ''}); os.makedirs(a.project, exist_ok=True)
    open(p, 'w').write(json.dumps(L, ensure_ascii=False, indent=1)); print(json.dumps({'ok': True, 'saved': p}, ensure_ascii=False))

ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
s = sp.add_parser('sheet'); s.add_argument('video'); s.add_argument('--every', type=float, default=1.0); s.add_argument('--start', type=float, default=0.0); s.add_argument('--end', type=float); s.add_argument('--out'); s.add_argument('--json')
u = sp.add_parser('used'); u.add_argument('op', choices=['add', 'check', 'list']); u.add_argument('--project', required=True); u.add_argument('--src'); u.add_argument('--start', type=float); u.add_argument('--end', type=float); u.add_argument('--note'); u.add_argument('--force', action='store_true')
a = ap.parse_args(); cmd_sheet(a) if a.cmd == 'sheet' else cmd_used(a)
