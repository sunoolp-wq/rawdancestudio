#!/usr/bin/env python3
# 30초 버전 (원장님 2026-11-13): A30 Modern World 그대로 이어서 / B30 TRINDADE 는 음악을 마디 단위로 잘라 붙임(비트 → 브레이크다운 끝 2마디 → 드롭)
import os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(D, "make_plan3.py"), encoding="utf-8").read().split("# ── A:")[0])   # 재료·자막·build() 가져오기
h = 0.5

# ── A30: 무대 → 연습실 (약 29초) ──
BA = 4 * 60 / 114.84375
A30 = [
 (1, BUSK_GO, big("RAW", "수원점 전문반"), BL),
 (1, PRAC, ed("02 — BEHIND THE STAGE", "그 무대 뒤에는\n[이 연습실]이 있다")),
 (1, NOFF_3, big("110평", "홀 3개 · 2026 오픈", "STUDIO")),
 (1, MINK_D2, ed("03 — TEACHERS", "강사진 전원\n[현역 댄서]"), "T. MINKYUNG — GIRLS HIPHOP"),
 (h, YELLS_2, ed("04 — PRO CLASS", "전문반이면\n[모든 수업 무제한]"), "T. YELLS — PRO CLASS"),
 (h, NOFF_4, "+", "T. NOFF — HIP HOP"),
 (h, ARIN_3, None, "T. ARIN — GIRLISH"), (h, YUNI_K2, None, "T. YUNI — K-POP"),
 (h, HWANU_2, None, "T. HWAN.U — CHOREOGRAPHY"), (h, WAACK_A, None, "T. J — WAACKING"),
 (1, AUD_A1, ed("05 — T. YUNI", "[대형 기획사 연습생 출신]\n쌤의 오디션 전문반"), AL),
 (1, AUD_A2, ed("06 — T. YUNI", "오디션 · 예고 · 예대\n[쌤 제자 다수 합격]"), AL),
 (h, BUSK_C, big("제대로", pre="배울 거면"), BL), (h, YELLS_W2, "+"),
 (1.5, YELLS_W, END, None, {"speed": 0.72}),
]
build("A30", BA, 6.5, (BUSK_STILL, ed("01 — STAGE", "이 무대에\n[서기까지]"), BL), A30)

# ── B30: 수업(장르 몰아치기) → 연습(YUNI) → 무대 (약 30초) ──
BB = 4 * 60 / 129.19921875
def g(word, en, sub=""): return big(word, sub, en)
AUD_C = M("wide", "AUD.mp4", 7.0)   # 오디션반 카드용: 쌤·학생 같이 추는 구간 (설명 컷 15초·37초와 안 겹치게)
B30 = [   # 원장님 2026-11-13 (2차): 케이팝 → 베이직 → 장르들 → 전문반 → 오디션반 → 오디션반 설명 → 무대 / "걸리쉬" 표기 / 15초 음악 이음새는 8마디 뒤
 (1, YUNI_K_D, big("RAW", "로우댄스학원 수원점")),
 (1, MINK_D, ed("02 — TEACHERS", "강사진 전원\n[현역 댄서]")),
 (h, YUNI, g("케이팝", "K-POP", "T. YUNI")), (h, GAON, g("힙합 베이직", "HIPHOP BASIC", "T. GAON")),
 (h, NOFF, g("힙합", "HIP HOP", "T. NOFF")), (h, HEEONE, g("힐코레오", "HEELSCHOREO", "T. HEEONE")),
 (h, ARIN, g("걸리쉬", "GIRLISH", "T. ARIN")), (h, HWANU_D, g("코레오", "CHOREOGRAPHY", "T. HWAN.U")),
 (h, KIRY, g("재즈", "JAZZ", "T. KIRY")), (h, WAACK_B, g("왁킹", "WAACKING", "T. J")),
 (h, MINK_G, g("걸스힙합", "GIRLS HIPHOP", "T. MINKYUNG")), (h, POPUP_D, g("팝업", "POP-UP CLASS")),
 (1, YELLS_D, g("전문반", "PRO CLASS", "T. YELLS · 전 클래스 프리패스")),
 # ← 음악: 8마디 끝나고 브레이크다운 끝 4마디 (원장님 2026-11-13: 전문반도 눈에 보이는 혜택 3가지 설명)
 (h, PRAC, ed("03 — PRO CLASS", "매달 [월말평가]\n연습실 [상시 개방]\n다양한 [공연 기회]")), (h, PRAC2, "+"), (h, BUSK_A, "+", BL),
 (h, AUD_C, g("오디션반", "AUDITION CLASS", "T. YUNI"), AL),
 (1, AUD_B1, ed("04 — T. YUNI", "[대형 기획사 연습생 출신]\n쌤의 오디션 전문반"), AL),
 (1, AUD_B2, ed("05 — T. YUNI", "오디션 · 예고 · 예대\n[쌤 제자 다수 합격]"), AL),
 (1, BUSK_GO2, big("무대", "월말평가 · 버스킹 · 콘서트", "STAGE"), BL),                      # ← 드롭
 (h, BUSK_E, big("제대로", pre="배울 거면"), BL), (h, MINK_G2, "+"),
 (1.5, YELLS_W, END, None, {"speed": 0.8}),
]
build("B30", BB, 0.0, (HEEONE_LIE, ed("01 — CLASS · PRACTICE · STAGE", "수업 · 연습 · 무대\n[전부] 여기서"), "T. HEEONE — HEELSCHOREO"), B30)

# B30 음악: [1.138 → 비트 8마디 끝] + [드롭 직전 4마디] + [드롭 48.10 →]  (마디 경계에서 이어 붙임, 10ms 페이드로 '딱' 소리 방지)
def music_b30(src, out):
    s1a, s1b = 1.138, 1.138 + 2.382 + 8 * BB   # 비트 8마디(한 프레이즈) 끝에서 넘어감
    s2a, s2b = 48.10 - 4 * BB, 48.10   # 브레이크다운 끝 4마디 (전문반·오디션반 설명)
    X = 0.12   # 첫 이음새는 짧게 겹쳐서(크로스페이드) 자연스럽게. 겹친 만큼 뒤 구간을 미리 가져와 박자 위치는 그대로
    fc = (f"[0:a]atrim={s1a}:{s1b + X / 2},asetpts=PTS-STARTPTS[a];"
          f"[0:a]atrim={s2a - X / 2}:{s2b},asetpts=PTS-STARTPTS,afade=t=out:st={s2b - s2a + X / 2 - 0.01}:d=0.01[b];"
          f"[a][b]acrossfade=d={X}:c1=tri:c2=tri[ab];"
          f"[0:a]atrim={s2b}:{s2b + 20},asetpts=PTS-STARTPTS,afade=t=in:d=0.01[c];[ab][c]concat=n=2:v=0:a=1[m]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[m]", out], check=True)
if __name__ == "__main__" and os.environ.get("MUSIC_SRC"):
    music_b30(os.environ["MUSIC_SRC"], os.environ["MUSIC_OUT"]); print("B30 음악:", os.environ["MUSIC_OUT"])
