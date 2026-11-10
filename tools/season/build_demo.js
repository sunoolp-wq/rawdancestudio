// 아이패드·태블릿에서 눌러 볼 체험판: 진짜 Code.gs를 브라우저 안 가짜 구글 시트 위에서 그대로 돌림 (예시 데이터, 기록 안 남음)
// 학생 비밀번호 1234 · 원장님 비밀번호 0000 · 시계는 금 18:42부터, 누를 때마다 2분(연습 끝은 35분) 흐름
// node tools/season/build_demo.js → content/2026-11-10_motivation-ideas/raw-season-demo.html (Artifact로 공개)
const fs = require('fs'), path = require('path');
const sample = require('./sample.js');
const code = fs.readFileSync(path.join(__dirname, 'Code.gs'), 'utf8');
let h = fs.readFileSync(path.join(__dirname, 'Board.html'), 'utf8');
h = h.replace(/<!doctype html>\s*<html[^>]*>\s*<head>/i, '').replace(/<meta charset="utf-8">/, '').replace(/<meta name="viewport"[^>]*>/, '')
  .replace('<title>RAW SEASON</title>', '<title>RAW SEASON 체험판</title>').replace(/<\/head>\s*<body>/i, '').replace(/<\/body>\s*<\/html>\s*$/i, '');
h = h.replace('html,body{width:100%;height:100%;background:#0e0d12;overflow:hidden}', ':root{color-scheme:dark;padding:0!important}html,body{width:100%;height:100%;background:#0e0d12;overflow:hidden}');
const banner = `<div id="demo" style="position:absolute;left:40px;top:6px;z-index:5;font-family:'Noto Sans KR',sans-serif;font-size:12px;color:#0e0d12;background:#f5be46;border-radius:6px;padding:3px 10px;font-weight:700">체험판 · 예시 학생 · 학생 비번 1234 · 원장님 0000 · 금 18:42부터, 누를 때마다 2분(연습 끝 35분) 흘러요 · 새로고침하면 처음으로</div>`;
h = h.replace('<div class="g" id="g1"></div>', banner + '<div class="g" id="g1"></div>');
const seed = {
  cfg: sample.cfg.concat([['출석: 시작 몇 분 전부터', '20'], ['출석: 시작 후 몇 분까지', '15'], ['지각 출석 점수 (%)', '50'], ['출석 제외 수업', 'K-POP'], ['휴강일', ''], ['원장님 비밀번호', '0000']]),
  tt: sample.tt, stu: [['이름', '비밀번호', '보호권', '상태']].concat(sample.stu.slice(1).map(r => [r[0], '1234', r[2], ''])),
  log: [['시각', '이름', '종류', '메모', '비고']].concat(sample.log.slice(1)), now: sample.now };
const mock = `<script>
(() => {
  // 가짜 구글 시트 (체험판 전용)
  const SEED = ${JSON.stringify(seed).replace(/</g, '\\u003c')};
  const RealDate = Date, BASE = RealDate.parse(SEED.now.replace(' ', 'T') + '+09:00'), T0 = RealDate.now(); let OFF = 0;
  const vnow = () => BASE + OFF + (RealDate.now() - T0); // 체험판 시계: 실제 시간대로 흐르고, 누를 때마다 조금 더 감
  window.Date = class extends RealDate { constructor(...a) { if (!a.length) super(vnow()); else super(...a); } static now() { return vnow(); } };
  const tick = m => { OFF += m * 60000; };
  const sheets = {};
  const mk = (n, rows) => { const v = rows.map(r => r.slice()); const sh = { v,
    getDataRange: () => ({ getValues: () => { const w = Math.max(0, ...v.map(r => r.length)); return v.map(r => Array.from({ length: w }, (_, i) => r[i] === undefined ? '' : r[i])); } }),
    getRange: () => { const o = { setValues: () => o, setValue: () => o, setNumberFormat: () => o, setFontWeight: () => o, setWrap: () => o }; return o; },
    appendRow: r => v.push(r.slice()), clearContents: () => { v.length = 0; }, setColumnWidth: () => sh, setFrozenRows: () => sh, getLastRow: () => v.length }; sheets[n] = sh; };
  mk('설정', SEED.cfg); mk('시간표', SEED.tt); mk('학생', SEED.stu); mk('기록', SEED.log);
  const ss = { getSpreadsheetTimeZone: () => 'Asia/Seoul', getSheetByName: n => sheets[n] || null, insertSheet: n => (mk(n, []), sheets[n]) };
  const SpreadsheetApp = { getActive: () => ss };
  const Utilities = { formatDate: (d, tz, f) => { const k = new RealDate(d.getTime() + 9 * 3600e3), p = n => String(n).padStart(2, '0');
    return f.replace('yyyy', k.getUTCFullYear()).replace('MM', p(k.getUTCMonth() + 1)).replace('dd', p(k.getUTCDate())).replace('HH', p(k.getUTCHours())).replace('mm', p(k.getUTCMinutes())).replace('ss', p(k.getUTCSeconds())); } };
  const cache = {}; const CacheService = { getScriptCache: () => ({ get: k => cache[k] || null, put: (k, v) => cache[k] = v, remove: k => delete cache[k] }) };
  const LockService = { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) };
  const HtmlService = {}, PropertiesService = {}, ScriptApp = {};
  // ↓ 진짜 Code.gs 그대로
  ${code.replace(/<\/script/gi, '<\\/script')}
  window.MOCK = {
    get: cb => setTimeout(() => cb(JSON.parse(getData())), 60),
    checkIn: (n, p, k, note, cb) => setTimeout(() => { tick(k === '연습 끝' ? 35 : 2); cb(checkIn(n, p, k, note)); }, 200)
  };
})();
</script>`;
h = h.replace('<script>\nconst KINDS', mock + '\n<script>\nconst KINDS');
const out = path.join(__dirname, '../../content/2026-11-10_motivation-ideas/raw-season-demo.html');
fs.writeFileSync(out, h); console.log(out, (h.length / 1024).toFixed(0) + 'KB');
