// 예시 데이터로 랭크보드 미리보기: node tools/season/preview.js [오늘 날짜] → content/2026-11-10_motivation-ideas/rankboard-preview.png
const { launch } = require('../pw.js'); const path = require('path');
const today = process.argv[2] || '2026-12-10';
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const names = ['김서윤','이하은','박지우','최민서','정예린','강다은','조수아','윤채원','장하린','임지아','한소율','오유나','서아린','신예나','권도희','황시은','안지민','송하율','류나연','전가은','홍세아','고은채','문서진','양태리','배리아','백수빈'];
const cls = ['취미 K-POP','성인 K-POP','GIRLISH','HIP HOP','JAZZ','PRO 전문반','BASIC','GIRLS HIPHOP'];
const days = []; for (let d = new Date('2026-11-16T00:00:00'); d <= new Date('2026-12-31T00:00:00'); d.setDate(d.getDate() + 1)) if (d.getDay() >= 1 && d.getDay() <= 5) days.push(new Date(d).toISOString().slice(0, 10));
const fix = s => { const d = new Date(s + 'T00:00:00'); d.setDate(d.getDate()); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
const att = [['이름', '반', ...days.map(fix)]];
names.forEach((n, i) => { const p = 0.1 + rnd() * 0.55; att.push([n, cls[i % cls.length], ...days.map(d => fix(d) <= today && rnd() < p)]); });
const mis = [['날짜', '이름', '미션']]; const ml = ['셀프캠', '셀프캠', '사이퍼 참여', '팝업 참여', '공연·버스킹'];
for (let k = 0; k < 30; k++) { const d = days[Math.floor(rnd() * days.length)]; if (fix(d) <= today) mis.push([fix(d), names[Math.floor(rnd() * names.length)], ml[Math.floor(rnd() * ml.length)]]); }
const cfg = [['항목','값'],['시즌 이름','RAW SEASON 1'],['시즌 시작','2026-11-16'],['시즌 끝','2026-12-31'],['출석 1회 점수',10],['연속 보너스 (2주 연속부터 매주)',5],['CREW 기준 점수',60],['CORE 기준 점수',150],['RAW 기준 점수',250],['미션: 셀프캠',5],['미션: 사이퍼 참여',10],['미션: 팝업 참여',10],['미션: 공연·버스킹',20]];
(async () => {
  const b = await launch(); const out = path.join(__dirname, '../../content/2026-11-10_motivation-ideas');
  for (const [w, h, f] of [[1920, 1080, 'rankboard-preview.png']]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.addInitScript(s => { window.SAMPLE = s; }, { att, mis, cfg, today });
    await p.goto('file://' + path.join(__dirname, 'Board.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1500);
    await p.screenshot({ path: path.join(out, f) });
  }
  await b.close(); console.log('ok');
})();
