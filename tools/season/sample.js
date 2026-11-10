// 예시 데이터 (지어낸 전문반 10명, 2026-12-04 금 18:42 가정) — preview.js·데모 링크 공용
const NOW = '2026-12-04 18:42:00';
const names = ['김서윤', '이하은', '박지우', '최민서', '정예린', '강다은', '조수아', '윤채원', '장하린', '임지아'];
const stu = [['이름', '비밀번호', '보호권']].concat(names.map((n, i) => [n, '', i === 4 ? '2026-11-20' : '']));
let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const log = [['시각', '이름', '종류', '메모']]; const add = (d, t, n, k, note = '') => log.push([`${d} ${t}:00`, n, k, note]);
const sch = require('../daily-story/schedule-2026-11.json'), KR = { MON: '월', TUE: '화', WED: '수', THU: '목', FRI: '금', SAT: '토' };
const tt = [['요일', '시작', '끝', '수업', '강사', '홀']].concat(Object.entries(sch.days).flatMap(([k, v]) => v.map(c => [KR[k], c.start, c.end, c.name, c.teacher, c.hall])));
const days = []; for (let d = new Date('2026-11-13T00:00:00'); d <= new Date('2026-12-04T00:00:00'); d.setDate(d.getDate() + 1)) if (d.getDay() >= 1 && d.getDay() <= 5) days.push(d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'));
const missP = [0, 0, 0.1, 0, 0.5, 0.3, 0, 0.6, 0.2, 0];
names.forEach((n, i) => days.forEach(d => {
  const fri = new Date(d + 'T00:00:00').getDay() === 5, lazy = missP[i];
  if (fri && d < '2026-12-04') { if (!(i === 4 && d === '2026-11-20') && rnd() > lazy) add(d, '18:2' + (i % 10), n, '수업 출석', '18:30 PRO 전문반'); }
  if (!fri && rnd() < 0.4 - lazy * 0.3) add(d, '18:1' + (i % 10), n, '수업 출석', '18:30 BASIC');
  if (d >= NOW.slice(0, 10)) return;
  if (rnd() < 0.45 - lazy * 0.4) { add(d, '16:5' + (i % 10), n, '연습 시작'); log.push([`${d} ${rnd() < 0.8 ? '17:4' : '17:0'}${i % 10}:00`, n, '연습 끝', rnd() < 0.25 ? '월말평가 준비' : '개인연습']); }
  if (rnd() < 0.55 - lazy * 0.5) log.push([`${d} 22:10:00`, n, '운동 완료', d]);
  if (rnd() < 0.5 - lazy * 0.5) log.push([`${d} 22:30:00`, n, '연습일지', d]);
}));
['김서윤', '박지우', '임지아'].forEach((n, i) => add('2026-12-04', '18:0' + i, n, '연습 시작'));
['이하은', '최민서'].forEach(n => add('2026-12-04', '18:25', n, '수업 출석', '18:30 PRO 전문반'));
const cfg = [['항목','값'],['시즌 이름','RAW SEASON 1'],['시즌 시작','2026-11-13'],['시즌 끝','2026-12-25'],['수업 점수 (수업마다, 하루 3회까지)',10],['전문반 고정수업 점수',20],['운동 루틴 점수 (하루 1회)',10],['연습일지 점수 (하루 1회)',10],['개인연습 점수 (하루 1회)',10],['연습 인정 최소 분',30],['보호권 (시즌당)',1],['고정수업 요일 (0=일 … 5=금)',5],['고정수업 시간','18:30']];
const sample = { stu, log, cfg, tt, now: NOW };
module.exports = sample;
