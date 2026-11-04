"""11월 A홀·B홀 프로그램표 v3 (v2 배치 + 브랜드 다크·보라 색, 1080x1350)."""
import subprocess
from pathlib import Path
from PIL import Image
from make_grid import A, B, CHROME

HERE = Path(__file__).parent
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&family=Montserrat:ital,wght@0,500;0,600;0,700;0,800;1,800&display=swap" rel="stylesheet">'
C = {"kpop": "#6d4fe0", "basic": "#4656c8", "pro": "#f5be46", "heel": "#9b45c4", "girlish": "#c0559f",
     "waack": "#3a78cc", "hiphop": "#54409e", "jazz": "#7e3aa8", "choreo": "#8577f0", "open": "#f5be46", "adult": "#b9a6ff"}
NAMES = {"kpop": "K-POP", "basic": "Basic", "pro": "PRO", "heel": "Heel Choreo", "girlish": "Girlish", "waack": "Waacking",
         "hiphop": "Hip Hop", "jazz": "Jazz", "choreo": "Choreo", "adult": "성인 K-POP"}
WD = ["MON", "TUE", "WED", "THU", "FRI"]; KR = {"MON": "월", "TUE": "화", "WED": "수", "THU": "목", "FRI": "금"}
T0, T1 = 16, 22
GX, GY, GW, GH = 128, 300, 1080 - 128 - 48, 790       # 격자 위치
PX = GH / (T1 - T0); CW = GW / 5

def blk(d, s, e, name, tm, sub, key):
    x = GX + WD.index(d) * CW + 5; y = GY + (s - T0) * PX + 3; w = CW - 10; h = (e - s) * PX - 6
    c = C[key]
    new = '<em>NEW</em>' if key == "adult" else ""
    return (f'<div class="b" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;'
            f'background:linear-gradient(180deg,{c}4d,{c}1f);border:1px solid {c}80;color:#f4f2ee">'
            f'{new}<b>{name.replace("<br>", " ")}</b><span>{tm.replace(" ~ ", "–")}</span><small>{sub}</small></div>')

def page(hall, blocks):
    wk = [b for b in blocks if b[0] != "SAT"]; sat = [b for b in blocks if b[0] == "SAT"]
    keys = []
    for b in wk + sat:
        k = "kpop" if b[6] == "open" else b[6]
        if k not in keys: keys.append(k)
    leg = "".join(f'<span><i style="background:{C[k]}"></i>{NAMES[k]}</span>' for k in keys)
    ruler = "".join(f'<div class="rl" style="top:{GY+(t-T0)*PX:.0f}px"><span>{t}:00</span></div>' for t in range(T0, T1 + 1))
    heads = "".join(f'<div class="dh" style="left:{GX+i*CW:.0f}px;width:{CW:.0f}px">{d}<small>{KR[d]}</small></div>' for i, d in enumerate(WD))
    satband = ""
    if sat:
        chips = "".join(f'<div class="sc"><b>{n}</b><span>{tm.replace(" ~ ", "–")}</span><em>모집중</em></div>' for _, _, _, n, tm, _, _ in sat)
        satband = f'<div class="sat"><div class="sl">SAT<small>토</small><i>REGINA</i></div>{chips}</div>'
    else:
        satband = '<div class="sat empty"><div class="sl">SAT<small>토</small></div><p>B홀 토요일 수업 없음</p></div>'
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">{FONTS}<style>
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1350px}}
body{{background:#0e0d12;color:#f4f2ee;font-family:Montserrat,"Noto Sans KR",sans-serif;position:relative;overflow:hidden}}
.top{{position:absolute;left:48px;right:48px;top:48px;display:flex;justify-content:space-between;align-items:flex-start}}
.top img{{height:36px}}
.g1{{position:absolute;width:1200px;height:1200px;border-radius:50%;right:-640px;top:-660px;background:radial-gradient(circle,rgba(124,92,255,.38),rgba(124,92,255,0) 62%)}}
.g2{{position:absolute;width:1100px;height:1100px;border-radius:50%;left:-580px;bottom:-660px;background:radial-gradient(circle,rgba(124,92,255,.24),rgba(124,92,255,0) 62%)}}
.top .r{{text-align:right;font-size:13px;font-weight:600;letter-spacing:.32em;line-height:1.8;color:#c3bfcc;margin-right:-.32em}}
.hero{{position:absolute;left:44px;top:96px;display:flex;align-items:flex-end;gap:22px}}
.hero .n{{font-weight:800;font-style:italic;font-size:170px;line-height:.82;letter-spacing:-.06em;color:transparent;-webkit-text-stroke:3px #b9a6ff}}
.hero .t{{padding-bottom:8px}}
.hero .t b{{display:block;font-weight:800;font-size:44px;letter-spacing:.02em;line-height:1}}
.hero .t span{{display:block;margin-top:8px;font-size:17px;font-weight:600;letter-spacing:.3em;color:#c3bfcc}}
.hall{{position:absolute;right:48px;top:118px;width:104px;height:104px;border-radius:50%;background:#b9a6ff;color:#0e0d12;display:flex;flex-direction:column;align-items:center;justify-content:center}}
.hall b{{font-size:52px;font-weight:800;line-height:1}}.hall span{{font-size:12px;font-weight:700;letter-spacing:.3em;margin-top:2px;margin-right:-.3em}}
.dh{{position:absolute;top:{GY-48}px;height:40px;display:flex;align-items:baseline;justify-content:center;gap:6px;font-size:19px;font-weight:800;letter-spacing:.1em}}
.dh small{{font-family:"Noto Sans KR";font-size:14px;font-weight:500;color:#8f8a9c;letter-spacing:0}}
.rl{{position:absolute;left:48px;right:48px;height:0;border-top:1px dashed #2f2c38}}
.rl span{{position:absolute;left:0;top:-10px;font-size:15px;font-weight:600;color:#8f8a9c;background:#0e0d12;padding-right:8px}}
.b{{position:absolute;border-radius:10px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:10px 14px;gap:2px;}}
.b b{{font-family:"Noto Sans KR",Montserrat;font-weight:900;font-size:19px;line-height:1.15}}
.b span{{font-size:14px;font-weight:700;color:#c9bfff}}
.b small{{font-size:12.5px;font-weight:700;letter-spacing:.08em;color:#c3bfcc}}
.b em{{font-style:normal;font-size:11px;font-weight:800;letter-spacing:.14em;background:#b9a6ff;color:#0e0d12;padding:2px 7px;border-radius:4px;margin-bottom:4px}}
.sat{{position:absolute;left:48px;right:48px;top:{GY+GH+28}px;height:118px;border-radius:16px;background:#17151e;border:1.5px solid #2f2c38;color:#f4f2ee;display:flex;align-items:center;gap:14px;padding:0 18px}}
.sl{{width:120px;flex:none;font-size:30px;font-weight:800;letter-spacing:.08em;color:#f4f2ee;display:flex;flex-direction:column}}
.sl small{{font-family:"Noto Sans KR";font-size:14px;font-weight:500;color:#8f8a9c;letter-spacing:0}}
.sl i{{font-style:normal;font-size:12px;font-weight:700;letter-spacing:.14em;color:#c3bfcc;margin-top:4px}}
.sc{{flex:1;height:82px;border-radius:12px;border:1.5px solid rgba(185,166,255,.35);background:rgba(109,79,224,.12);display:flex;flex-direction:column;justify-content:center;padding:0 14px;gap:2px;position:relative}}
.sc b{{font-family:"Noto Sans KR";font-weight:900;font-size:20px}}.sc span{{font-size:14px;font-weight:700;color:#b9a6ff}}
.sc em{{position:absolute;right:12px;top:12px;font-style:normal;font-family:"Noto Sans KR";font-size:12px;font-weight:700;color:#f5be46;background:rgba(245,190,70,.16);padding:2px 7px;border-radius:4px}}
.sat.empty p{{font-family:"Noto Sans KR";font-size:20px;color:#8f8a9c}}
.ft{{position:absolute;left:48px;right:48px;bottom:40px;display:flex;justify-content:space-between;align-items:center}}
.lg{{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px;font-weight:600;color:#c3bfcc;max-width:700px}}
.lg span{{display:flex;align-items:center;gap:6px}}.lg i{{display:block;width:11px;height:11px;border-radius:3px}}
.ct{{font-size:14px;font-weight:600;color:#8f8a9c;text-align:right;letter-spacing:.06em;line-height:1.6}}
</style></head><body><div class="g1"></div><div class="g2"></div>
<div class="top"><img src="raw-logo.png"><div class="r">SUWON<br>2026 NOVEMBER</div></div>
<div class="hero"><div class="n">11</div><div class="t"><b>NOVEMBER</b><span>PROGRAM TABLE · 2026</span></div></div>
<div class="hall"><b>{hall}</b><span>HALL</span></div>
{heads}{ruler}{"".join(blk(*b) for b in wk)}{satband}
<div class="ft"><div class="lg">{leg}</div><div class="ct">@rawdance_suwon<br>031-225-6600</div></div>
</body></html>"""

for hall, blocks in [("A", A), ("B", B)]:
    html = page(hall, blocks)
    name = f"hall-{hall.lower()}-2026-11-v3"
    (HERE / f"{name}.html").write_text(html, encoding="utf-8")
    tmp = HERE / f".{name}.render.html"; tmp.write_text(html.replace(FONTS, ""), encoding="utf-8")
    out = HERE / f"{name}.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1080,1600", f"--screenshot={out}", tmp.as_uri()],
                   check=True, capture_output=True)
    tmp.unlink()
    Image.open(out).convert("RGB").crop((0, 0, 1080, 1350)).save(out)
