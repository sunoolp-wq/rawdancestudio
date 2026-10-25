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

front = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{BASE}
body{{background:#0e0d12;color:#f4f2ee;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px}}
.glow{{position:absolute;width:900px;height:900px;border-radius:50%;left:-430px;bottom:-560px;background:radial-gradient(circle,rgba(124,92,255,.34),rgba(124,92,255,0) 62%)}}
img{{width:220px;position:relative}}
.s{{font-family:Montserrat,sans-serif;font-weight:600;font-size:27px;letter-spacing:.62em;margin-right:-.62em;color:#b9a6ff;position:relative}}
</style></head><body><div class="glow"></div><img src="raw-logo.png"><div class="s">SUWON</div></body></html>"""

back = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{BASE}
body{{background:#f4f2ee;color:#16141c}}
.p{{position:absolute;inset:{SAFE}px {SAFE+4}px {SAFE}px {SAFE+4}px;display:flex;flex-direction:column;justify-content:space-between}}
.name{{font-size:40px;font-weight:700;letter-spacing:-.5px;line-height:1.1}}
.en{{margin-top:10px;font-family:Montserrat,sans-serif;font-weight:600;font-size:17px;letter-spacing:.32em;color:#6d4fe0}}
.cls{{margin-top:16px;font-size:25px;font-weight:500;color:#4a4655}}
.row{{display:flex;justify-content:space-between;align-items:flex-end;gap:24px}}
.ct{{display:grid;grid-template-columns:auto 1fr;column-gap:16px;row-gap:3px;font-size:26px;line-height:1.45}}
.ct b{{font-family:Montserrat,sans-serif;font-weight:600;font-size:19px;letter-spacing:.08em;color:#6d4fe0;padding-top:5px}}
.addr{{margin-top:10px;font-size:22px;color:#4a4655;line-height:1.45}}
.q{{display:flex;flex-direction:column;align-items:center;gap:8px;flex:none}}
.q img{{width:175px;height:175px;image-rendering:pixelated}}
.q span{{font-size:19px;color:#4a4655}}
</style></head><body><div class="p">
<div><div class="name">로우댄스학원 수원점</div><div class="en">RAW DANCE STUDIO SUWON</div>
<div class="cls">예고·대학 입시 · 오디션 · K-POP · 장르 클래스</div></div>
<div class="row"><div><div class="ct">
<b>TEL</b><span>031-225-6600</span>
<b>KAKAO</b><span>로우댄스수원점학원</span>
<b>INSTA</b><span>@rawdance_suwon</span></div>
<div class="addr">경기도 수원시 팔달구 매산로 136, 유림빌딩 4층 401호<br>학원등록번호 제8189호</div></div>
<div class="q"><img src="qr-place.png"><span>네이버 지도</span></div></div>
</div></body></html>"""

def render(name, html):
    src = HERE / f"{name}.html"; src.write_text(html, encoding="utf-8")
    tmp = HERE / f".{name}.render.html"
    tmp.write_text(html.replace(FONTS, ""), encoding="utf-8")   # 설치된 글꼴로 렌더
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

# 미리보기: 재단선 표시
from PIL import ImageDraw
pv = Image.new("RGB", (W * 2 + 60, H + 40), (200, 200, 200))
for i, im in enumerate(imgs):
    c = im.copy(); d = ImageDraw.Draw(c)
    d.rectangle((24, 24, W - 25, H - 25), outline=(255, 60, 60), width=2)   # 재단선(2mm)
    pv.paste(c, (20 + i * (W + 20), 20))
pv.save(HERE / "preview.png")
print("ok")
