// 예시 데이터로 태블릿 화면 미리보기 (전문반 10명, 지어낸 이름)
// node tools/season/preview.js → content/2026-11-10_motivation-ideas/tablet-*.png
const { launch } = require('../pw.js'); const path = require('path');
const sample = require('./sample.js');
(async () => {
  const b = await launch(); const out = path.join(__dirname, '../../content/2026-11-10_motivation-ideas');
  const p = await b.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 2 });
  await p.addInitScript(s => { window.MOCK = { get: cb => cb(JSON.parse(JSON.stringify(s))),
    checkIn: (n, pin, k, note, cb) => setTimeout(() => cb(pin === '1234' ? { ok: true, name: n, kind: k, time: '18:44', msg: k === '연습 끝' ? '개인연습 41분 🔥 인정!' : (k === '운동 완료' || k === '연습일지') ? '오늘 ' + k + ' ✓ · 단톡방에 인증 올려 주세요' : '' } : { ok: false, msg: '비밀번호가 달라요' }), 200) }; }, sample);
  await p.goto('file://' + path.join(__dirname, 'Board.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1200);
  await p.screenshot({ path: path.join(out, 'tablet-1-home.png') });
  await p.click('.row[data-i="2"]'); await p.waitForTimeout(300); await p.screenshot({ path: path.join(out, 'tablet-2-choose.png') });
  await p.click('[data-k="연습 끝"]'); await p.waitForTimeout(200); await p.screenshot({ path: path.join(out, 'tablet-2b-type.png') });
  await p.click('[data-v="개인연습"]'); for (const x of ['1', '2']) await p.click(`[data-p="${x}"]`); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, 'tablet-3-pin.png') });
  for (const x of ['3', '4']) await p.click(`[data-p="${x}"]`); await p.waitForTimeout(600);
  await p.screenshot({ path: path.join(out, 'tablet-4-done.png') });
  await b.close(); console.log('ok');
})();
