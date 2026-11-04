"""2026년 11월 주간 시간표 (A·B홀 통합, 요일별 리스트형, 1080x1920)."""
import subprocess
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Montserrat:ital,wght@0,500;0,600;0,700;1,700&display=swap" rel="stylesheet">'

# (시작, 끝, 수업명, 강사, 홀, 표시)  표시: "" / "new" / "open"(모집중)
DAYS = {
 "MON": [("16:00","17:00","유아 K-POP","YUNI","A",""),("17:00","18:00","키즈 K-POP","YUNI","A",""),
         ("18:00","19:10","취미 K-POP","YUNI","B",""),("19:30","20:30","성인 K-POP","YUNI","","new"),
         ("19:40","20:50","HEELSCHOREO","HEEONE","A",""),("20:50","22:00","CHOREO","RAEKU","A","")],
 "TUE": [("16:00","17:00","유아 K-POP","MINKYUNG","A",""),("17:00","18:00","키즈 K-POP","MINKYUNG","A",""),
         ("18:00","19:10","취미 K-POP","MINKYUNG","B",""),("18:30","19:40","BASIC","GAON","A",""),
         ("19:40","20:50","GIRLISH","ARIN","A","")],
 "WED": [("16:00","17:00","유아 K-POP","YUNI","A",""),("17:00","18:00","키즈 K-POP","YUNI","A",""),
         ("18:00","19:10","취미 K-POP","YUNI","B",""),("19:30","20:30","성인 K-POP","YUNI","","new"),
         ("19:40","20:50","WAACKING","J","A",""),("20:50","22:00","JAZZ","KIRY","A","")],
 "THU": [("16:00","17:00","유아 K-POP","MINKYUNG","A",""),("17:00","18:00","키즈 K-POP","MINKYUNG","A",""),
         ("18:00","19:10","취미 K-POP","MINKYUNG","B",""),("18:30","19:40","BASIC","GAON","A",""),
         ("19:40","20:50","HIP HOP","NOFF","A",""),("20:50","22:00","CHOREO","HWAN.U","A","")],
 "FRI": [("18:30","20:00","PRO 전문반","YELLS","A",""),("20:10","21:20","GIRLS HIPHOP","MINKYUNG","A","")],
 "SAT": [("13:00","14:00","유아 K-POP","REGINA","A","open"),("14:00","15:00","키즈 K-POP","REGINA","A","open"),
         ("15:00","16:10","취미 K-POP","REGINA","A","open")],
}
KR = {"MON":"월","TUE":"화","WED":"수","THU":"목","FRI":"금","SAT":"토"}

def day_html(d):
    rows = []
    for s, e, name, t, hall, mark in DAYS[d]:
        badge = {"new": '<em class="new">NEW</em>', "open": '<em class="open">모집중</em>'}.get(mark, "")
        h = f'<i>{hall}</i>' if hall else '<i class="x"></i>'
        rows.append(f'<div class="r{" hl" if mark=="new" else ""}"><span class="tm">{s}<small>–{e}</small></span>'
                    f'<span class="nm">{name}{badge}</span><span class="tc">{t}</span>{h}</div>')
    return f'<section><h3>{d}<span>{KR[d]}</span></h3>{"".join(rows)}</section>'

html = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">{FONTS}<style>
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1920px}}
body{{background:#0e0d12;color:#f4f2ee;font-family:"Noto Sans KR",sans-serif;position:relative;overflow:hidden}}
.g1{{position:absolute;width:1300px;height:1300px;border-radius:50%;right:-700px;top:-720px;background:radial-gradient(circle,rgba(124,92,255,.38),rgba(124,92,255,0) 62%)}}
.g2{{position:absolute;width:1200px;height:1200px;border-radius:50%;left:-640px;bottom:-700px;background:radial-gradient(circle,rgba(124,92,255,.24),rgba(124,92,255,0) 62%)}}
.p{{position:absolute;inset:0 64px;display:flex;flex-direction:column}}
.top{{padding-top:72px;display:flex;justify-content:space-between;align-items:flex-start}}
.top img{{height:46px}}
.top .en{{font-family:Montserrat,sans-serif;font-weight:500;font-size:16px;letter-spacing:.36em;color:#c3bfcc;text-align:right;line-height:1.8;margin-right:-.36em}}
.ttl{{margin-top:56px;display:flex;align-items:flex-end;justify-content:space-between;padding-bottom:30px;border-bottom:1px solid #2a2832}}
.ttl h1{{font-family:Montserrat,sans-serif;font-weight:700;font-style:italic;font-size:118px;line-height:.86;letter-spacing:-.04em;margin-left:-6px}}
.ttl h1 span{{display:block;color:transparent;-webkit-text-stroke:2px #b9a6ff;font-size:96px}}
.ttl .m{{text-align:right;font-family:Montserrat,sans-serif}}
.ttl .m b{{display:block;font-size:92px;font-weight:700;line-height:.9;color:#b9a6ff}}
.ttl .m small{{display:block;margin-top:8px;font-size:18px;font-weight:600;letter-spacing:.34em;color:#c3bfcc;margin-right:-.34em}}
.grid{{margin-top:36px;display:grid;grid-template-columns:1fr 1fr;column-gap:40px;align-items:start}}
.col{{display:flex;flex-direction:column;gap:30px}}
section h3{{display:flex;align-items:baseline;gap:12px;font-family:Montserrat,sans-serif;font-weight:700;font-size:30px;letter-spacing:.12em;padding-bottom:10px;border-bottom:2px solid #b9a6ff;margin-bottom:6px}}
section h3 span{{font-family:"Noto Sans KR";font-size:20px;font-weight:500;color:#8f8a9c;letter-spacing:0}}
.r{{display:grid;grid-template-columns:118px 1fr auto 30px;align-items:center;column-gap:12px;padding:11px 0;border-bottom:1px solid #22202a}}
.r.hl{{background:linear-gradient(90deg,rgba(185,166,255,.16),rgba(185,166,255,0));margin:0 -10px;padding:11px 10px}}
.tm{{font-family:Montserrat,sans-serif;font-weight:600;font-size:21px;line-height:1.05}}
.tm small{{display:block;font-size:14px;font-weight:500;color:#8f8a9c;margin-top:3px}}
.nm{{font-size:21px;font-weight:700;letter-spacing:-.2px;white-space:nowrap;display:flex;align-items:center;gap:8px}}
.nm em{{font-style:normal;font-family:Montserrat,sans-serif;font-size:12px;font-weight:700;letter-spacing:.1em;padding:3px 7px;border-radius:5px}}
.nm .new{{background:#b9a6ff;color:#0e0d12}}
.nm .open{{font-family:"Noto Sans KR";letter-spacing:0;background:rgba(245,190,70,.16);color:#f5be46}}
.tc{{font-family:Montserrat,sans-serif;font-weight:500;font-size:15px;letter-spacing:.06em;color:#c3bfcc;text-align:right}}
.r i{{font-style:normal;font-family:Montserrat,sans-serif;font-weight:700;font-size:13px;width:26px;height:26px;border-radius:50%;border:1.5px solid #4a4655;color:#8f8a9c;display:flex;align-items:center;justify-content:center}}
.r i.x{{border:0}}
.bot{{margin-top:auto;padding:28px 0 64px;border-top:1px solid #2a2832;display:flex;justify-content:space-between;align-items:flex-end;font-size:20px;color:#a6a1b2;line-height:1.6}}
.bot b{{color:#f4f2ee;font-weight:500}}
.bot .lg{{display:flex;gap:18px;font-family:Montserrat,sans-serif;font-size:14px;letter-spacing:.12em;color:#8f8a9c;align-items:center}}
.bot .lg span{{display:flex;align-items:center;gap:7px}}
.bot .lg i{{font-style:normal;font-weight:700;font-size:11px;width:22px;height:22px;border-radius:50%;border:1.5px solid #4a4655;display:flex;align-items:center;justify-content:center}}
</style></head><body><div class="g1"></div><div class="g2"></div><div class="p">
<div class="top"><img src="raw-logo.png"><div class="en">SUWON<br>수원시 팔달구 매산로 136</div></div>
<div class="ttl"><h1>WEEKLY<span>TIMETABLE</span></h1><div class="m"><b>11</b><small>2026 NOV</small></div></div>
<div class="grid"><div class="col">{day_html("MON")}{day_html("TUE")}{day_html("WED")}</div>
<div class="col">{day_html("THU")}{day_html("FRI")}{day_html("SAT")}</div></div>
<div class="bot"><div><b>031-225-6600</b> · @rawdance_suwon<br>카카오톡 '로우댄스수원점학원'</div>
<div class="lg"><span><i>A</i>A HALL</span><span><i>B</i>B HALL</span></div></div>
</div></body></html>"""

if __name__ == "__main__":
    (HERE / "timetable-2026-11.html").write_text(html, encoding="utf-8")
    tmp = HERE / ".render.html"; tmp.write_text(html.replace(FONTS, ""), encoding="utf-8")
    out = HERE / "timetable-2026-11.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1080,2200", f"--screenshot={out}", tmp.as_uri()],
                   check=True, capture_output=True)
    tmp.unlink()
    Image.open(out).convert("RGB").crop((0, 0, 1080, 1920)).save(out)
