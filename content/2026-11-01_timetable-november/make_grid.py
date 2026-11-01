"""11월 A홀·B홀 주간 프로그램표 (10월 격자형 레이아웃, 11월 가을 색, 1080x1920)."""
import subprocess
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&family=Montserrat:wght@500;600;700;800&display=swap" rel="stylesheet">'

# 장르 색 (11월: 와인·러스트·머스터드·올리브·브라운 계열)
C = {"kpop": "#b0476a", "basic": "#8a9a52", "pro": "#e0a93c", "heel": "#c8573c", "girlish": "#d27a78",
     "waack": "#4f9a8c", "hiphop": "#a8714a", "jazz": "#8e3a52", "choreo": "#e0823e", "open": "#e0a93c",
     "adult": "#f0c27a", "aud": "#b0476a"}
LEG = {"A": [("kpop","K-POP"),("basic","Basic"),("pro","PRO"),("heel","Heel Choreo"),("girlish","Girlish"),
             ("waack","Waacking"),("hiphop","Hip Hop"),("jazz","Jazz"),("choreo","Choreo"),("open","모집중")],
       "B": [("kpop","K-POP"),("adult","성인 K-POP (NEW)")]}
DAYS = ["MON","TUE","WED","THU","FRI","SAT"]
# (요일, 시작, 끝, 이름, 표시시간, 아래줄, 색키)  토요일은 13:00→16:00 위치에 맞춰 3시간 당겨 배치 (10월 표와 같은 방식)
A = []
for d, t in [("MON","YUNI"),("TUE","MINKYUNG"),("WED","YUNI"),("THU","MINKYUNG")]:
    A += [(d,16,17,"유아 K-POP","16:00 ~ 17:00",t,"kpop"),(d,17,18,"키즈 K-POP","17:00 ~ 18:00",t,"kpop")]
A += [("TUE",18.5,19+40/60,"BASIC","18:30 ~ 19:40","GAON","basic"),("THU",18.5,19+40/60,"BASIC","18:30 ~ 19:40","GAON","basic"),
      ("FRI",18.5,20,"PRO","18:30 ~ 20:00","YELLS","pro"),
      ("MON",19+40/60,20+50/60,"HEEL<br>CHOREO","19:40 ~ 20:50","HEEONE","heel"),
      ("TUE",19+40/60,20+50/60,"GIRLISH","19:40 ~ 20:50","ARIN","girlish"),
      ("WED",19+40/60,20+50/60,"WAACKING","19:40 ~ 20:50","J","waack"),
      ("THU",19+40/60,20+50/60,"HIP HOP","19:40 ~ 20:50","NOFF","hiphop"),
      ("FRI",20+10/60,21+20/60,"GIRLS<br>HIPHOP","20:10 ~ 21:20","MINKYUNG","girlish"),
      ("MON",20+50/60,22,"CHOREO","20:50 ~ 22:00","RAEKU","choreo"),
      ("WED",20+50/60,22,"JAZZ","20:50 ~ 22:00","KIRY","jazz"),
      ("THU",20+50/60,22,"CHOREO","20:50 ~ 22:00","HWAN.U","choreo"),
      ("SAT",16,17,"유아 K-POP","13:00 ~ 14:00","모집중","open"),("SAT",17,18,"키즈 K-POP","14:00 ~ 15:00","모집중","open"),
      ("SAT",18,19+10/60,"취미 K-POP","15:00 ~ 16:10","모집중","open")]
B = []
for d, t in [("MON","YUNI"),("TUE","MINKYUNG"),("WED","YUNI"),("THU","MINKYUNG")]:
    B.append((d,18,19+10/60,"취미 K-POP","18:00 ~ 19:10",t,"kpop"))
B += [("MON",19.5,20.5,"성인 K-POP","19:30 ~ 20:30","YUNI","adult"),("WED",19.5,20.5,"성인 K-POP","19:30 ~ 20:30","YUNI","adult")]

T0, T1, Y0, Y1 = 16, 22, 300, 1900
PX = (Y1 - Y0) / (T1 - T0)
COLW = 1040 / 6

def block(d, s, e, name, tm, sub, key):
    x = 20 + DAYS.index(d) * COLW + 4; y = Y0 + (s - T0) * PX + 4
    w = COLW - 8; h = (e - s) * PX - 8; c = C[key]
    subc = c if key in ("open",) else "#f3ece4"
    new = '<em>NEW</em>' if key == "adult" else ""
    return (f'<div class="b" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;'
            f'border-color:{c};background:linear-gradient(180deg,{c}38,{c}1a)">{new}<b>{name}</b>'
            f'<span style="color:{c}">{tm}</span><small style="color:{subc}">{sub}</small></div>')

def page(hall, blocks):
    leg = "".join(f'<span><i style="background:{C[k]}"></i>{n}</span>' for k, n in LEG[hall])
    lines = "".join(f'<div class="hl" style="top:{Y0+(t-T0)*PX:.0f}px"></div>' for t in range(T0+1, T1))
    cols = "".join(f'<div class="vl" style="left:{20+i*COLW:.0f}px"></div>' for i in range(1, 6))
    heads = "".join(f'<div class="dh{" sat" if d=="SAT" else ""}" style="left:{20+i*COLW:.0f}px;width:{COLW:.0f}px">{d}</div>' for i, d in enumerate(DAYS))
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">{FONTS}<style>
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1920px}}
body{{background:#140f0e;color:#f3ece4;font-family:Montserrat,"Noto Sans KR",sans-serif;position:relative;overflow:hidden}}
.hd{{position:absolute;left:0;right:0;top:0;height:156px;background:linear-gradient(180deg,#221715,#1a1210);border-bottom:4px solid #e0823e;display:flex;align-items:center;justify-content:center;gap:34px}}
.hd img{{height:92px}}
.hd .sep{{width:1px;height:80px;background:#4a3530}}
.hd .t{{text-align:center}}
.hd .t .s{{font-size:14px;letter-spacing:.42em;color:#e0823e;font-weight:600}}
.hd .t h1{{margin-top:4px;font-size:42px;font-weight:800;letter-spacing:.12em}}
.hd .t .m{{margin-top:4px;font-size:13px;letter-spacing:.2em;color:#9a8478}}
.lg{{position:absolute;left:0;right:0;top:160px;height:58px;display:flex;justify-content:center;align-items:center;gap:16px;font-size:12.5px;font-weight:600;color:#c9b8ab;border-bottom:1px solid #2a201d}}
.lg span{{display:flex;align-items:center;gap:6px}}.lg i{{display:block;width:10px;height:10px;border-radius:2px}}
.dhw{{position:absolute;left:20px;right:20px;top:236px;height:56px;background:#1c1513;border-bottom:2px solid #e0823e}}
.dh{{position:absolute;top:236px;height:56px;display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:700;letter-spacing:.14em}}
.dh.sat{{color:#e0a93c}}
.hl{{position:absolute;left:20px;right:20px;height:1px;background:#231a17}}
.vl{{position:absolute;top:300px;bottom:20px;width:1px;background:#231a17}}
.b{{position:absolute;border:1.5px solid;border-left-width:4px;border-radius:7px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:3px;padding:6px}}
.b b{{font-family:"Noto Sans KR",Montserrat,sans-serif;font-weight:900;font-size:21px;line-height:1.15}}
.b span{{font-size:15px;font-weight:700}}
.b small{{font-size:14px;font-weight:800;letter-spacing:.02em;font-family:"Noto Sans KR",Montserrat,sans-serif}}
.b em{{font-style:normal;font-size:12px;font-weight:800;letter-spacing:.12em;background:#f0c27a;color:#140f0e;padding:2px 8px;border-radius:4px;margin-bottom:4px}}
</style></head><body>
<div class="hd"><img src="raw-logo.png"><div class="sep"></div><div class="t"><div class="s">SUWON · 수원시 팔달구 매산로 136</div>
<h1>{hall} HALL PROGRAM TABLE</h1><div class="m">RAW DANCE STUDIO · {hall}홀 주간 프로그램표 · 2026. 11</div></div></div>
<div class="lg">{leg}</div><div class="dhw"></div>{heads}{lines}{cols}{"".join(block(*b) for b in blocks)}
</body></html>"""

if __name__ == "__main__":
    for hall, blocks in [("A", A), ("B", B)]:
        html = page(hall, blocks)
        name = f"hall-{hall.lower()}-2026-11"
        (HERE / f"{name}.html").write_text(html, encoding="utf-8")
        tmp = HERE / f".{name}.render.html"; tmp.write_text(html.replace(FONTS, ""), encoding="utf-8")
        out = HERE / f"{name}.png"
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1080,2200", f"--screenshot={out}", tmp.as_uri()],
                       check=True, capture_output=True)
        tmp.unlink()
        Image.open(out).convert("RGB").crop((0, 0, 1080, 1920)).save(out)
