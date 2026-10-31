"""성인 K-POP반 오픈 카드뉴스 (1080x1350, 2장)."""
import subprocess
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Montserrat:ital,wght@0,500;0,600;0,700;1,700&display=swap" rel="stylesheet">'
BASE = """*{box-sizing:border-box;margin:0;padding:0}html,body{width:1080px;height:1350px}
body{background:#0e0d12;color:#f4f2ee;font-family:"Noto Sans KR",sans-serif;position:relative;overflow:hidden}
.g1{position:absolute;width:1200px;height:1200px;border-radius:50%;right:-620px;top:-640px;background:radial-gradient(circle,rgba(124,92,255,.40),rgba(124,92,255,0) 62%)}
.g2{position:absolute;width:1100px;height:1100px;border-radius:50%;left:-560px;bottom:-640px;background:radial-gradient(circle,rgba(124,92,255,.26),rgba(124,92,255,0) 62%)}
.p{position:absolute;inset:0 76px;display:flex;flex-direction:column}
.top{height:146px;display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid #2a2832;padding-bottom:27px}
.top img{height:40px;display:block}
.en{font-family:Montserrat,sans-serif;font-weight:500;font-size:15px;letter-spacing:.38em;color:#c3bfcc;text-align:right;line-height:1.75;margin-right:-.38em}
.bot{height:110px;border-top:1px solid #2a2832;display:flex;justify-content:space-between;align-items:flex-start;padding-top:24px;font-family:Montserrat,sans-serif;font-size:18px;letter-spacing:.2em}
.bot .h{color:#8f8a9c;font-weight:500}.bot .s{font-weight:600}
"""

card1 = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">{FONTS}<style>{BASE}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center}}
.new{{display:inline-flex;align-self:flex-start;align-items:center;gap:14px;font-family:Montserrat,sans-serif;font-weight:600;font-size:22px;letter-spacing:.34em;color:#b9a6ff}}
.new i{{display:block;width:12px;height:12px;border-radius:50%;background:#b9a6ff;box-shadow:0 0 18px #b9a6ff}}
.t{{margin-top:26px;font-family:Montserrat,sans-serif;font-weight:700;font-style:italic;line-height:.84;letter-spacing:-.04em;margin-left:-10px}}
.t .a{{display:block;font-size:208px;color:transparent;-webkit-text-stroke:2.5px #b9a6ff}}
.t .b{{display:block;font-size:262px}}
.kr{{margin-top:40px;font-size:62px;font-weight:900;letter-spacing:-1.5px}}
.kr span{{color:#b9a6ff}}
.when{{margin-top:54px;display:flex;gap:46px;align-items:flex-end}}
.when div{{display:flex;flex-direction:column;gap:8px}}
.when small{{font-family:Montserrat,sans-serif;font-weight:600;font-size:17px;letter-spacing:.3em;color:#8f8a9c}}
.when b{{font-family:Montserrat,sans-serif;font-weight:700;font-size:44px;letter-spacing:-.01em}}
</style></head><body><div class="g1"></div><div class="g2"></div><div class="p">
<div class="top"><img src="raw-logo.png"><div class="en">SUWON<br>NEW CLASS</div></div>
<div class="mid">
<div class="new"><i></i>NOW OPEN</div>
<div class="t"><span class="a">ADULT</span><span class="b">K-POP</span></div>
<div class="kr">성인 K-POP반 <span>오픈</span></div>
<div class="when"><div><small>DAY</small><b>MON · WED</b></div><div><small>TIME</small><b>19:30 – 20:30</b></div><div><small>T.</small><b>YUNI</b></div></div>
</div>
<div class="bot"><span class="h">@RAWDANCE_SUWON</span><span class="s">SWIPE →</span></div>
</div></body></html>"""

card2 = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">{FONTS}<style>{BASE}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center}}
.k{{font-family:Montserrat,sans-serif;font-weight:600;font-size:20px;letter-spacing:.34em;color:#b9a6ff}}
h1{{margin-top:18px;font-size:76px;font-weight:900;letter-spacing:-2px}}
.rows{{margin-top:48px;border-top:1px solid #2a2832}}
.r{{display:flex;align-items:baseline;padding:30px 0;border-bottom:1px solid #2a2832}}
.r small{{width:190px;flex:none;font-family:Montserrat,sans-serif;font-weight:600;font-size:18px;letter-spacing:.3em;color:#8f8a9c}}
.r b{{font-size:44px;font-weight:700;letter-spacing:-.5px}}
.r b em{{font-style:normal;font-weight:400;color:#c3bfcc;font-size:32px;margin-left:14px}}
.ask{{margin-top:56px}}
.ask .k{{font-size:18px}}
.ask p{{margin-top:16px;font-size:36px;font-weight:700;line-height:1.5}}
.ask p span{{color:#c3bfcc;font-weight:400}}
.legal{{margin-top:26px;font-size:21px;color:#8f8a9c;line-height:1.6}}
</style></head><body><div class="g1"></div><div class="g2"></div><div class="p">
<div class="top"><img src="raw-logo.png"><div class="en">SUWON<br>NEW CLASS</div></div>
<div class="mid">
<div class="k">CLASS INFO</div>
<h1>성인 K-POP반</h1>
<div class="rows">
<div class="r"><small>DAY</small><b>월 · 수<em>주 2회</em></b></div>
<div class="r"><small>TIME</small><b>19:30 ~ 20:30</b></div>
<div class="r"><small>TEACHER</small><b>YUNI</b></div>
<div class="r"><small>FOR</small><b>성인</b></div>
</div>
<div class="ask"><div class="k">CONTACT</div>
<p>카카오톡 채널 '로우댄스수원점학원'<br><span>인스타 DM · 031-225-6600</span></p></div>
<div class="legal">수원시 팔달구 매산로 136, 4층 · 학원등록번호 제8189호</div>
</div>
<div class="bot"><span class="h">@RAWDANCE_SUWON</span><span class="s">RAW DANCE STUDIO</span></div>
</div></body></html>"""

def render(name, html):
    (HERE / f"{name}.html").write_text(html, encoding="utf-8")
    tmp = HERE / f".{name}.render.html"
    tmp.write_text(html.replace(FONTS, ""), encoding="utf-8")
    out = HERE / f"{name}.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1080,1600",
                    f"--screenshot={out}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    Image.open(out).convert("RGB").crop((0, 0, 1080, 1350)).save(out)

render("card1", card1); render("card2", card2)
a, b = Image.open(HERE / "card1.png"), Image.open(HERE / "card2.png")
sheet = Image.new("RGB", (2180, 1350), (40, 40, 40)); sheet.paste(a, (0, 0)); sheet.paste(b, (1100, 0))
sheet.resize((1090, 675)).save(HERE / ".preview.png")
