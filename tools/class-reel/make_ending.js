// 학원 로고 엔딩 이미지 (세로 1080x1920 / 가로 3840x2160)
const { launch } = require('../pw.js'); const path = require('path');
(async () => {
  const b = await launch();
  for (const [w, h, name, scale] of [[1080, 1920, 'ending-9x16.png', 1], [1920, 1080, 'ending-16x9.png', 2]]) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
    await p.goto('file://' + path.join(__dirname, 'ending.html'));
    await p.addStyleTag({ content: `html,body{width:${w}px;height:${h}px}` + (w > h ? 'img{width:520px}' : '') });
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(__dirname, name) }); await p.close();
  }
  await b.close();
})();
