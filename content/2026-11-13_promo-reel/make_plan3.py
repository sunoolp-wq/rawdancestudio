#!/usr/bin/env python3
# 광고 릴스 3차 (원장님 피드백 2026-11-13): 음원마다 완전히 다른 구성, REC 표시 없음, RAEKU 1번만, 남학생 2명 컷 제외
#  A (Modern World 115BPM, 음악 6.5초부터): "무대 → 연습실" 거꾸로 — 버스킹 무대에서 시작해서 학원으로
#  B (TRINDADE 129.2BPM, 음악 1.138초부터): "수업 → 연습 → 무대" — 장르 이름을 큰 글자로, 브레이크다운에 연습, 드롭에 무대
import json, os
D = os.path.dirname(os.path.abspath(__file__)); G0 = 2.382
def M(mode, src, ss, cx=0.5, **ex): return (mode, src, ss, cx, ex)

# 재료 (남학생 2명이 나오는 HWANU 솔로 63~78초·YUNI 69초 구간은 쓰지 않음)
YELLS = M("yolo", "YELLS.mp4", 9.0); YELLS_W = M("wide", "YELLS.mp4", 43.0); YELLS_W2 = M("wide", "YELLS.mp4", 29.5)
NOFF = M("yolo", "NOFF.mp4", 35.0); NOFF_G = M("wide", "NOFF.mp4", 59.0)
HEEONE = M("yolo", "HEEONE.mp4", 11.0, 0.55, shape="auto"); HEEONE_LIE = M("wide", "HEEONE.mp4", 3.6, 0.5); HEEONE2 = M("yolo", "HEEONE.mp4", 39.5, shape="auto")
ARIN = M("wide", "ARIN.mp4", 15.6); YUNI = M("wide", "C2230.MP4", 3.5); YUNI_T = M("wide", "YUNI.mp4", 99.5, 0.5); YUNI_K = M("wide", "C1912.MP4", 5.0)
HWANU = M("yolo", "C2059.MP4", 11.5); HWANU_G = M("wide", "HWANU.mp4", 19.0); RAEKU = M("yolo", "C2127.MP4", 12.0)
GAON = M("vert", "GAONV.mp4", 8.5); GAON2 = M("yolo", "C2051.MP4", 23.6, 0.45); KIRY = M("yolo", "C2246.MP4", 20.5, shape="auto")
MINK = M("yolo", "C2224.MP4", 7.4); MINK_G = M("wide", "C1870.MP4", 8.0); MINK_F = M("wide", "C1870.MP4", 35.0); MINK_G2 = M("wide", "C2224.MP4", 35.5, 0.55)
POPUP = M("yolo", "C2037.MP4", 0.6, 0.62, pick_t=1.0)
PRAC = M("wide", "C2167.MP4", 0.0); PRAC2 = M("wide", "C2164.MP4", 1.0, 0.55); PRAC3 = M("wide", "C2162.MP4", 2.0, 0.55)
FB = M("tall", "C2259.MP4", 0.5); SMILE = M("yolo", "C2204.MP4", 3.0, 0.8, pick_t=1.0)
BUSK_STILL = M("full", "BUSK.mp4", 4.118); BUSK_GO = M("wide", "BUSK.mp4", 6.5, 0.5); BUSK_GO2 = M("wide", "BUSK.mp4", 12.0, 0.5)
BUSK_A = M("wide", "BUSK.mp4", 30.0, 0.5); BUSK_B = M("wide", "BUSK.mp4", 60.0, 0.5); BUSK_C = M("wide", "BUSK.mp4", 100.0, 0.45)
BUSK_D = M("wide", "BUSK.mp4", 173.5, 0.42); BUSK_E = M("wide", "BUSK.mp4", 176.0, 0.42); BUSK_PRE = M("full", "BUSK.mp4", 1.0)
BL = "RAW 파주운정점 버스킹 · 수원점 전문반 게스트"
END = {"type": "ed", "end": True, "tag": "RAW DANCE SUWON", "h": "로우댄스학원 수원점\n[전문반]",
       "info": ["**중·고등** · 예고·예대 입시 · 기획사 준비", "상담 인스타 DM @rawdance_suwon", "카톡 '로우댄스수원점학원' · 수원 팔달구 매산로 136, 4층"],
       "tiny": "교습비는 캡션 참고 · 학원 등록번호 제8189호"}
def ed(tag, h): return {"type": "ed", "tag": tag, "h": h}
def big(word, sub="", en="", pre=""): return {"type": "big", "word": word, "sub": sub, "en": en, "pre": pre}

def build(name, bar, music_ss, hook, items):
    """hook: (재료, 자막, 라벨). items: (길이(마디), 재료, 자막 or None, 라벨 or None, 덮어쓰기 dict)"""
    S, C = [], []
    def add(t0, t1, m, cue, lbl, over):
        mode, src, ss, cx, ex = m; d = dict(t0=round(t0, 4), t1=round(t1, 4), mode=mode, src=src, ss=ss, cx=cx, **ex); d.update(over or {}); S.append(d)
    t = 0.0; add(0, G0, hook[0], None, None, None)
    if hook[1]: c = dict(hook[1]); c.update(a=0.12, b=round(G0 - 0.06, 3)); C.append(c)
    if hook[2]: C.append({"type": "lbl", "a": 0.0, "b": round(G0 - 0.02, 3), "text": hook[2]})
    t = G0; spans = []   # 자막은 여러 컷에 걸칠 수 있음: ("cue", 시작, 끝)
    for it in items:
        bars, m, cue, lbl, over = (list(it) + [None] * 5)[:5]
        t1 = t + bars * bar; add(t, t1, m, cue, lbl, over)
        if cue == "+":   # 앞 자막을 이 컷까지 늘림
            C[spans[-1]]["b"] = round(t1 - 0.04, 3)
        elif cue:
            c = dict(cue); c["a"] = round(t + 0.05, 3); c["b"] = round(t1 - 0.04, 3); C.append(c); spans.append(len(C) - 1)
        if lbl: C.append({"type": "lbl", "a": round(t, 3), "b": round(t1 - 0.02, 3), "text": lbl})
        t = t1
    for c in C:
        if c.get("end"): c["b"] = round(t + 0.05, 3)
    json.dump({"fps": [24000, 1001], "bar": bar, "g0": G0, "end": round(t, 4), "music_ss": music_ss, "segments": S},
              open(os.path.join(D, f"plan_{name}.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(C, open(os.path.join(D, f"cues_{name}.json"), "w"), ensure_ascii=False, indent=1)
    print(name, len(S), "컷, 본편", round(t, 2), "초 + 로고 2.5초 =", round(t + 2.5, 1))

# ── A: Modern World "무대 → 연습실" (55초) ── 17마디 그루브 → 1마디 쉼 → 4마디 클라이맥스 → 2마디 엔딩
BA = 4 * 60 / 114.84375; h = 0.5
A = [
 (1, BUSK_GO, big("RAW", "수원점 전문반"), BL),
 (h, BUSK_A, None, BL), (h, BUSK_B, None, BL),
 (1, PRAC, ed("02 — BEHIND THE STAGE", "그 무대 뒤에는\n[이 연습실]이 있다")),
 (1, NOFF_G, big("100평", "4층 · 홀 3개 · 2026 오픈", "STUDIO")),
 (1, PRAC2, big("항시 개방", "연습실", "PRACTICE ROOM")),
 (1, HEEONE2, big("최신 장비", "촬영 장비 · LED 조명", "EQUIPMENT"), "T. HEEONE — HEELSCHOREO"),
 (1, MINK, ed("03 — TEACHERS", "강사진 전원\n[현역 댄서]"), "T. MINKYUNG — GIRLS HIPHOP"),
 (h, YELLS, ed("04 — PRO CLASS", "전문반이면\n[모든 수업 무제한]"), "T. YELLS — PRO CLASS"),
 (h, NOFF, "+", "T. NOFF — HIP HOP"),
 (h, ARIN, None, "T. ARIN — GIRLISH"), (h, YUNI, None, "T. YUNI — K-POP"),
 (h, HWANU, None, "T. HWAN.U — CHOREOGRAPHY"), (h, RAEKU, None, "T. RAEKU — CHOREOGRAPHY"),
 (h, GAON, None, "T. GAON — BASIC"), (h, KIRY, None, "T. KIRY — JAZZ"),
 (h, HEEONE, None, "T. HEEONE — HEELSCHOREO"), (h, MINK_G, None, "T. MINKYUNG — GIRLS HIPHOP"),
 (1, POPUP, big("전부", "팝업 수업까지 프리패스", "FREE PASS"), "POP-UP CLASS"),
 (1, FB, ed("05 — FEEDBACK", "쌤 피드백은\n[바로바로]")),
 (1, PRAC3, ed("06 — T. YUNI", "[대형 기획사 연습생 출신]\n쌤의 오디션 전문반")),
 (1, YUNI_T, ed("07 — T. YUNI", "오디션 · 예고 · 예대\n[쌤 제자 다수 합격]"), "T. YUNI — K-POP"),
 (1, SMILE, ed("08 — BEHIND", "수업이 끝나도\n[연습]은 계속")),
 (1, HEEONE_LIE, None),                                        # 음악 쉼: 바닥에 누운 정지 장면
 (h, YELLS_W2, None), (h, BUSK_D, None, BL), (h, NOFF, None), (h, BUSK_E, None, BL),
 (h, MINK_G2, None), (h, GAON2, None), (h, BUSK_C, big("제대로", pre="배울 거면"), BL), (h, YELLS, "+"),
 (2, YELLS_W, END, None, {"speed": 0.72}),
]
build("A", BA, 6.5, (BUSK_STILL, ed("01 — STAGE", "이 무대에\n[서기까지]"), BL), A)

# ── B: TRINDADE "수업 → 연습 → 무대" (60초) ── 16마디 비트(수업) → 8마디 브레이크다운(연습) → 4마디 드롭(무대) → 2마디 엔딩
BB = 4 * 60 / 129.19921875
B = [
 (1, NOFF, big("RAW", "로우댄스학원 수원점")),
 (1, MINK, ed("02 — TEACHERS", "강사진 전원\n[현역 댄서]")),
 (1, YELLS, big("전문반", "T. YELLS · 모든 수업 무제한 프리패스", "PRO CLASS")),
 (1, NOFF_G, big("힙합", "T. NOFF", "HIP HOP")),
 (1, HEEONE, big("힐코레오", "T. HEEONE", "HEELSCHOREO")),
 (1, ARIN, big("걸리시", "T. ARIN", "GIRLISH")),
 (1, YUNI, big("케이팝", "T. YUNI", "K-POP")),
 (1, HWANU, big("코레오", "T. HWAN.U · T. RAEKU", "CHOREOGRAPHY")),
 (1, RAEKU, "+"),
 (1, GAON, big("베이직", "T. GAON", "BASIC")),
 (1, KIRY, big("재즈", "T. KIRY", "JAZZ")),
 (1, MINK_G, big("걸스힙합", "T. MINKYUNG", "GIRLS HIPHOP")),
 (1, POPUP, big("팝업", "팝업 수업까지 프리패스", "POP-UP CLASS")),
 (1, HWANU_G, big("전부", "전문반은 전 클래스 프리패스", "FREE PASS")),
 (h, YUNI_K, None), (h, GAON2, None),
 (1, MINK_G2, ed("03 — AFTER CLASS", "수업이 끝나면")),
 # 브레이크다운: 연습
 (1, PRAC, ed("04 — PRACTICE", "연습실\n[항시 개방]")),
 (1, PRAC2, ed("05 — STUDIO", "4층 [100평] · 홀 3개\n2026 오픈")),
 (1, FB, ed("06 — FEEDBACK", "쌤 피드백은\n[바로바로]")),
 (1, PRAC3, ed("07 — T. YUNI", "[대형 기획사 연습생 출신]\n쌤의 오디션 전문반")),
 (1, YUNI_T, ed("08 — T. YUNI", "오디션 · 예고 · 예대\n[쌤 제자 다수 합격]")),
 (1, SMILE, ed("09 — FILM", "[최신 촬영 장비]로\n찍는 수업 영상")),
 (1, M("wide", "C2246.MP4", 3.0), ed("10 — STAGE", "그리고\n[무대]")),
 (1, BUSK_PRE, None, BL),
 # 드롭: 무대
 (1, BUSK_GO2, big("무대", "월말평가 · 버스킹 · 콘서트", "STAGE"), BL),
 (h, BUSK_A, None, BL), (h, BUSK_B, None, BL), (h, BUSK_C, None, BL), (h, BUSK_D, None, BL),
 (h, BUSK_E, big("제대로", pre="배울 거면"), BL), (h, YELLS_W2, "+"),
 (2, YELLS_W, END, None, {"speed": 0.8}),
]
build("B", BB, 1.138, (HEEONE_LIE, ed("01 — CLASS · PRACTICE · STAGE", "수업 · 연습 · 무대\n[전부] 여기서"), "T. HEEONE — HEELSCHOREO"), B)
