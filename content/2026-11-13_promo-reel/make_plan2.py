#!/usr/bin/env python3
# 광고 릴스 2차: 장르 퍼레이드 + 버스킹, 음원 2버전 → plan_v1.json, plan_v2.json, cues_v1.json, cues_v2.json
# v1 Modern World (115 BPM, 음악 6.5초부터 → 영상 2.382초 첫 큰 킥) / v2 TRINDADE (129.2 BPM, 음악 1.138초부터 → 2.382초, 33.2초 브레이크다운, 48.1초 드롭)
import json, os
D = os.path.dirname(os.path.abspath(__file__)); G0 = 2.382

# 장면 재료 (mode, src, ss, cx, extra)
HOOK = ("full", "C2128.MP4", 1.118, 0.5, {})
BURST = ("yolo", "C2128.MP4", 3.5, 0.49, {})
G = {  # 장르 컷: 라벨, 재료
 "MINKYUNG": ("T. MINKYUNG — GIRLS HIPHOP", ("yolo", "C2224.MP4", 7.4, 0.5, {})),
 "YELLS": ("T. YELLS — PRO CLASS", ("yolo", "YELLS.mp4", 9.0, 0.5, {})),
 "NOFF": ("T. NOFF — HIP HOP", ("yolo", "NOFF.mp4", 35.0, 0.5, {})),
 "HEEONE": ("T. HEEONE — HEELSCHOREO", ("yolo", "HEEONE.mp4", 11.0, 0.55, {"shape": "auto"})),
 "ARIN": ("T. ARIN — GIRLISH", ("wide", "ARIN.mp4", 15.6, 0.5, {})),
 "YUNI": ("T. YUNI — K-POP", ("yolo", "YUNI.mp4", 69.0, 0.65, {})),
 "HWANU": ("T. HWAN.U — CHOREOGRAPHY", ("yolo", "HWANU.mp4", 63.0, 0.5, {})),
 "RAEKU": ("T. RAEKU — CHOREOGRAPHY", ("yolo", "C2127.MP4", 12.0, 0.5, {})),
 "GAON": ("T. GAON — BASIC", ("vert", "GAONV.mp4", 8.5, 0.5, {})),
 "KIRY": ("T. KIRY — JAZZ", ("yolo", "C2246.MP4", 20.5, 0.5, {"shape": "auto"})),
 "POPUP": ("POP-UP CLASS", ("yolo", "C2037.MP4", 0.6, 0.62, {"pick_t": 1.0})),
 "GAON2": ("T. GAON — BASIC", ("yolo", "C2051.MP4", 23.6, 0.45, {})),
 "HWANU2": ("T. HWAN.U — CHOREOGRAPHY", ("yolo", "C2059.MP4", 11.5, 0.5, {})),
 "YUNI2": ("T. YUNI — K-POP", ("wide", "C2230.MP4", 3.5, 0.5, {})),
 "MINKYUNG2": ("T. MINKYUNG — GIRLS HIPHOP", ("wide", "C1870.MP4", 8.0, 0.5, {})),
}
BEH = {
 "practice": ("wide", "C2167.MP4", 0.0, 0.5, {}), "practice2": ("wide", "C2164.MP4", 1.0, 0.55, {}),
 "feedback": ("tall", "C2259.MP4", 0.5, 0.5, {}), "order": ("wide", "C2175.MP4", 0.0, 0.45, {}),
 "yuni1": ("wide", "C2162.MP4", 2.0, 0.55, {}), "yuni2": ("yolo", "C2204.MP4", 3.0, 0.8, {"pick_t": 1.0}),
 "busk1": ("full", "BUSK.mp4", 7.0, 0.5, {}), "busk2": ("wide", "BUSK.mp4", 173.5, 0.42, {}),
}
CLIMAX = [("wide", "YELLS.mp4", 29.5, 0.5, {}), ("yolo", "NOFF.mp4", 40.0, 0.5, {}), ("yolo", "C2128.MP4", 9.0, 0.5, {}),
          ("wide", "BUSK.mp4", 176.0, 0.42, {}), ("wide", "YUNI.mp4", 119.5, 0.5, {}), ("yolo", "HWANU.mp4", 67.5, 0.5, {}),
          ("wide", "C1870.MP4", 20.0, 0.5, {}), ("yolo", "HEEONE.mp4", 39.5, 0.5, {"shape": "auto"})]
ENDING = ("full", "C2128.MP4", 0.0, 0.5, {})   # 첫 장면처럼 RAW 간판 앞 한 줄 (천천히)

T = {  # 자막 (검수 반영 2026-11-13)
 "hook": {"type": "ed", "tag": "01 — PRO CLASS", "h": "어디서 배우느냐가\n[실력]이 된다"},
 "raw": {"type": "big", "word": "RAW", "sub": "로우댄스학원 수원점"},
 "teach": {"type": "ed", "tag": "02 — TEACHERS", "h": "강사진 전원\n[현역 댄서]"},
 "pro": {"type": "ed", "tag": "03 — PRO CLASS", "h": "전문반이면\n[모든 수업 무제한]"},
 "area": {"type": "big", "en": "STUDIO", "word": "100평", "sub": "4층 · 홀 3개 · 2026 오픈"},
 "open": {"type": "big", "en": "PRACTICE ROOM", "word": "항시 개방", "sub": "연습실"},
 "equip": {"type": "big", "en": "EQUIPMENT", "word": "최신 장비", "sub": "촬영 장비 · LED 조명"},
 "all": {"type": "big", "en": "FREE PASS", "word": "전부", "sub": "전문반은 전 클래스 프리패스"},
 "behind": {"type": "ed", "tag": "07 — BEHIND", "h": "수업이 끝나도\n[연습]은 계속"},
 "fb": {"type": "ed", "tag": "08 — FEEDBACK", "h": "쌤 피드백은\n[바로바로]"},
 "yuni1": {"type": "ed", "tag": "09 — T. YUNI", "h": "[대형 기획사 연습생 출신]\n쌤의 오디션 전문반"},
 "yuni2": {"type": "ed", "tag": "10 — T. YUNI", "h": "오디션 · 예고 · 예대\n[쌤 제자 다수 합격]"},
 "stage": {"type": "big", "en": "STAGE", "word": "무대", "sub": "월말평가 · 버스킹 · 콘서트"},
 "close": {"type": "big", "pre": "배울 거면", "word": "제대로"},
 "end": {"type": "ed", "end": True, "tag": "RAW DANCE SUWON", "h": "로우댄스학원 수원점\n[전문반]",
         "info": ["**중·고등** · 예고·예대 입시 · 기획사 준비", "상담 인스타 DM @rawdance_suwon", "카톡 '로우댄스수원점학원' · 수원 팔달구 매산로 136, 4층"],
         "tiny": "교습비는 캡션 참고 · 학원 등록번호 제8189호"},
}
BUSK_LBL = "RAW 파주운정점 버스킹 · 수원점 전문반 게스트"

def build(name, bar, music_ss, order):
    """order: [(bars, 재료, 자막키 or None, 라벨 or None)] — 첫 항목은 훅(0~G0)"""
    S, C, t = [], [], 0.0
    def seg(t0, t1, m, lbl=None, key=None, **over):
        mode, src, ss, cx, ex = m; d = dict(t0=round(t0, 4), t1=round(t1, 4), mode=mode, src=src, ss=ss, cx=cx, **ex); d.update(over); S.append(d)
        if key: c = dict(T[key]); c["a"] = round(t0 + 0.05, 3); c["b"] = round(t1 - 0.04, 3); C.append(c)
        if lbl: C.append({"type": "lbl", "a": round(t0, 3), "b": round(t1 - 0.02, 3), "text": lbl})
    seg(0, G0, HOOK, None, "hook"); t = G0
    for bars, m, key, lbl, *rest in order:
        over = rest[0] if rest else {}
        seg(t, t + bars * bar, m, lbl, key, **over); t += bars * bar
    end = t
    for c in C:
        if c.get("end"): c["b"] = round(end + 0.05, 3)
    json.dump({"fps": [24000, 1001], "bar": bar, "g0": G0, "end": round(end, 4), "music_ss": music_ss, "segments": S},
              open(os.path.join(D, f"plan_{name}.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(C, open(os.path.join(D, f"cues_{name}.json"), "w"), ensure_ascii=False, indent=1)
    print(name, len(S), "컷, 본편", round(end, 2), "초 + 로고 2.5초 =", round(end + 2.5, 1))

def g(k): return G[k][1], G[k][0]
def climax(n_half, bar, keys_last2=True):
    out = []
    for j in range(n_half):
        m = CLIMAX[j % len(CLIMAX)]
        out.append((0.5, m, "close" if j == n_half - 2 else None, None))
    return out

# v1 Modern World: 17마디 그루브 → 1마디 쉼 → 4마디 클라이맥스 → 2마디 엔딩
B1 = 4 * 60 / 114.84375
o1 = [(1, BURST, "raw", None), (1, G["MINKYUNG"][1], "teach", G["MINKYUNG"][0]),
      (1, G["YELLS"][1], "pro", G["YELLS"][0]), (1, G["NOFF"][1], "area", G["NOFF"][0]), (1, G["HEEONE"][1], None, G["HEEONE"][0]),
      (1, G["ARIN"][1], "open", G["ARIN"][0]), (1, G["YUNI"][1], None, G["YUNI"][0]), (1, G["HWANU"][1], "equip", G["HWANU"][0]),
      (1, G["RAEKU"][1], None, G["RAEKU"][0]), (1, G["GAON"][1], "all", G["GAON"][0]), (1, G["KIRY"][1], None, G["KIRY"][0]),
      (1, G["POPUP"][1], None, G["POPUP"][0]),
      (1, BEH["practice"], "behind", None), (1, BEH["feedback"], "fb", None), (1, BEH["yuni1"], "yuni1", None), (1, BEH["yuni2"], "yuni2", None),
      (1, BEH["busk1"], "stage", BUSK_LBL), (1, BEH["order"], None, None)] + climax(8, B1) + [(2, ENDING, "end", None, {"speed": 0.72})]
build("v1", B1, 6.5, o1)

# v2 TRINDADE: 16마디 비트 → 8마디 브레이크다운(비하인드) → 4마디 드롭 → 2마디 엔딩
B2 = 4 * 60 / 129.19921875
o2 = [(1, BURST, "raw", None), (1, G["MINKYUNG"][1], "teach", G["MINKYUNG"][0]),
      (1, G["YELLS"][1], "pro", G["YELLS"][0]), (1, G["NOFF"][1], "area", G["NOFF"][0]), (1, G["HEEONE"][1], None, G["HEEONE"][0]),
      (1, G["ARIN"][1], "open", G["ARIN"][0]), (1, G["YUNI"][1], None, G["YUNI"][0]), (1, G["HWANU"][1], "equip", G["HWANU"][0]),
      (1, G["RAEKU"][1], None, G["RAEKU"][0]), (1, G["GAON"][1], "all", G["GAON"][0]), (1, G["KIRY"][1], None, G["KIRY"][0]),
      (1, G["POPUP"][1], None, G["POPUP"][0]), (1, G["HWANU2"][1], None, G["HWANU2"][0]), (1, G["MINKYUNG2"][1], None, G["MINKYUNG2"][0]),
      (1, G["YUNI2"][1], None, G["YUNI2"][0]), (1, G["GAON2"][1], None, G["GAON2"][0]),
      (1, BEH["practice"], "behind", None), (1, BEH["practice2"], None, None), (1, BEH["feedback"], "fb", None), (1, BEH["order"], None, None),
      (1, BEH["yuni1"], "yuni1", None), (1, BEH["yuni2"], "yuni2", None), (1, BEH["busk1"], "stage", BUSK_LBL), (1, BEH["busk2"], None, BUSK_LBL)] \
     + climax(8, B2) + [(2, ENDING, "end", None, {"speed": 0.8})]
build("v2", B2, 1.138, o2)
