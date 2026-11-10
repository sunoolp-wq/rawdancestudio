/**
 * RAW SEASON (전문반) — 구글 시트 + 학원 태블릿 한 대
 *  - 태블릿 화면 = 순위표 (🔥 금요일 연속 출석·점수·지금 연습 중·포폴 영상 자격)
 *  - 내 이름 → 수업 출석 / 연습 시작·끝 / 운동 완료 / 연습일지 → 비밀번호 4자리 → [기록] 탭에 한 줄
 *  - 운동·연습일지는 집에서 해도 됨 → 오늘/어제 골라 체크, 증거는 단톡방 (원장님 확인)
 * 점수 (2026-11-10 원장님): 수업마다 10P · 전문반 고정수업 20P · 운동 루틴 10P · 연습일지 10P · 개인연습 10P (월말평가 준비는 0P, 기록만)
 * 설치: tools/season/README.md
 */
const TAB = { stu: '학생', log: '기록', cfg: '설정' };
// 처음 setup 때 [학생] 탭에 넣을 명단 [이름, 상태]. 상태에 '휴원'이 들어가면 화면에 안 나오고 체크도 안 됨
const ROSTER = [];
const KINDS = ['수업 출석', '연습 시작', '연습 끝', '운동 완료', '연습일지'];
const DAILY = ['운동 완료', '연습일지']; // 오늘/어제 골라서, 날짜마다 1회
const PRAC_TYPES = ['개인연습', '월말평가 준비'];

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Board').setTitle('RAW SEASON')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
}

const tz_ = () => SpreadsheetApp.getActive().getSpreadsheetTimeZone();
const fmt_ = (d, f) => Utilities.formatDate(d, tz_(), f || 'yyyy-MM-dd HH:mm:ss');
const P_ = x => Date.parse(String(x).replace(' ', 'T')); // 시트 시간대 글자끼리 비교 (스크립트 시간대와 무관)
function read_(name) {
  const sh = SpreadsheetApp.getActive().getSheetByName(name);
  if (!sh) return [];
  return sh.getDataRange().getValues().map(r => r.map(c => c instanceof Date ? fmt_(c) : c));
}
function cfg_() {
  const o = {}; read_(TAB.cfg).slice(1).forEach(r => { if (r[0] !== '') o[String(r[0]).trim()] = r[1]; });
  return k => { const e = Object.entries(o).find(([n]) => n.startsWith(k)); return e ? e[1] : ''; };
}

// 태블릿 화면이 1분마다·기록 직후 부름 (비밀번호 열은 보내지 않음)
function getData() {
  const stu = read_(TAB.stu).filter((r, i) => i === 0 || String(r[3] || '').indexOf('휴원') < 0).map(r => [r[0], '', r[2]]);
  return JSON.stringify({ stu, log: read_(TAB.log), cfg: read_(TAB.cfg), now: fmt_(new Date()) });
}

// 태블릿에서 누르면 기록 한 줄. note = 연습 끝: '개인연습' | '월말평가 준비' / 운동 완료·연습일지: 'yyyy-MM-dd' (오늘 또는 어제)
function checkIn(name, pin, kind, note) {
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    if (KINDS.indexOf(kind) < 0) return { ok: false, msg: '알 수 없는 버튼이에요' };
    const row = read_(TAB.stu).slice(1).find(r => String(r[0]).trim() === name);
    if (!row) return { ok: false, msg: '명단에 없는 이름이에요' };
    if (String(row[3] || '').indexOf('휴원') >= 0) return { ok: false, msg: '휴원 중인 학생이에요' };
    if (String(row[1]).trim().padStart(4, '0') !== String(pin).trim().padStart(4, '0')) return { ok: false, msg: '비밀번호가 달라요' };
    const g = cfg_(), now = new Date(), nowS = fmt_(now), today = nowS.slice(0, 10);
    const mine = read_(TAB.log).slice(1).filter(r => String(r[1]).trim() === name && String(r[0]).slice(0, 10) === today)
      .map(r => ({ t: String(r[0]), k: String(r[2]).trim() }));
    const lastT = k => { const a = mine.filter(x => x.k === k); return a.length ? a[a.length - 1].t : ''; };
    const openS = (a, b) => lastT(a) > lastT(b); // 시작만 있고 끝이 없음
    if (kind === '수업 출석') {
      const cls = mine.filter(x => x.k === '수업 출석');
      if (cls.length >= 3) return { ok: false, msg: '수업 출석은 하루 3번까지예요' };
      if (cls.length && (P_(nowS) - P_(cls[cls.length - 1].t)) / 60000 < 60) return { ok: false, msg: '방금 수업 출석했어요. 다음 수업 때 눌러요' };
    }
    if (DAILY.indexOf(kind) >= 0) {
      const y = new Date(now.getTime() - 864e5), yest = fmt_(y, 'yyyy-MM-dd');
      if (note !== today && note !== yest) return { ok: false, msg: '오늘이나 어제만 고를 수 있어요' };
      const dup = read_(TAB.log).slice(1).some(r => String(r[1]).trim() === name && String(r[2]).trim() === kind && String(r[3]).slice(0, 10) === note);
      if (dup) return { ok: false, msg: `${note === today ? '오늘' : '어제'} ${kind}는 이미 체크했어요` };
    }
    if (kind === '연습 시작' && openS('연습 시작', '연습 끝')) return { ok: false, msg: '이미 연습 중이에요. 끝나면 [연습 끝]' };
    if (kind === '연습 끝' && !openS('연습 시작', '연습 끝')) return { ok: false, msg: '[연습 시작]을 먼저 눌러야 해요' };
    if (kind === '연습 끝' && PRAC_TYPES.indexOf(note) < 0) return { ok: false, msg: '개인연습인지 월말평가 준비인지 골라 주세요' };
    SpreadsheetApp.getActive().getSheetByName(TAB.log).appendRow([nowS, name, kind, kind === '연습 끝' || DAILY.indexOf(kind) >= 0 ? note : '']);
    let msg = '';
    if (kind === '연습 끝') {
      const min = Math.round((P_(nowS) - P_(lastT('연습 시작'))) / 60000), need = +g('연습 인정 최소 분') || 0;
      msg = note === '월말평가 준비' ? `월말평가 준비 ${min}분 기록 (점수 없음)` : `개인연습 ${min}분` + (min >= need ? ' 🔥 인정!' : ` (${need}분부터 인정)`);
    }
    if (DAILY.indexOf(kind) >= 0) msg = `${note === today ? '오늘' : '어제'} ${kind} ✓ · 단톡방에 인증 올려 주세요`;
    return { ok: true, name, kind, time: nowS.slice(11, 16), msg };
  } finally { lock.releaseLock(); }
}

// 처음 한 번: 탭 3개 만들기 (이미 있으면 건드리지 않음)
function setup() {
  const ss = SpreadsheetApp.getActive();
  if (ss.getSpreadsheetTimeZone() !== 'Asia/Seoul') ss.setSpreadsheetTimeZone('Asia/Seoul');
  if (!ss.getSheetByName(TAB.cfg)) {
    const c = ss.insertSheet(TAB.cfg);
    const rows = [
      ['항목', '값'],
      ['시즌 이름', 'RAW SEASON 1'],
      ['시즌 시작', '2026-11-13'],
      ['시즌 끝', '2026-12-25'],
      ['수업 점수 (수업마다, 하루 3회까지)', 10],
      ['전문반 고정수업 점수', 20],
      ['운동 루틴 점수 (하루 1회)', 10],
      ['연습일지 점수 (하루 1회)', 10],
      ['개인연습 점수 (하루 1회)', 10],
      ['연습 인정 최소 분', 30],
      ['보호권 (시즌당)', 1],
      ['고정수업 요일 (0=일 … 5=금)', 5],
      ['고정수업 시간', '18:30'],
    ];
    c.getRange(1, 1, rows.length, 2).setValues(rows);
    c.getRange('B3:B4').setNumberFormat('@');
    c.setColumnWidth(1, 280).setColumnWidth(2, 420).getRange('A1:B1').setFontWeight('bold');
  }
  if (!ss.getSheetByName(TAB.stu)) {
    const s = ss.insertSheet(TAB.stu);
    s.getRange(1, 1, 1, 4).setValues([['이름', '비밀번호 4자리', '보호권 쓴 금요일 (보호자 연락 확인 후 원장님이 입력)', '상태 (휴원이면 화면에 안 나옴)']]).setFontWeight('bold');
    s.getRange('B:B').setNumberFormat('@'); s.getRange('C:C').setNumberFormat('@');
    s.setColumnWidth(3, 380).setColumnWidth(4, 220); s.setFrozenRows(1);
    // 명단 + 비밀번호 4자리 자동 생성 (원장님이 학생마다 따로 알려 주고, 바꿔도 됨)
    const used = {};
    const pin = () => { let p; do { p = String(1000 + Math.floor(Math.random() * 9000)); } while (used[p]); used[p] = 1; return p; };
    if (ROSTER.length) s.getRange(2, 1, ROSTER.length, 4).setValues(ROSTER.map(([n, st]) => [n, pin(), '', st || '']));
  }
  if (!ss.getSheetByName(TAB.log)) {
    const l = ss.insertSheet(TAB.log);
    l.getRange(1, 1, 1, 4).setValues([['시각', '이름', '종류', '연습 종류 / 해당 날짜']]).setFontWeight('bold');
    l.getRange('A:A').setNumberFormat('@'); l.getRange('D:D').setNumberFormat('@'); l.setFrozenRows(1);
  }
}
