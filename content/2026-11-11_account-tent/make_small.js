// 계좌번호 삼각 POP 명함 크기 (면 90×50mm, 띠 90×150mm) — A4 가로에 3개, 잘라서 접기 → tent-card-print.pdf
// node content/2026-11-11_account-tent/make_small.js
const { launch } = require('../../tools/pw.js'); const fs = require('fs'), path = require('path');
const logo = fs.readFileSync(path.join(__dirname, '../../tools/daily-story/raw-logo.png')).toString('base64');
const face = `<div class="face"><div class="glow"></div><div class="big">RAW</div>
  <div class="top"><img src="data:image/png;base64,${logo}"><span>계좌 이체 안내</span></div>
  <div class="bank"><b>KB</b>국민은행</div><div class="no">529437-01-019625</div>
  <div class="who">예금주 <b>이선우</b> (로우댄스수원점학원)</div></div>`;
const strip = x => `<div class="strip" style="left:${x}mm">
  <div class="pn p1">${face}</div><div class="pn p2">${face}</div><div class="pn p3">바닥 · 테이프로 붙이기</div>
  <i class="fold" style="top:50mm"></i><i class="fold" style="top:100mm"></i></div>`;
// 자르는 표시: 띠 사이 6mm 간격, 세로 표시는 각 띠 좌우 끝 위·아래, 가로 표시는 맨 바깥 좌우만
const xs = [7.5, 103.5, 199.5], top = 30;
const crop = xs.map(x => [x, x + 90]).flat().map(x => `<i class="cv" style="left:${x}mm;top:${top - 7}mm"></i><i class="cv" style="left:${x}mm;top:${top + 152}mm"></i>`).join('')
  + [top, top + 150].map(y => `<i class="ch" style="top:${y}mm;left:0.5mm"></i><i class="ch" style="top:${y}mm;left:291.5mm"></i>`).join('');
const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Noto+Sans+KR:wght@500;700;900&display=swap" rel="stylesheet">
<style>@page{size:297mm 210mm;margin:0}*{margin:0;padding:0;box-sizing:border-box}
body{width:297mm;height:210mm;background:#fff;font-family:"Noto Sans KR",sans-serif;position:relative}
.strip{position:absolute;top:${top}mm;width:90mm;height:150mm}
.pn{position:absolute;left:0;width:90mm;height:50mm}.p1{top:0;transform:rotate(180deg)}.p2{top:50mm}.p3{top:100mm;display:flex;align-items:center;justify-content:center;color:#c2bdcd;font-size:2.4mm;letter-spacing:.2em;border:.2mm dashed #e2dfe8}
.face{position:relative;width:100%;height:100%;background:#0e0d12;color:#f4f2ee;overflow:hidden;padding:5.5mm 6mm}
.glow{position:absolute;width:70mm;height:70mm;border-radius:50%;right:-28mm;top:-40mm;background:radial-gradient(circle,rgba(124,92,255,.42),rgba(124,92,255,0) 62%)}
.big{position:absolute;right:-2mm;bottom:-5mm;font-family:Montserrat;font-style:italic;font-weight:800;font-size:22mm;letter-spacing:-.04em;line-height:1;color:transparent;-webkit-text-stroke:.2mm rgba(185,166,255,.28)}
.top{position:relative;display:flex;align-items:center;justify-content:space-between}.top img{height:5.6mm}.top span{font-weight:700;font-size:2.5mm;color:#b9a6ff;letter-spacing:.08em}
.bank{position:relative;margin-top:5mm;display:flex;align-items:center;gap:1.6mm;font-weight:900;font-size:3.9mm}.bank b{font-family:Montserrat;font-weight:800;font-size:2.2mm;color:#0e0d12;background:#f5be46;border-radius:.8mm;padding:.35mm 1.1mm}
.no{position:relative;margin-top:1.2mm;font-family:Montserrat;font-weight:800;font-size:6.5mm;line-height:1.05;white-space:nowrap;font-variant-numeric:tabular-nums}
.who{position:relative;margin-top:2.2mm;font-weight:500;font-size:2.6mm;color:#c3bfcc}.who b{font-weight:900;color:#f4f2ee}
.fold{position:absolute;left:-2.5mm;width:95mm;height:0;border-top:.2mm dashed #b9b4c6;z-index:-1}
.cv{position:absolute;width:0;height:5mm;border-left:.2mm solid #555}.ch{position:absolute;height:0;width:5mm;border-top:.2mm solid #555}
.guide{position:absolute;left:7.5mm;right:7.5mm;bottom:12mm;display:flex;justify-content:space-between;font-size:3mm;color:#8f8a9c}
</style></head><body>${xs.map(strip).join('')}${crop}
<div class="guide"><span>✂ 바깥 선대로 잘라 주세요 (한 개 = 9 × 15cm)</span><span>점선 두 곳 접기 → 삼각으로 세우고 맨 아래 칸을 테이프로</span></div>
</body></html>`;
(async () => {
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 2 });
  await p.setContent(html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  await p.pdf({ path: path.join(__dirname, 'tent-card-print.pdf'), width: '297mm', height: '210mm', printBackground: true });
  await p.screenshot({ path: path.join(__dirname, 'card-preview.png') });
  const el = await p.$('.strip .p2 .face'); await el.screenshot({ path: path.join(__dirname, 'card-face.png') });
  await b.close(); console.log('ok');
})();
