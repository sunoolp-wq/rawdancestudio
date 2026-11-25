"""음악에서 실제로 '쾅' 하는 시각 재기 (원장님 2026-11-25: 박자 계산으로 맞춘 예고편이 "노래랑 텍스트랑 너무 안 맞아")
BPM 격자로 계산하지 않고, 소리가 갑자기 커지는 순간(스펙트럼 변화량 봉우리)을 직접 찾는다.
사용: python3 tools/video-kit/beats.py 음원.wav [--top 12] [--min-gap 0.35] [--out 결과.json] [--png 그림.png]
출력 JSON: duration, bpm(참고용), hits[{t, s, low}] (s = 세기 0~1, low = 저음(킥) 세기), strong(센 것 top N, 시간순), sections(분위기가 바뀌는 시각)
"""
import argparse, json, subprocess, sys
import numpy as np
SR, N, HOP = 22050, 2048, 512

def load(path):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

def analyse(y):
    win = np.hanning(N).astype(np.float32)
    nf = 1 + max(0, (len(y) - N) // HOP)
    fr = np.lib.stride_tricks.as_strided(y, (nf, N), (y.strides[0] * HOP, y.strides[0])) * win
    mag = np.log1p(np.abs(np.fft.rfft(fr, axis=1)) * 10)
    d = np.maximum(0, np.diff(mag, axis=0, prepend=mag[:1]))
    lowbin = int(150 / (SR / N))
    flux, low = d.sum(1), d[:, :lowbin].sum(1)
    rms = np.sqrt((fr ** 2).mean(1))
    t = (np.arange(nf) * HOP + N / 2) / SR
    return t, flux, low, rms

def peaks(t, x, min_gap):
    fps = SR / HOP; w = max(1, int(min_gap * fps))
    # 주변 2초 평균+표준편차보다 높은 봉우리만 (조용한 구간의 작은 소리도 잡히게 지역 기준)
    k = int(2 * fps); pad = np.pad(x, k, mode='edge'); cs = np.cumsum(np.insert(pad, 0, 0)); cs2 = np.cumsum(np.insert(pad ** 2, 0, 0))
    m = (cs[2 * k + 1:] - cs[:-2 * k - 1]) / (2 * k + 1); v = (cs2[2 * k + 1:] - cs2[:-2 * k - 1]) / (2 * k + 1) - m ** 2
    thr = m + 0.8 * np.sqrt(np.maximum(v, 0))
    out = []
    for i in range(1, len(x) - 1):
        if x[i] > thr[i] and x[i] == x[max(0, i - w):i + w + 1].max(): out.append(i)
    return out

def bpm(t, flux):
    fps = SR / HOP; x = flux - flux.mean(); ac = np.correlate(x, x, 'full')[len(x) - 1:]
    lags = np.arange(len(ac)); b = 60 * fps / np.maximum(lags, 1); ok = (b >= 70) & (b <= 180)
    return round(float(b[ok][np.argmax(ac[ok])]), 1) if ok.any() else None

def sections(t, rms, step=0.5):
    # 0.5초 평균 음량이 앞 2초보다 확 커지거나 작아지는 지점 = 구간 시작
    n = int(t[-1] / step); e = np.array([rms[(t >= i * step) & (t < (i + 1) * step)].mean() for i in range(n)])
    e = 20 * np.log10(e + 1e-6); out = []
    for i in range(4, n):
        if abs(e[i] - e[i - 4:i].mean()) > 4.5 and (not out or i * step - out[-1] > 2): out.append(round(i * step, 2))
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('audio'); ap.add_argument('--top', type=int, default=12); ap.add_argument('--min-gap', type=float, default=0.35)
    ap.add_argument('--out'); ap.add_argument('--png'); a = ap.parse_args()
    y = load(a.audio); t, flux, low, rms = analyse(y)
    fn, ln = flux / flux.max(), low / (low.max() or 1)
    idx = peaks(t, fn, a.min_gap)
    hits = [{'t': round(float(t[i]), 2), 's': round(float(fn[i]), 2), 'low': round(float(ln[i]), 2)} for i in idx]
    strong = sorted(sorted(hits, key=lambda h: -(h['s'] + 0.5 * h['low']))[:a.top], key=lambda h: h['t'])
    res = {'audio': a.audio, 'duration': round(len(y) / SR, 2), 'bpm': bpm(t, flux), 'strong': strong, 'sections': sections(t, rms), 'hits': hits}
    js = json.dumps(res, ensure_ascii=False, indent=1)
    if a.out: open(a.out, 'w').write(js)
    print(json.dumps({k: res[k] for k in ('duration', 'bpm', 'strong', 'sections')}, ensure_ascii=False))
    if a.png:
        from PIL import Image, ImageDraw
        W, H = 1600, 360; im = Image.new('RGB', (W, H), '#111'); d = ImageDraw.Draw(im); X = lambda s: int(s / res['duration'] * (W - 20)) + 10
        for i in range(0, len(t), 2): d.line([(X(t[i]), H - 30), (X(t[i]), H - 30 - int(fn[i] * 250))], fill='#555')
        for s in res['sections']: d.line([(X(s), 0), (X(s), H)], fill='#2a6cff', width=2)
        for h in strong: d.line([(X(h['t']), 20), (X(h['t']), H - 30)], fill='#ff3b3b', width=2); d.text((X(h['t']) + 3, 22), f"{h['t']}", fill='#fff')
        for s in range(int(res['duration']) + 1): d.text((X(s), H - 20), str(s), fill='#888')
        im.save(a.png)
