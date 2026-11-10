/**
 * RAW SEASON (전문반) — 구글 시트 + 학원 태블릿 한 대
 *  - 태블릿 화면 = 순위표 (🔥 금요일 연속 출석·점수·지금 연습 중·포폴 영상 자격)
 *  - 내 이름 → 수업 출석 / 연습 시작·끝 / 운동 완료 / 연습일지 → 비밀번호 4자리 → [기록] 탭에 한 줄
 *  - 운동·연습일지는 집에서 해도 됨 → 오늘/어제 골라 체크, 증거는 단톡방 (원장님 확인)
 * 점수 (2026-11-10 원장님): 수업마다 10P · 전문반 고정수업 20P · 운동 루틴 10P · 연습일지 10P · 개인연습 10P (월말평가 준비는 0P, 기록만)
 * 설치: tools/season/README.md
 */
const TAB = { stu: '학생', log: '기록', cfg: '설정', tt: '시간표' };
// [시간표] 탭 처음 내용 = 2026년 11월 시간표 (tools/daily-story/schedule-2026-11.json). 시간표가 바뀌면 탭에서 고치면 됨
const TIMETABLE = [["월", "16:00", "17:00", "유아 K-POP", "YUNI", "A"], ["월", "17:00", "18:00", "키즈 K-POP", "YUNI", "A"], ["월", "18:00", "19:10", "취미 K-POP", "YUNI", "B"], ["월", "19:30", "20:30", "성인 K-POP", "YUNI", "B"], ["월", "19:40", "20:50", "HEELSCHOREO", "HEEONE", "A"], ["월", "20:50", "22:00", "CHOREO", "RAEKU", "A"], ["화", "16:00", "17:00", "유아 K-POP", "MINKYUNG", "A"], ["화", "17:00", "18:00", "키즈 K-POP", "MINKYUNG", "A"], ["화", "18:00", "19:10", "취미 K-POP", "MINKYUNG", "B"], ["화", "18:30", "19:40", "BASIC", "GAON", "A"], ["화", "19:40", "20:50", "GIRLISH", "ARIN", "A"], ["수", "16:00", "17:00", "유아 K-POP", "YUNI", "A"], ["수", "17:00", "18:00", "키즈 K-POP", "YUNI", "A"], ["수", "18:00", "19:10", "취미 K-POP", "YUNI", "B"], ["수", "19:30", "20:30", "성인 K-POP", "YUNI", "B"], ["수", "19:40", "20:50", "WAACKING", "J", "A"], ["수", "20:50", "22:00", "JAZZ", "KIRY", "A"], ["목", "16:00", "17:00", "유아 K-POP", "MINKYUNG", "A"], ["목", "17:00", "18:00", "키즈 K-POP", "MINKYUNG", "A"], ["목", "18:00", "19:10", "취미 K-POP", "MINKYUNG", "B"], ["목", "18:30", "19:40", "BASIC", "GAON", "A"], ["목", "19:40", "20:50", "HIP HOP", "NOFF", "A"], ["목", "20:50", "22:00", "CHOREO", "HWAN.U", "A"], ["금", "18:30", "20:00", "PRO 전문반", "YELLS", "A"], ["금", "20:10", "21:20", "GIRLS HIPHOP", "MINKYUNG", "A"], ["토", "13:00", "14:00", "유아 K-POP", "REGINA", "A"], ["토", "14:00", "15:00", "키즈 K-POP", "REGINA", "A"], ["토", "15:00", "16:10", "취미 K-POP", "REGINA", "A"]];
// 처음 setup 때 [학생] 탭에 넣을 명단 [이름, 상태]. 상태에 '휴원'이 들어가면 화면에 안 나오고 체크도 안 됨
const ROSTER = [];
// 처음 setup 때 [설정] 탭에 넣을 시즌 (나중엔 [설정] 탭에서 고침)
const SEASON = { name: 'RAW SEASON 1', start: '2026-11-13', end: '2026-12-25' };
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
const DAYS_ = ['일', '월', '화', '수', '목', '금', '토'];
// 출석 포인트 제외 수업: [설정] '출석 제외 수업'에 쉼표로 (기본 K-POP → 유아·키즈·취미·성인 K-POP 제외, 원장님 2026-11-10)
const skip_ = (name, skip) => String(skip || '').split(',').map(x => x.trim()).filter(Boolean).some(x => String(name).indexOf(x) >= 0);
const hm_ = v => { const m = /(\d{1,2}):(\d{2})/.exec(String(v)); return m ? (+m[1]) * 60 + (+m[2]) : null; };
// 그날 수업 시간 [{s, e, label}] (분). 연습은 수업 시간에 시작 못 하고, 연습 시간에서 수업 시간은 뺌 (원장님 2026-11-10)
function classesOn_(tt, dateS, skip) {
  const day = DAYS_[new Date(dateS + 'T00:00:00').getDay()];
  return tt.slice(1).filter(r => String(r[0]).trim().charAt(0) === day && hm_(r[1]) != null && hm_(r[2]) != null && !skip_(r[3], skip))
    .map(r => ({ s: hm_(r[1]), e: hm_(r[2]), label: `${String(r[1]).trim()}~${String(r[2]).trim()} ${String(r[3]).trim()}` }));
}
// 연습 분 = 시작~끝에서 수업 시간과 겹치는 분을 뺀 것 (같은 날)
function pracMin_(tt, startS, endS, skip) {
  const m = x => (+x.slice(11, 13)) * 60 + (+x.slice(14, 16)), a = m(startS), b = m(endS);
  const over = classesOn_(tt, startS.slice(0, 10), skip).reduce((t, c) => t + Math.max(0, Math.min(b, c.e) - Math.max(a, c.s)), 0);
  return { total: b - a, over, min: b - a - over };
}
// 지금 출석할 수 있는 수업 (시작 before분 전 ~ 시작 after분 후) + 오늘 다음 수업. 태블릿 화면(Board.html)에도 같은 계산이 있음
function classesAt_(tt, nowS, before, after, skip) {
  const day = DAYS_[new Date(nowS.slice(0, 10) + 'T00:00:00').getDay()], mins = (+nowS.slice(11, 13)) * 60 + (+nowS.slice(14, 16));
  const list = tt.slice(1).filter(r => String(r[0]).trim().charAt(0) === day && hm_(r[1]) != null && !skip_(r[3], skip)).map(r => {
    const st = hm_(r[1]); return { start: st, label: `${String(Math.floor(st / 60)).padStart(2, '0')}:${String(st % 60).padStart(2, '0')} ${String(r[3]).trim()}`, teacher: String(r[4] || '').trim() };
  });
  return { open: list.filter(c => mins >= c.start - before && mins <= c.start + after), next: list.filter(c => c.start - before > mins).sort((a, b) => a.start - b.start)[0] || null };
}
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
  return JSON.stringify({ stu, log: read_(TAB.log), cfg: read_(TAB.cfg), tt: read_(TAB.tt), now: fmt_(new Date()) });
}

// 태블릿에서 누르면 기록 한 줄. note = 수업 출석: 'HH:MM 수업명' / 연습 끝: '개인연습' | '월말평가 준비' / 운동 완료·연습일지: 'yyyy-MM-dd' (오늘 또는 어제)
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
      .map(r => ({ t: String(r[0]), k: String(r[2]).trim(), note: String(r[3] || '').trim() }));
    const lastT = k => { const a = mine.filter(x => x.k === k); return a.length ? a[a.length - 1].t : ''; };
    const openS = (a, b) => lastT(a) > lastT(b); // 시작만 있고 끝이 없음
    if (kind === '수업 출석') {
      const bf = g('출석: 시작 몇 분 전부터'), af = g('출석: 시작 후 몇 분까지');
      const sk = g('출석 제외 수업'), w = classesAt_(read_(TAB.tt), nowS, bf === '' ? 20 : +bf, af === '' ? 15 : +af, sk === '' ? 'K-POP' : sk);
      if (!w.open.length) return { ok: false, msg: '지금은 수업 출석 시간이 아니에요' + (w.next ? ` · 다음 ${w.next.label}` : '') };
      const c = w.open.find(x => x.label === note) || (w.open.length === 1 ? w.open[0] : null);
      if (!c) return { ok: false, msg: '어느 수업인지 골라 주세요' };
      note = c.label;
      const cls = mine.filter(x => x.k === '수업 출석');
      if (cls.some(x => x.note === note)) return { ok: false, msg: `${note} 출석은 이미 했어요` };
      if (cls.length >= 3) return { ok: false, msg: '수업 출석은 하루 3번까지예요' };
    }
    if (DAILY.indexOf(kind) >= 0) {
      const y = new Date(now.getTime() - 864e5), yest = fmt_(y, 'yyyy-MM-dd');
      if (note !== today && note !== yest) return { ok: false, msg: '오늘이나 어제만 고를 수 있어요' };
      const dup = read_(TAB.log).slice(1).some(r => String(r[1]).trim() === name && String(r[2]).trim() === kind && String(r[3]).slice(0, 10) === note);
      if (dup) return { ok: false, msg: `${note === today ? '오늘' : '어제'} ${kind}는 이미 체크했어요` };
    }
    const skipS = g('출석 제외 수업') === '' ? 'K-POP' : g('출석 제외 수업');
    if (kind === '연습 시작' && openS('연습 시작', '연습 끝')) return { ok: false, msg: '이미 연습 중이에요. 끝나면 [연습 끝]' };
    if (kind === '연습 시작') {
      const mm = (+nowS.slice(11, 13)) * 60 + (+nowS.slice(14, 16)), c = classesOn_(read_(TAB.tt), today, skipS).find(c => mm >= c.s && mm < c.e);
      if (c) return { ok: false, msg: `수업 시간에는 연습을 시작할 수 없어요 · ${c.label}` };
    }
    if (kind === '연습 끝' && !openS('연습 시작', '연습 끝')) return { ok: false, msg: '[연습 시작]을 먼저 눌러야 해요' };
    if (kind === '연습 끝' && PRAC_TYPES.indexOf(note) < 0) return { ok: false, msg: '개인연습인지 월말평가 준비인지 골라 주세요' };
    SpreadsheetApp.getActive().getSheetByName(TAB.log).appendRow([nowS, name, kind, note || '']);
    let msg = '';
    if (kind === '연습 끝') {
      const pm = pracMin_(read_(TAB.tt), lastT('연습 시작'), nowS, skipS), min = pm.min, need = +g('연습 인정 최소 분') || 0;
      const ex = pm.over ? ` (수업 시간 ${pm.over}분 제외)` : '';
      msg = note === '월말평가 준비' ? `월말평가 준비 ${min}분 기록${ex} · 점수 없음` : `개인연습 ${min}분${ex}` + (min >= need ? ' 🔥 인정!' : ` · ${need}분부터 인정`);
    }
    if (DAILY.indexOf(kind) >= 0) msg = `${note === today ? '오늘' : '어제'} ${kind} ✓ · 단톡방에 인증 올려 주세요`;
    if (kind === '수업 출석') msg = note;
    return { ok: true, name, kind, time: nowS.slice(11, 16), msg };
  } finally { lock.releaseLock(); }
}

// 처음 한 번: 탭 4개 만들기. 이미 설치했으면 다시 실행해도 됨 (없는 탭·설정 항목만 추가, 기존 내용은 그대로)
function setup() {
  const ss = SpreadsheetApp.getActive();
  if (ss.getSpreadsheetTimeZone() !== 'Asia/Seoul') ss.setSpreadsheetTimeZone('Asia/Seoul');
  const rows = [
    ['항목', '값'],
    ['시즌 이름', SEASON.name],
    ['시즌 시작', SEASON.start],
    ['시즌 끝', SEASON.end],
    ['수업 점수 (수업마다, 하루 3회까지)', 10],
    ['전문반 고정수업 점수', 20],
    ['운동 루틴 점수 (하루 1회)', 10],
    ['연습일지 점수 (하루 1회)', 10],
    ['개인연습 점수 (하루 1회)', 10],
    ['연습 인정 최소 분', 30],
    ['보호권 (시즌당)', 1],
    ['고정수업 요일 (0=일 … 5=금)', 5],
    ['고정수업 시간', '18:30'],
    ['출석: 시작 몇 분 전부터', 20],
    ['출석: 시작 후 몇 분까지', 15],
    ['출석 제외 수업 (이름에 들어가면 제외, 쉼표로)', 'K-POP'],
  ];
  let c = ss.getSheetByName(TAB.cfg);
  if (!c) {
    c = ss.insertSheet(TAB.cfg);
    c.getRange(1, 1, rows.length, 2).setNumberFormat('@').setValues(rows.map(r => r.map(String)));
    c.setColumnWidth(1, 280).setColumnWidth(2, 420).getRange('A1:B1').setFontWeight('bold');
  } else { // 이미 있으면 없는 항목만 아래에 추가 (원장님이 고친 값은 그대로)
    const have = c.getDataRange().getValues().map(r => String(r[0]).trim());
    rows.filter(r => have.indexOf(r[0]) < 0).forEach(r => c.appendRow([r[0], String(r[1])]));
  }
  if (!ss.getSheetByName(TAB.tt)) {
    const t = ss.insertSheet(TAB.tt);
    t.getRange(1, 1, TIMETABLE.length + 1, 6).setNumberFormat('@')
      .setValues([['요일', '시작', '끝', '수업', '강사', '홀']].concat(TIMETABLE));
    t.getRange('A1:F1').setFontWeight('bold'); t.setFrozenRows(1); t.setColumnWidth(4, 160);
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
