"""12월 A홀·B홀 프로그램표 (11월 v3 배치 + 겨울·눈 콘셉트, 1080x1350)
원장님 2026-11-25: "12월 시간표, 겨울이고 눈 내리는 시즌에 맞게 / 힐코레오가 팝핑으로"
12월 변경: 월 19:40 HEELSCHOREO → POPPING (T. SUNGMI — 11/23 팝업 쌤, 원장님 확인 필요), 수 19:30~20:50 오디션반(YUNI, B홀) 복귀
원장님 2026-11-26: "릴스 비율로", "월요일 8:00~9:00 성인 케이팝 B홀" → 월 20:00~21:00 성인 K-POP(B홀, 쌤 확인 필요) 추가, 1080x1920 릴스판(-reels) 같이 만듦
사용: python3 make_dec.py  → hall-a-2026-12.png, hall-b-2026-12.png (node + playwright로 캡처)"""
import json, random, subprocess
from pathlib import Path

HERE = Path(__file__).parent
POP_T = "SUNGMI"
C = {"kpop": "#6f9bff", "basic": "#5cc4ff", "pro": "#ffd27a", "pop": "#7ff0ff", "girlish": "#ff9ed2",
     "waack": "#4fd8c8", "hiphop": "#9a8cff", "jazz": "#c29bff", "choreo": "#a9d8ff", "open": "#ffd27a", "aud": "#ffb38a", "kpro": "#ff6b7a"}
NAMES = {"kpop": "K-POP", "basic": "Basic", "pro": "PRO", "pop": "Popping", "girlish": "Girlish", "waack": "Waacking",
         "hiphop": "Hip Hop", "jazz": "Jazz", "choreo": "Choreo", "aud": "Audition", "kpro": "Kids Pro"}
WD = ["MON", "TUE", "WED", "THU", "FRI"]; KR = {"MON": "월", "TUE": "화", "WED": "수", "THU": "목", "FRI": "금"}
A = []
for d, t in [("MON", "YUNI"), ("TUE", "MINKYUNG"), ("WED", "YUNI"), ("THU", "MINKYUNG")]:
    A += [(d, 16, 17, "유아 K-POP", "16:00–17:00", t, "kpop"), (d, 17, 18, "키즈 K-POP", "17:00–18:00", t, "kpop")]
A += [("TUE", 18.5, 19 + 40 / 60, "BASIC", "18:30–19:40", "GAON", "basic"), ("THU", 18.5, 19 + 40 / 60, "BASIC", "18:30–19:40", "GAON", "basic"),
      ("FRI", 18.5, 20, "PRO", "18:30–20:00", "YELLS", "pro"),
      ("MON", 19 + 40 / 60, 20 + 50 / 60, "POPPING", "19:40–20:50", POP_T, "pop"),
      ("TUE", 19 + 40 / 60, 20 + 50 / 60, "GIRLISH", "19:40–20:50", "ARIN", "girlish"),
      ("WED", 19 + 40 / 60, 20 + 50 / 60, "WAACKING", "19:40–20:50", "J", "waack"),
      ("THU", 19 + 40 / 60, 20 + 50 / 60, "HIP HOP", "19:40–20:50", "NOFF", "hiphop"),
      ("FRI", 20 + 10 / 60, 21 + 20 / 60, "GIRLS HIPHOP", "20:10–21:20", "MINKYUNG", "girlish"),
      ("MON", 20 + 50 / 60, 22, "CHOREO", "20:50–22:00", "RAEKU", "choreo"),
      ("WED", 20 + 50 / 60, 22, "JAZZ", "20:50–22:00", "KIRY", "jazz"),
      ("THU", 20 + 50 / 60, 22, "CHOREO", "20:50–22:00", "HWAN.U", "choreo")]
SAT_A = [("유아 K-POP", "13:00–14:00"), ("키즈 K-POP", "14:00–15:00"), ("취미 K-POP", "15:00–16:10")]
# 원장님 2026-11-26: 화 취미 K-POP → 키즈 전문반 시간(B홀), 목 취미 K-POP 유지, 목 18:00~19:00 키즈 전문반은 C홀 → C홀은 따로 표 없이 B홀 표 아래 띠로
# 원장님 2026-11-28: 키즈 전문반은 12월 말 시작 → 그때부터 화 취미 K-POP이 키즈 전문반으로 바뀌고 취미 K-POP(민경쌤 반)은 주 1회(목). 그 전까지는 화 취미 K-POP 그대로
# 원장님 2026-11-28 다시: "취미 K-POP은 월·수 / 목요일만" → 12월부터 화 취미 K-POP 없음 (키즈 전문반은 12월 말 시작)
B = [(d, 18, 19 + 10 / 60, "취미 K-POP", "18:00–19:10", t, "kpop") for d, t in [("MON", "YUNI"), ("WED", "YUNI"), ("THU", "MINKYUNG")]]
KPRO_T = "MINKYUNG"   # 키즈 전문반 쌤 (원장님 2026-11-28)
KIDZ_START = False   # 키즈 전문반 시작하면 True → 화 B홀 키즈 전문반 + C홀 띠(목)
if KIDZ_START:
    B = [b for b in B if not (b[0] == "TUE" and b[3] == "취미 K-POP")] + [("TUE", 18, 19, "키즈 전문반", "18:00–19:00", KPRO_T, "kpro", "모집중")]
C_HALL = [("THU", "목", "키즈 전문반", "18:00–19:00", KPRO_T)]
B += [("WED", 19.5, 20 + 50 / 60, "오디션반", "19:30–20:50", "YUNI", "aud")]
ADULT_T = "YUNI"   # 월 성인 K-POP 쌤 (원장님 2026-11-28)
B += [("MON", 20, 21, "성인 K-POP", "20:00–21:00", ADULT_T, "kpop")]

T0, T1 = 16, 22
GX, GW = 128, 1080 - 128 - 48; CW = GW / 5
# 판형: feed 1080x1350 / reels 1080x1920 (위 220·아래 260은 인스타 화면 글자에 가려서 비움)
FMT = {"feed": dict(H=1350, OY=0, GY=300, GH=790, FB=40), "reels": dict(H=1920, OY=190, GY=540, GH=900, FB=250)}
def use(f):
    global H, OY, GY, GH, FB, PX
    H, OY, GY, GH, FB = (FMT[f][k] for k in ("H", "OY", "GY", "GH", "FB")); PX = GH / (T1 - T0)
use("feed")
FLAKE = '<svg viewBox="-50 -50 100 100"><g stroke="currentColor" stroke-width="5" stroke-linecap="round" fill="none">' + "".join(
    f'<g transform="rotate({a})"><line x1="0" y1="0" x2="0" y2="-44"/><line x1="0" y1="-26" x2="-11" y2="-36"/><line x1="0" y1="-26" x2="11" y2="-36"/><line x1="0" y1="-12" x2="-8" y2="-19"/><line x1="0" y1="-12" x2="8" y2="-19"/></g>'
    for a in range(0, 360, 60)) + '</g></svg>'

def blk(d, s, e, name, tm, sub, key, badge=None):
    x = GX + WD.index(d) * CW + 5; y = GY + (s - T0) * PX + 3; w = CW - 10; h = (e - s) * PX - 6; c = C[key]
    small = ' style="font-size:16px"' if len(name) > 10 else ""
    return (f'<div class="b" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;--c:{c}">'
            f'<b{small}>{name}</b><span>{tm}</span><small>{sub}</small>' + (f'<em class="bd">{badge}</em>' if badge else '') + '</div>')

def snow(seed, n=150):
    random.seed(seed); out = []
    for _ in range(n):
        x, y, r = random.uniform(0, 1080), random.uniform(0, H), random.choice([1.2, 1.6, 2, 2.4, 3, 3.6])
        o = random.uniform(.25, .85) * (0.55 if GY < y < GY + GH + 150 and 110 < x < 1040 else 1)   # 표 위는 옅게
        out.append(f'<i style="left:{x:.0f}px;top:{y:.0f}px;width:{r*2:.1f}px;height:{r*2:.1f}px;opacity:{o:.2f};filter:blur({0 if r<2.4 else .6}px)"></i>')
    return "".join(out)

def flakes(seed):
    random.seed(seed + 7); spots = [(470, 64 + OY, 34, .45), (560, 196 + OY, 24, .5), (780, 120 + OY, 40, .35), (1040, GY + 420, 34, .22), (6, GY + 260, 30, .22)]
    return "".join(f'<div class="fk" style="left:{x}px;top:{y}px;width:{s}px;height:{s}px;opacity:{o};transform:rotate({random.randint(0,30)}deg)">{FLAKE}</div>' for x, y, s, o in spots)

def page(hall, blocks, sat):
    keys = []
    for b in blocks:
        if b[6] not in keys: keys.append(b[6])
    if sat and "kpop" not in keys: keys.insert(0, "kpop")
    if not sat and KIDZ_START and "kpro" not in keys: keys.append("kpro")
    leg = "".join(f'<span><i style="background:{C[k]}"></i>{NAMES[k]}</span>' for k in keys)
    ruler = "".join(f'<div class="rl" style="top:{GY+(t-T0)*PX:.0f}px"><span>{t}:00</span></div>' for t in range(T0, T1 + 1))
    heads = "".join(f'<div class="dh" style="left:{GX+i*CW:.0f}px;width:{CW:.0f}px">{d}<small>{KR[d]}</small></div>' for i, d in enumerate(WD))
    if sat:
        chips = "".join(f'<div class="sc"><b>{n}</b><span>{tm}</span><em>모집중</em></div>' for n, tm in sat)
        satband = f'<div class="sat"><div class="sl">SAT<small>토</small><i>REGINA</i></div>{chips}</div>'
    else:   # B홀 표: 토요일 수업이 없어서 그 자리에 C홀(키즈 전문반) 띠
        if KIDZ_START:
            cc = "".join(f'<div class="sc kp"><b>{n}</b><span>{d} {kr} · {tm}</span><em>모집중</em></div>' for d, kr, n, tm, t in C_HALL)
            satband = f'<div class="sat"><div class="sl" style="width:150px;white-space:nowrap">C HALL<small>C홀</small></div>{cc}<p class="cn">RAW KIDZ 1기 · 10~13세<br>화요일은 B홀, 목요일은 C홀</p></div>'
        else:   # 시작 전: 토요일 B홀은 비어 있으니 그 자리에 모집 안내
            satband = '<div class="sat"><div class="sl" style="width:185px;white-space:nowrap">KIDS PRO<small>키즈 전문반</small></div><div class="sc kp"><b>RAW KIDZ 1기</b><span>12월 말 개강 예정 · 10~13세</span><em>모집중</em></div><p class="cn">상담 DM · 카톡 \'로우댄스수원점학원\'<br>B홀 토요일 수업 없음</p></div>'
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:{H}px}}
body{{background:linear-gradient(180deg,#0b1530 0%,#0a1124 45%,#0c1022 100%);color:#f3f7ff;font-family:Montserrat,"Noto Sans KR",sans-serif;position:relative;overflow:hidden}}
.g1{{position:absolute;width:1300px;height:1300px;border-radius:50%;right:-700px;top:-720px;background:radial-gradient(circle,rgba(120,180,255,.42),rgba(120,180,255,0) 62%)}}
.g2{{position:absolute;width:1100px;height:1100px;border-radius:50%;left:-600px;bottom:-640px;background:radial-gradient(circle,rgba(150,130,255,.26),rgba(150,130,255,0) 62%)}}
.sn{{position:absolute;inset:0;pointer-events:none}}.sn i{{position:absolute;border-radius:50%;background:#fff;box-shadow:0 0 6px rgba(255,255,255,.7)}}
.fk{{position:absolute;color:#dff0ff}}.fk svg{{width:100%;height:100%;filter:drop-shadow(0 0 6px rgba(190,225,255,.7))}}
.drift{{position:absolute;left:-40px;right:-40px;bottom:-60px;height:150px;border-radius:50% 50% 0 0/100% 100% 0 0;background:radial-gradient(ellipse at 50% 0%,rgba(230,242,255,.16),rgba(230,242,255,0) 70%)}}
.top{{position:absolute;left:48px;right:48px;top:{48+OY}px;display:flex;justify-content:space-between;align-items:flex-start}}
.top img{{height:36px}}
.top .r{{text-align:right;font-size:13px;font-weight:600;letter-spacing:.32em;line-height:1.8;color:#b9cbe8;margin-right:-.32em}}
.hero{{position:absolute;left:44px;top:{96+OY}px;display:flex;align-items:flex-end;gap:22px}}
.hero .n{{position:relative;font-weight:800;font-style:italic;font-size:170px;line-height:.82;letter-spacing:-.06em;color:transparent;-webkit-text-stroke:3px #cfe6ff;text-shadow:0 0 28px rgba(160,210,255,.45)}}
.cap{{position:absolute;left:30px;top:-9px;width:150px;height:20px;background:radial-gradient(ellipse at 50% 100%,#fff 0 40%,rgba(255,255,255,0) 70%);border-radius:50%;opacity:.8}}
.hero .t{{padding-bottom:8px}}
.hero .t b{{display:block;font-weight:800;font-size:44px;letter-spacing:.02em;line-height:1}}
.hero .t span{{display:block;margin-top:8px;font-size:17px;font-weight:600;letter-spacing:.3em;color:#b9cbe8}}
.hero .t em{{display:inline-block;margin-top:10px;font-style:normal;font-size:13px;font-weight:700;letter-spacing:.28em;color:#0b1530;background:#dff0ff;padding:4px 10px;border-radius:20px}}
.hall{{position:absolute;right:48px;top:{118+OY}px;width:104px;height:104px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffffff,#cfe6ff 70%);color:#0b1530;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 0 30px rgba(180,220,255,.45)}}
.hall b{{font-size:52px;font-weight:800;line-height:1}}.hall span{{font-size:12px;font-weight:700;letter-spacing:.3em;margin-top:2px;margin-right:-.3em}}
.dh{{position:absolute;top:{GY-48}px;height:40px;display:flex;align-items:baseline;justify-content:center;gap:6px;font-size:19px;font-weight:800;letter-spacing:.1em}}
.dh small{{font-family:"Noto Sans KR";font-size:14px;font-weight:500;color:#8ea0bf;letter-spacing:0}}
.rl{{position:absolute;left:48px;right:48px;height:0;border-top:1px dashed #253252}}
.rl span{{position:absolute;left:0;top:-10px;font-size:15px;font-weight:600;color:#8ea0bf;background:#0a1226;padding-right:8px}}
.b{{position:absolute;border-radius:12px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:10px 14px;gap:2px;
  background:linear-gradient(160deg,color-mix(in srgb,var(--c) 34%,transparent),color-mix(in srgb,var(--c) 12%,transparent) 70%);
  border:1px solid color-mix(in srgb,var(--c) 60%,transparent);box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 8px 24px rgba(0,0,0,.25);overflow:hidden}}
.b:before{{content:"";position:absolute;left:-10%;right:-10%;top:-2px;height:8px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.75),transparent);filter:blur(2px);border-radius:50%;opacity:.55}}
.b b{{font-family:"Noto Sans KR",Montserrat;font-weight:900;font-size:19px;line-height:1.15}}
.b span{{font-size:14px;font-weight:700;color:color-mix(in srgb,var(--c) 70%,#fff)}}
.b small{{font-size:12.5px;font-weight:700;letter-spacing:.08em;color:#c3d0e8}}
.sat{{position:absolute;left:48px;right:48px;top:{GY+GH+28}px;height:118px;border-radius:16px;background:rgba(20,32,62,.75);border:1.5px solid #2a3a62;display:flex;align-items:center;gap:14px;padding:0 18px}}
.sl{{width:120px;flex:none;font-size:30px;font-weight:800;letter-spacing:.08em;display:flex;flex-direction:column}}
.sl small{{font-family:"Noto Sans KR";font-size:14px;font-weight:500;color:#8ea0bf;letter-spacing:0}}
.sl i{{font-style:normal;font-size:12px;font-weight:700;letter-spacing:.14em;color:#b9cbe8;margin-top:4px}}
.sc{{flex:1;height:82px;border-radius:12px;border:1.5px solid rgba(160,200,255,.35);background:rgba(111,155,255,.12);display:flex;flex-direction:column;justify-content:center;padding:0 14px;gap:2px;position:relative}}
.sc b{{font-family:"Noto Sans KR";font-weight:900;font-size:20px}}.sc span{{font-size:14px;font-weight:700;color:#a9c8ff}}
.sc em{{position:absolute;right:12px;top:12px;font-style:normal;font-family:"Noto Sans KR";font-size:12px;font-weight:700;color:#ffd27a;background:rgba(255,210,122,.16);padding:2px 7px;border-radius:4px}}
.sat.empty p{{font-family:"Noto Sans KR";font-size:20px;color:#8ea0bf}}
.sc.kp{{flex:0 0 330px;border-color:rgba(255,107,122,.55);background:rgba(255,107,122,.14)}}.sc.kp span{{color:#ffb3bb}}
.cn{{font-family:"Noto Sans KR";font-size:17px;font-weight:500;line-height:1.55;color:#b9cbe8;margin-left:10px}}
.bd{{position:absolute;right:10px;top:10px;font-style:normal;font-family:"Noto Sans KR";font-size:11px;font-weight:700;color:#ffd27a;background:rgba(255,210,122,.16);padding:2px 6px;border-radius:4px}}
.ft{{position:absolute;left:48px;right:48px;bottom:{FB}px;display:flex;justify-content:space-between;align-items:center}}
.lg{{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px;font-weight:600;color:#c3d0e8;max-width:700px}}
.lg span{{display:flex;align-items:center;gap:6px}}.lg i{{display:block;width:11px;height:11px;border-radius:3px}}
.ct{{font-size:14px;font-weight:600;color:#8ea0bf;text-align:right;letter-spacing:.06em;line-height:1.6}}
</style></head><body><div class="g1"></div><div class="g2"></div><div class="drift"></div>
<div class="sn">{snow(1 if hall=='A' else 2)}</div>{flakes(1 if hall=='A' else 2)}
<div class="top"><img src="raw-logo.png"><div class="r">SUWON<br>2026 DECEMBER</div></div>
<div class="hero"><div class="n"><div class="cap"></div>12</div><div class="t"><b>DECEMBER</b><span>PROGRAM TABLE · 2026</span><em>❄ WINTER SEASON</em></div></div>
<div class="hall"><b>{hall}</b><span>HALL</span></div>
{heads}{ruler}{"".join(blk(*b) for b in blocks)}{satband}
<div class="ft"><div class="lg">{leg}</div><div class="ct">@rawdance_suwon<br>031-225-6600</div></div>
</body></html>"""

files = []
for f in ("feed", "reels"):
    use(f)
    for hall, blocks, sat in [("A", A, SAT_A), ("B", B, [])]:
        name = f"hall-{hall.lower()}-2026-12" + ("-reels" if f == "reels" else "")
        (HERE / f"{name}.html").write_text(page(hall, blocks, sat), encoding="utf-8"); files.append((name, H))
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [n,h] of %s){const p=await b.newPage({viewport:{width:1080,height:h}});await p.goto('file://'+%s+'/'+n+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);await p.screenshot({path:%s+'/'+n+'.png'});await p.close();}await b.close();})();""" % (
    json.dumps(files), json.dumps(str(HERE)), json.dumps(str(HERE)))
subprocess.run(["node", "-e", js], check=True)
files = [n for n, _ in files]
print("\n".join(str(HERE / f"{n}.png") for n in files))
