// 그날 수업 순서 (시간표 + extra.json 대강·팝업·휴강 반영) — 스토리 예약용
// 사용: node tools/daily-story/plan.js 2026-11-23   → 00:00 시간표 스토리, 00:01부터 수업 순서대로 한 줄씩
const fs = require('fs'), path = require('path');
const dateStr = process.argv[2];
if (!dateStr) { console.error('날짜를 넣어 주세요: node tools/daily-story/plan.js 2026-11-23'); process.exit(1); }
const [Y, M, D] = dateStr.split('-').map(Number);
const DOW = ['SUN','MON','TUE','WED','THU','FRI','SAT'][new Date(Date.UTC(Y, M - 1, D)).getUTCDay()];
const sp = path.join(__dirname, `schedule-${Y}-${String(M).padStart(2,'0')}.json`);
if (!fs.existsSync(sp)) { console.error(`${Y}-${M}월 시간표 파일이 없어요: ${sp}`); process.exit(1); }
let classes = JSON.parse(fs.readFileSync(sp)).days[DOW] || [];
const ep = path.join(__dirname, 'extra.json');
if (fs.existsSync(ep)) { const ex = JSON.parse(fs.readFileSync(ep))[dateStr]; if (ex) {
  if (ex.replace) classes = classes.map(c => { const r = ex.replace.find(r => r.start === c.start && r.name === c.name); return r ? { ...c, ...r.set } : c; });
  if (ex.remove) classes = classes.filter(c => !ex.remove.some(r => r.start === c.start && r.name === c.name));
  if (ex.add) classes = classes.concat(ex.add);
  classes.sort((a, b) => a.start.localeCompare(b.start)); } }
const story = path.join(__dirname, '../../content', `${dateStr}_daily-story`, 'story.mp4');
console.log(`${dateStr} (${DOW}) 예약 순서`);
console.log(`00:00  시간표 스토리  ${story}`);
classes.forEach((c, i) => console.log(`00:${String(i + 1).padStart(2, '0')}  ${c.start} ${c.name}  T. ${c.teacher || '?'}${c.mark ? '  (' + c.mark + ')' : ''}`));
