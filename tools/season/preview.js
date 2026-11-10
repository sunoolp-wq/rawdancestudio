// 예시 데이터로 태블릿 화면 미리보기 (전문반 10명, 지어낸 이름)
// node tools/season/preview.js → content/2026-11-10_motivation-ideas/tablet-*.png
const { launch } = require('../pw.js'); const path = require('path');
const NOW = '2026-12-04 18:42:00';
const names = ['김서윤', '이하은', '박지우', '최민서', '정예린', '강다은', '조수아', '윤채원', '장하린', '임지아'];
const stu = [['이름', '비밀번호', '보호권']].concat(names.map((n, i) => [n, '', i === 4 ? '2026-11-20' : '']));
let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const log = [['시각', '이름', '종류']]; const add = (d, t, n, k) => log.push([`${d} ${t}:00`, n, k]);
const days = []; for (let d = new Date('2026-11-13T00:00:00'); d <= new Date('2026-12-04T00:00:00'); d.setDate(d.getDate() + 1)) if (d.getDay() >= 1 && d.getDay() <= 5) days.push(d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'));
const missP = [0, 0, 0.1, 0, 0.5, 0.3, 0, 0.6, 0.2, 0];
names.forEach((n, i) => days.forEach(d => {
  const fri = new Date(d + 'T00:00:00').getDay() === 5, lazy = missP[i];
  if (fri && d < '2026-12-04') { if (!(i === 4 && d === '2026-11-20') && rnd() > lazy) add(d, '18:2' + (i % 10), n, '수업 출석'); }
  if (!fri && rnd() < 0.4 - lazy * 0.3) add(d, '17:1' + (i % 10), n, '수업 출석');
  if (rnd() < 0.45 - lazy * 0.4) { add(d, '16:5' + (i % 10), n, '연습 시작'); log.push([`${d} ${rnd() < 0.8 ? '17:4' : '17:0'}${i % 10}:00`, n, '연습 끝', rnd() < 0.25 ? '월말평가 준비' : '개인연습']); }
  if (rnd() < 0.55 - lazy * 0.5) log.push([`${d} 22:10:00`, n, '운동 완료', d]);
  if (rnd() < 0.5 - lazy * 0.5) log.push([`${d} 22:30:00`, n, '연습일지', d]);
}));
['김서윤', '박지우', '임지아'].forEach((n, i) => add('2026-12-04', '18:0' + i, n, '연습 시작'));
['이하은', '최민서'].forEach(n => add('2026-12-04', '18:25', n, '수업 출석'));
const cfg = [['항목','값'],['시즌 이름','RAW SEASON 1'],['시즌 시작','2026-11-13'],['시즌 끝','2026-12-25'],['수업 점수 (수업마다, 하루 3회까지)',10],['전문반 고정수업 점수',20],['운동 루틴 점수 (하루 1회)',10],['연습일지 점수 (하루 1회)',10],['개인연습 점수 (하루 1회)',10],['연습 인정 최소 분',30],['보호권 (시즌당)',1],['고정수업 요일 (0=일 … 5=금)',5],['고정수업 시간','18:30']];
const sample = { stu, log, cfg, now: NOW };
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
