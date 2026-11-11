// 계좌번호 삼각 POP (A4 가로, 3단으로 접기) → tent-print.pdf, preview.png, face.png
// node content/2026-11-11_account-tent/make.js
const { launch } = require('../../tools/pw.js'); const fs = require('fs'), path = require('path');
const logo = fs.readFileSync(path.join(__dirname, '../../tools/daily-story/raw-logo.png')).toString('base64');
const face = `<div class="face"><div class="glow"></div><div class="big">RAW</div>
  <div class="l"><img src="data:image/png;base64,${logo}"><span>SUWON</span></div><div class="bar"></div>
  <div class="r"><div class="k">계좌 이체 안내 <em>BANK TRANSFER</em></div>
    <div class="bank"><b>KB</b>국민은행</div><div class="no">529437-01-019625</div>
    <div class="who">예금주 <b>이선우</b> (로우댄스수원점학원)</div></div></div>`;
const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,600;0,700;0,800;1,800&family=Noto+Sans+KR:wght@500;700;900&display=swap" rel="stylesheet">
<style>@page{size:297mm 210mm;margin:0}*{margin:0;padding:0;box-sizing:border-box}
body{width:297mm;height:210mm;background:#fff;font-family:"Noto Sans KR",sans-serif;position:relative}
.p{position:absolute;left:0;width:297mm;height:70mm;padding:4mm}.p1{top:0;transform:rotate(180deg)}.p2{top:70mm}.p3{top:140mm;display:flex;align-items:center;justify-content:center;color:#b5b0c2;font-size:3.2mm;letter-spacing:.3em}
.face{position:relative;width:100%;height:100%;border-radius:4mm;background:#0e0d12;color:#f4f2ee;overflow:hidden;display:flex;align-items:center;padding:0 14mm}
.glow{position:absolute;width:150mm;height:150mm;border-radius:50%;right:-60mm;top:-85mm;background:radial-gradient(circle,rgba(124,92,255,.38),rgba(124,92,255,0) 62%)}
.big{position:absolute;right:-4mm;bottom:-9mm;font-family:Montserrat;font-style:italic;font-weight:800;font-size:46mm;letter-spacing:-.04em;line-height:1;color:transparent;-webkit-text-stroke:.3mm rgba(185,166,255,.30)}
.l{position:relative;display:flex;flex-direction:column;align-items:center;gap:2mm;width:46mm}.l img{width:36mm}.l span{font-family:Montserrat;font-weight:700;font-size:2.6mm;letter-spacing:.6em;margin-right:-.6em;color:#b9a6ff}
.bar{position:relative;width:.35mm;height:36mm;background:rgba(185,166,255,.35);margin:0 11mm 0 6mm}
.r{position:relative}
.k{font-weight:700;font-size:3.6mm;color:#b9a6ff;letter-spacing:.06em}.k em{font-style:normal;font-family:Montserrat;font-weight:700;font-size:2.6mm;letter-spacing:.34em;color:#8f8a9c;margin-left:3mm}
.bank{margin-top:3mm;display:flex;align-items:center;gap:2.5mm;font-weight:900;font-size:6.4mm}.bank b{font-family:Montserrat;font-weight:800;font-size:3.4mm;color:#0e0d12;background:#f5be46;border-radius:1.2mm;padding:.6mm 1.6mm}
.no{margin-top:1.5mm;font-family:Montserrat;font-weight:800;font-size:12.2mm;letter-spacing:.02em;line-height:1.05;font-variant-numeric:tabular-nums;white-space:nowrap}
.who{margin-top:2.6mm;font-weight:500;font-size:4.2mm;color:#c3bfcc}.who b{font-weight:900;color:#f4f2ee}
.tick{position:absolute;width:6mm;height:0;border-top:.25mm dashed #9a95a8}.tick.a{top:70mm}.tick.b{top:140mm}.L{left:0}.R{right:0}
</style></head><body>
<div class="p p1">${face}</div><div class="p p2">${face}</div><div class="p p3">✂ 점선 두 곳을 접어 삼각으로 세우고, 이 칸을 바닥에 테이프로 붙여 주세요</div>
<div class="tick a L"></div><div class="tick a R"></div><div class="tick b L"></div><div class="tick b R"></div>
</body></html>`;
(async () => {
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 2 });
  await p.setContent(html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  await p.pdf({ path: path.join(__dirname, 'tent-print.pdf'), width: '297mm', height: '210mm', printBackground: true });
  await p.screenshot({ path: path.join(__dirname, 'preview.png') });
  const el = await p.$('.p2 .face'); await el.screenshot({ path: path.join(__dirname, 'face.png') });
  await b.close(); console.log('ok');
})();
