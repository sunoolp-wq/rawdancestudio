/**
 * RAW SEASON (전문반) — 구글 시트 + 학원 태블릿 한 대
 *  - 태블릿 화면 = 순위표 (🔥 금요일 연속 출석·점수·지금 연습실·포폴 영상 자격)
 *  - 내 이름 누르기 → 수업 출석 / 연습 시작 / 연습 끝 / 인증 올림 → 비밀번호 4자리 → 시트에 기록
 * 설치: tools/season/README.md
 */
const TAB = { stu: '학생', log: '기록', cfg: '설정' };
const KINDS = ['수업 출석', '연습 시작', '연습 끝', '인증 올림'];

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Board').setTitle('RAW SEASON')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
}

const tz_ = () => SpreadsheetApp.getActive().getSpreadsheetTimeZone();
const fmt_ = (d, f) => Utilities.formatDate(d, tz_(), f || 'yyyy-MM-dd HH:mm:ss');
function read_(name) {
  const sh = SpreadsheetApp.getActive().getSheetByName(name);
  if (!sh) return [];
  return sh.getDataRange().getValues().map(r => r.map(c => c instanceof Date ? fmt_(c) : c));
}

// 태블릿 화면이 1분마다·기록 직후 부름 (비밀번호 열은 보내지 않음)
function getData() {
  return JSON.stringify({ stu: read_(TAB.stu).map(r => [r[0], '', r[2]]), log: read_(TAB.log), cfg: read_(TAB.cfg), now: fmt_(new Date()) });
}

// 태블릿에서 누르면 기록 한 줄
function checkIn(name, pin, kind) {
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    if (KINDS.indexOf(kind) < 0) return { ok: false, msg: '알 수 없는 버튼이에요' };
    const row = read_(TAB.stu).slice(1).find(r => String(r[0]).trim() === name);
    if (!row) return { ok: false, msg: '명단에 없는 이름이에요' };
    if (String(row[1]).trim().padStart(4, '0') !== String(pin).trim().padStart(4, '0')) return { ok: false, msg: '비밀번호가 달라요' };
    const now = new Date(), today = fmt_(now, 'yyyy-MM-dd');
    const mine = read_(TAB.log).slice(1).filter(r => String(r[1]).trim() === name && String(r[0]).slice(0, 10) === today).map(r => String(r[2]).trim());
    const last = k => mine.lastIndexOf(k);
    if (kind === '수업 출석' && mine.includes('수업 출석')) return { ok: false, msg: '오늘 수업 출석은 이미 했어요' };
    if (kind === '인증 올림' && mine.includes('인증 올림')) return { ok: false, msg: '오늘 인증은 이미 올렸어요' };
    if (kind === '연습 시작' && last('연습 시작') > last('연습 끝')) return { ok: false, msg: '이미 연습 중이에요. 끝날 때 [연습 끝]을 눌러요' };
    if (kind === '연습 끝' && last('연습 시작') <= last('연습 끝')) return { ok: false, msg: '[연습 시작]을 먼저 눌러야 해요' };
    SpreadsheetApp.getActive().getSheetByName(TAB.log).appendRow([fmt_(now), name, kind]);
    let msg = '';
    if (kind === '연습 끝') {
      const st = read_(TAB.log).slice(1).filter(r => String(r[1]).trim() === name && String(r[2]).trim() === '연습 시작' && String(r[0]).slice(0, 10) === today).pop();
      const P = x => Date.parse(String(x).replace(' ', 'T')); // 둘 다 시트 시간대 글자로 비교 (스크립트 시간대와 무관)
      const min = Math.round((P(fmt_(now)) - P(st[0])) / 60000);
      msg = `오늘 연습 ${min}분` + (min >= 30 ? ' 🔥 인정!' : ' (30분부터 인정)');
    }
    return { ok: true, name, kind, time: fmt_(now, 'HH:mm'), msg };
  } finally { lock.releaseLock(); }
}

// 처음 한 번: 탭 3개 만들기 (이미 있으면 건드리지 않음)
function setup() {
  const ss = SpreadsheetApp.getActive();
  if (ss.getSpreadsheetTimeZone() !== 'Asia/Seoul') ss.setSpreadsheetTimeZone('Asia/Seoul');
  if (!ss.getSheetByName(TAB.cfg)) {
    const c = ss.insertSheet(TAB.cfg);
    c.getRange(1, 1, 11, 2).setValues([
      ['항목', '값'],
      ['시즌 이름', 'RAW SEASON 1'],
      ['시즌 시작', '2026-11-13'],
      ['시즌 끝', '2026-12-25'],
      ['수업 출석 점수 (하루 1회)', 10],
      ['연습실 점수 (하루 1회)', 10],
      ['연습 인정 최소 분', 30],
      ['인증 영상 점수 (하루 1회)', 5],
      ['보호권 (시즌당)', 1],
      ['고정수업 요일 (0=일 … 5=금)', 5],
      ['고정수업 시간', '18:30'],
    ]);
    c.getRange('A:A').setNumberFormat('@'); c.getRange('B3:B4').setNumberFormat('@');
    c.setColumnWidth(1, 260).getRange('A1:B1').setFontWeight('bold');
  }
  if (!ss.getSheetByName(TAB.stu)) {
    const s = ss.insertSheet(TAB.stu);
    s.getRange(1, 1, 1, 3).setValues([['이름', '비밀번호 4자리', '보호권 쓴 금요일 (보호자 연락 확인 후 원장님이 입력)']]).setFontWeight('bold');
    s.getRange('B:B').setNumberFormat('@'); s.getRange('C:C').setNumberFormat('@');
    s.setColumnWidth(3, 380); s.setFrozenRows(1);
  }
  if (!ss.getSheetByName(TAB.log)) {
    const l = ss.insertSheet(TAB.log);
    l.getRange(1, 1, 1, 3).setValues([['시각', '이름', '종류']]).setFontWeight('bold');
    l.getRange('A:A').setNumberFormat('@'); l.setFrozenRows(1);
  }
}
