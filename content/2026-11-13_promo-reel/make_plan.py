#!/usr/bin/env python3
# 40초 광고 릴스 컷 계획 → plan.json (음악 Modern World 115BPM, 음악 6.5초부터 사용 → 영상 2.382초 = 첫 큰 킥)
import json, os
BAR = 4 * 60 / 114.84375; G0 = 2.382
def b(n): return round(G0 + n * BAR, 4)
S = []
def add(t0, t1, mode, src, ss, cx=0.5, **k): S.append(dict(t0=t0, t1=t1, mode=mode, src=src + ".MP4", ss=ss, cx=cx, **k))
add(0, G0, "full", "C2128", 1.118)                         # 한 줄로 가만히 (16:9 전체)
add(G0, b(1), "yolo", "C2128", 3.5, 0.49)                  # 첫 킥에 터짐 → 세로로 확
add(b(1), b(2), "yolo", "C2224", 7.4, 0.5)                 # 쌤이 걸어옴
add(b(2), b(3), "wide", "C2230", 3.5, 0.5)                 # 핑크 2인
add(b(3), b(4), "yolo", "C2051", 23.6, 0.45)               # 자주 후드 쌤
add(b(4), b(5), "yolo", "C2037", 0.6, 0.62, pick_t=1.0)    # 앞줄 댄서
add(b(5), b(6), "yolo", "C2059", 11.5, 0.5)                # 빨간 티 쌤
add(b(6), b(7), "wide", "C2167", 0.0, 0.5)                 # 초록 조명 비하인드
add(b(7), b(8), "tall", "C2259", 0.5, 0.45)                # 쌤 피드백
add(b(8), b(9), "yolo", "C2204", 3.0, 0.8, pick_t=1.0)     # 웃는 학생
add(b(9), b(10), "yolo", "C2246", 20.5, 0.5, shape="auto") # 쌤 솔로 바닥
add(b(10), b(11), "wide", "C1870", 35.0, 0.5)              # 다 같이 바닥
half = BAR / 2; c0 = 11
clim = [("yolo", "C2128", 9.0, 0.5), ("yolo", "C2051", 30.0, 0.5), ("wide", "C2037", 21.0, 0.42), ("wide", "C2224", 36.0, 0.55),
        ("yolo", "C2059", 27.0, 0.5), ("yolo", "C2127", 43.0, 0.55), ("wide", "C2230", 28.5, 0.45), ("wide", "C1870", 39.5, 0.5)]
for j, (m, src, ss, cx) in enumerate(clim):
    add(round(G0 + c0 * BAR + j * half, 4), round(G0 + c0 * BAR + (j + 1) * half, 4), m, src, ss, cx)
add(b(15), b(17), "wide", "C2230", 0.0, 0.5)               # 엔딩 배경: 핑크 RAW 앞 두 사람
json.dump({"fps": [24000, 1001], "bar": BAR, "g0": G0, "end": b(17), "music_ss": 6.5, "segments": S},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json"), "w"), ensure_ascii=False, indent=1)
print(len(S), "컷, 끝", b(17))
