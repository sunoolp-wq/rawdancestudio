"""11월 시간표 인스타 피드용 캐러셀 (1080x1350, 4장: 표지 + 월화 / 수목 / 금토)."""
import subprocess
from pathlib import Path
from PIL import Image
from make_timetable import DAYS, KR, FONTS, CHROME

HERE = Path(__file__).parent
BASE = """*{box-sizing:border-box;margin:0;padding:0}html,body{width:1080px;height:1350px}
body{background:#0e0d12;color:#f4f2ee;font-family:"Noto Sans KR",sans-serif;position:relative;overflow:hidden}
.g1{position:absolute;width:1200px;height:1200px;border-radius:50%;right:-640px;top:-660px;background:radial-gradient(circle,rgba(124,92,255,.38),rgba(124,92,255,0) 62%)}
.g2{position:absolute;width:1100px;height:1100px;border-radius:50%;left:-580px;bottom:-660px;background:radial-gradient(circle,rgba(124,92,255,.24),rgba(124,92,255,0) 62%)}
.p{position:absolute;inset:0 76px;display:flex;flex-direction:column}
.top{height:146px;display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid #2a2832;padding-bottom:27px}
.top img{height:40px;display:block}
.en{font-family:Montserrat,sans-serif;font-weight:500;font-size:15px;letter-spacing:.38em;color:#c3bfcc;text-align:right;line-height:1.75;margin-right:-.38em}
.bot{height:110px;border-top:1px solid #2a2832;display:flex;justify-content:space-between;align-items:flex-start;padding-top:24px;font-family:Montserrat,sans-serif;font-size:18px;letter-spacing:.2em}
.bot .h{color:#8f8a9c;font-weight:500}.bot .s{font-weight:600}
"""
ROW = """
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;gap:34px}
h3{display:flex;align-items:baseline;gap:14px;font-family:Montserrat,sans-serif;font-weight:700;font-size:36px;letter-spacing:.12em;padding-bottom:10px;border-bottom:2px solid #b9a6ff}
h3 span{font-family:"Noto Sans KR";font-size:24px;font-weight:500;color:#8f8a9c;letter-spacing:0}
.r{display:grid;grid-template-columns:200px 1fr auto 40px;align-items:center;column-gap:18px;padding:12px 0;border-bottom:1px solid #22202a}
.r.hl{background:linear-gradient(90deg,rgba(185,166,255,.18),rgba(185,166,255,0));margin:0 -14px;padding:12px 14px}
.tm{font-family:Montserrat,sans-serif;font-weight:600;font-size:28px;white-space:nowrap}
.tm small{font-size:20px;font-weight:500;color:#8f8a9c;margin-left:4px}
.nm{font-size:30px;font-weight:700;white-space:nowrap;display:flex;align-items:center;gap:12px}
.nm em{font-style:normal;font-family:Montserrat,sans-serif;font-size:15px;font-weight:700;letter-spacing:.1em;padding:4px 9px;border-radius:6px}
.nm .new{background:#b9a6ff;color:#0e0d12}
.nm .open{font-family:"Noto Sans KR";letter-spacing:0;background:rgba(245,190,70,.16);color:#f5be46}
.tc{font-family:Montserrat,sans-serif;font-weight:500;font-size:20px;letter-spacing:.08em;color:#c3bfcc;text-align:right}
.r i{font-style:normal;font-family:Montserrat,sans-serif;font-weight:700;font-size:16px;width:34px;height:34px;border-radius:50%;border:2px solid #4a4655;color:#8f8a9c;display:flex;align-items:center;justify-content:center}
.r i.x{border:0}
"""

def page(body, css, bot_right="SWIPE →"):
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">{FONTS}<style>{BASE}{css}</style></head><body>'
            f'<div class="g1"></div><div class="g2"></div><div class="p">'
            f'<div class="top"><img src="raw-logo.png"><div class="en">SUWON<br>2026 NOVEMBER</div></div>'
            f'{body}<div class="bot"><span class="h">@RAWDANCE_SUWON</span><span class="s">{bot_right}</span></div></div></body></html>')

def day(d):
    rows = []
    for s, e, name, t, hall, mark in DAYS[d]:
        badge = {"new": '<em class="new">NEW</em>', "open": '<em class="open">모집중</em>'}.get(mark, "")
        h = f'<i>{hall}</i>' if hall else '<i class="x"></i>'
        rows.append(f'<div class="r{" hl" if mark=="new" else ""}"><span class="tm">{s}<small>–{e}</small></span>'
                    f'<span class="nm">{name}{badge}</span><span class="tc">{t}</span>{h}</div>')
    return f'<section><h3>{d}<span>{KR[d]}요일</span></h3>{"".join(rows)}</section>'

cover_css = """
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.k{font-family:Montserrat,sans-serif;font-weight:600;font-size:22px;letter-spacing:.38em;color:#b9a6ff;margin-right:-.38em}
.num{margin-top:10px;font-family:Montserrat,sans-serif;font-weight:700;font-style:italic;font-size:420px;line-height:.9;letter-spacing:-.06em;color:transparent;-webkit-text-stroke:3px #b9a6ff;position:relative;left:-14px}
.t{margin-top:6px;font-family:Montserrat,sans-serif;font-weight:700;font-style:italic;font-size:120px;line-height:.9;letter-spacing:-.04em;position:relative;left:-8px}
.kr{margin-top:34px;font-size:52px;font-weight:900;letter-spacing:-1px}
.nw{margin-top:40px;display:flex;align-items:center;gap:16px;padding:16px 28px;border:1.5px solid rgba(185,166,255,.5);border-radius:999px;font-size:28px;font-weight:500}
.nw em{font-style:normal;font-family:Montserrat,sans-serif;font-size:16px;font-weight:700;letter-spacing:.1em;background:#b9a6ff;color:#0e0d12;padding:5px 10px;border-radius:6px}
"""
cover = page('<div class="mid"><div class="k">WEEKLY TIMETABLE</div><div class="num">11</div>'
             '<div class="t">NOVEMBER</div><div class="kr">11월 시간표</div>'
             '<div class="nw"><em>NEW</em>성인 K-POP · 월·수 19:30 – 20:30</div></div>', cover_css)

last_css = ROW + """.legend{display:flex;gap:28px;font-family:Montserrat,sans-serif;font-size:18px;letter-spacing:.14em;color:#8f8a9c;align-items:center}
.legend span{display:flex;align-items:center;gap:10px}
.legend i{font-style:normal;font-weight:700;font-size:15px;width:32px;height:32px;border-radius:50%;border:2px solid #4a4655;display:flex;align-items:center;justify-content:center}
.ct{font-size:26px;line-height:1.6;color:#c3bfcc}.ct b{color:#f4f2ee;font-weight:700}"""
pages = {
 "slide1": cover,
 "slide2": page(f'<div class="mid">{day("MON")}{day("TUE")}</div>', ROW),
 "slide3": page(f'<div class="mid">{day("WED")}{day("THU")}</div>', ROW),
 "slide4": page(f'<div class="mid">{day("FRI")}{day("SAT")}'
                '<div class="legend"><span><i>A</i>A HALL</span><span><i>B</i>B HALL</span></div>'
                '<div class="ct"><b>문의</b> 인스타 DM · 카카오톡 \'로우댄스수원점학원\' · 031-225-6600<br>수원시 팔달구 매산로 136, 4층</div></div>',
                last_css, "RAW DANCE STUDIO"),
}
for name, html in pages.items():
    (HERE / f"{name}.html").write_text(html, encoding="utf-8")
    tmp = HERE / f".{name}.render.html"; tmp.write_text(html.replace(FONTS, ""), encoding="utf-8")
    out = HERE / f"{name}.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1080,1600", f"--screenshot={out}", tmp.as_uri()],
                   check=True, capture_output=True)
    tmp.unlink()
    Image.open(out).convert("RGB").crop((0, 0, 1080, 1350)).save(out)
ims = [Image.open(HERE / f"slide{i}.png") for i in range(1, 5)]
sheet = Image.new("RGB", (4 * 1080 + 60, 1350), (40, 40, 40))
for i, im in enumerate(ims): sheet.paste(im, (i * 1100, 0))
sheet.resize((sheet.width // 3, 450)).save(HERE / ".preview.png")
