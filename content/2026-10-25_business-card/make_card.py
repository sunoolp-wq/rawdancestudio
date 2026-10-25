"""로우댄스학원 수원점 명함 (90x50mm, 재단 여유 2mm씩 → 94x54mm, 300dpi).
사용: PYTHONPATH=<qrcode 설치 경로> python3 make_card.py  → front.png, back.png, card-print.pdf
"""
import subprocess, qrcode
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
W, H = 1110, 638            # 94x54mm @300dpi
SAFE = 71                   # 재단선 안쪽 4mm + 여유 2mm = 6mm
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Montserrat:wght@500;600&display=swap" rel="stylesheet">'
BASE = f"""*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{font-family:"Noto Sans KR",sans-serif;position:relative}}"""

# 네이버 플레이스 QR
qr = qrcode.QRCode(border=0, box_size=7, error_correction=qrcode.constants.ERROR_CORRECT_M)
qr.add_data("https://naver.me/x52OO6LN"); qr.make(fit=True)
qr.make_image(fill_color=(14, 13, 18), back_color=(244, 242, 238)).save(HERE / "qr-place.png")

FONTS2 = FONTS.replace("Montserrat:wght@500;600", "Montserrat:ital,wght@0,500;0,600;0,700;1,700")
front = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS2}<style>{BASE}
body{{background:#0e0d12;color:#f4f2ee}}
.glow{{position:absolute;width:1000px;height:1000px;border-radius:50%;right:-520px;top:-560px;background:radial-gradient(circle,rgba(124,92,255,.30),rgba(124,92,255,0) 62%)}}
.big{{position:absolute;right:-34px;bottom:-52px;font-family:Montserrat,sans-serif;font-style:italic;font-weight:700;font-size:232px;letter-spacing:-.04em;line-height:1;color:transparent;-webkit-text-stroke:2px rgba(185,166,255,.42)}}
.logo{{position:absolute;left:{SAFE+6}px;top:{SAFE+4}px;width:200px}}
.btm{{position:absolute;left:{SAFE+6}px;bottom:{SAFE+2}px}}
.btm .s{{font-family:Montserrat,sans-serif;font-weight:600;font-size:25px;letter-spacing:.5em;color:#b9a6ff}}
.btm .k{{margin-top:8px;font-size:22px;font-weight:500;color:#c3bfcc;letter-spacing:.02em}}
.eq{{position:absolute;right:{SAFE+6}px;top:{SAFE+8}px;display:flex;align-items:flex-end;gap:7px;height:60px}}
.eq i{{display:block;width:5px;border-radius:3px;background:#b9a6ff}}
</style></head><body><div class="glow"></div><div class="big">DANCE</div>
<img class="logo" src="raw-logo.png">
<div class="eq">""" + "".join(f'<i style="height:{h}%;opacity:{o}"></i>' for h, o in [(35,.5),(70,.7),(100,1),(55,.8),(85,.9),(40,.6),(65,.8),(25,.5)]) + f"""</div>
<div class="btm"><div class="s">SUWON</div><div class="k">로우댄스학원 수원점</div></div>
</body></html>"""

back = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS2}<style>{BASE}
body{{background:#0e0d12;color:#f4f2ee}}
.glow{{position:absolute;width:900px;height:900px;border-radius:50%;left:-470px;bottom:-560px;background:radial-gradient(circle,rgba(124,92,255,.26),rgba(124,92,255,0) 62%)}}
.p{{position:absolute;inset:{SAFE+2}px {SAFE+6}px {SAFE}px {SAFE+6}px;display:flex;justify-content:space-between;gap:30px}}
.l{{display:flex;flex-direction:column;justify-content:space-between;min-width:0}}
.name{{font-size:38px;font-weight:700;letter-spacing:-.5px;line-height:1.1}}
.en{{margin-top:10px;font-family:Montserrat,sans-serif;font-weight:600;font-size:16px;letter-spacing:.34em;color:#b9a6ff}}
.cls{{margin-top:22px;font-family:Montserrat,sans-serif;font-weight:500;font-size:15.5px;letter-spacing:.14em;color:#8f8a9c;line-height:1.7}}
.ct{{display:grid;grid-template-columns:auto 1fr;column-gap:18px;row-gap:2px;font-size:25px;line-height:1.5}}
.ct b{{font-family:Montserrat,sans-serif;font-weight:600;font-size:16px;letter-spacing:.14em;color:#b9a6ff;padding-top:7px}}
.addr{{margin-top:12px;font-size:20px;color:#a6a1b2;line-height:1.5}}
.r{{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:10px;flex:none}}
.tile{{background:#f4f2ee;border-radius:14px;padding:12px}}
.tile img{{width:150px;height:150px;image-rendering:pixelated;display:block}}
.r span{{font-family:Montserrat,sans-serif;font-weight:600;font-size:14px;letter-spacing:.22em;color:#8f8a9c}}
</style></head><body><div class="glow"></div><div class="p">
<div class="l"><div><div class="name">로우댄스학원 수원점</div><div class="en">RAW DANCE STUDIO SUWON</div>
<div class="cls">ADMISSION · AUDITION · K-POP<br>HIPHOP · JAZZ · WAACKING · CHOREOGRAPHY</div></div>
<div><div class="ct">
<b>TEL</b><span>031-225-6600</span>
<b>KAKAO</b><span>로우댄스수원점학원</span>
<b>INSTA</b><span>@rawdance_suwon</span></div>
<div class="addr">경기도 수원시 팔달구 매산로 136, 유림빌딩 4층 401호 · 학원등록번호 제8189호</div></div></div>
<div class="r"><div class="tile"><img src="qr-place.png"></div><span>NAVER MAP</span></div>
</div></body></html>"""

back_director = back.replace('<div class="l"><div><div class="name">로우댄스학원 수원점</div><div class="en">RAW DANCE STUDIO SUWON</div>\n<div class="cls">ADMISSION · AUDITION · K-POP<br>HIPHOP · JAZZ · WAACKING · CHOREOGRAPHY</div></div>', '<div class="l"><div><div class="name">이선우 <small>원장</small></div><div class="en">LEE SUNWOO · DIRECTOR</div>\n<div class="org">로우댄스학원 수원점 <span>RAW DANCE STUDIO SUWON</span></div></div>').replace(".r{{", ".r{{").replace("</style>", ".name small{font-size:24px;font-weight:500;color:#c3bfcc;margin-left:6px;letter-spacing:0}.org{margin-top:22px;font-size:22px;font-weight:500;color:#c3bfcc}.org span{display:block;margin-top:4px;font-family:Montserrat,sans-serif;font-weight:500;font-size:14px;letter-spacing:.24em;color:#8f8a9c}</style>")

def render(name, html):
    src = HERE / f"{name}.html"; src.write_text(html, encoding="utf-8")
    tmp = HERE / f".{name}.render.html"
    tmp.write_text(html.replace(FONTS2, ""), encoding="utf-8")   # 설치된 글꼴로 렌더
    out = HERE / f"{name}.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={W},{H+300}",
                    f"--screenshot={out}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    Image.open(out).convert("RGB").crop((0, 0, W, H)).save(out, dpi=(300, 300))
    return out

f, b = render("front", front), render("back", back)
imgs = [Image.open(f).convert("RGB"), Image.open(b).convert("RGB")]
imgs[0].save(HERE / "card-print.pdf", save_all=True, append_images=imgs[1:], resolution=300)
bd = render("back-director", back_director)
imgs_d = [imgs[0], Image.open(bd).convert("RGB")]
imgs_d[0].save(HERE / "card-print-director.pdf", save_all=True, append_images=imgs_d[1:], resolution=300)

# 미리보기: 재단선 표시
from PIL import ImageDraw
pv = Image.new("RGB", (W * 2 + 60, H + 40), (200, 200, 200))
for i, im in enumerate(imgs):
    c = im.copy(); d = ImageDraw.Draw(c)
    d.rectangle((24, 24, W - 25, H - 25), outline=(255, 60, 60), width=2)   # 재단선(2mm)
    pv.paste(c, (20 + i * (W + 20), 20))
pv.save(HERE / "preview.png")
print("ok")
