/**
 * RAW SEASON 랭크보드 — 구글 시트에 붙이는 코드 (확장 프로그램 → Apps Script)
 * 1) 이 파일 내용을 Code.gs에, Board.html 내용을 새 HTML 파일 "Board"에 붙여 넣기
 * 2) 위쪽 함수 선택에서 setup 실행 (처음 한 번, 권한 허용) → 탭 4개가 생김
 * 3) 배포 → 새 배포 → 유형: 웹 앱 → 실행: 나 / 액세스: 나만(학원 TV가 원장님 구글 계정으로 로그인된 경우) → 배포 → 나온 주소를 TV에서 열기
 * 선생님은 [출석] 탭에서 오늘 날짜 칸만 체크하면 끝. 점수·연속 기록·티어는 화면이 알아서 계산.
 */
const TAB = { att: '출석', mis: '미션', cfg: '설정' };

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Board')
    .setTitle('RAW SEASON')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// 화면이 1분마다 부르는 함수: 시트 3개를 그대로 넘긴다 (날짜는 yyyy-MM-dd 글자로)
function getData() {
  const ss = SpreadsheetApp.getActive();
  const tz = ss.getSpreadsheetTimeZone();
  const read = name => {
    const sh = ss.getSheetByName(name);
    if (!sh) return [];
    return sh.getDataRange().getValues().map(r => r.map(c =>
      c instanceof Date ? Utilities.formatDate(c, tz, 'yyyy-MM-dd') : c));
  };
  return JSON.stringify({ att: read(TAB.att), mis: read(TAB.mis), cfg: read(TAB.cfg),
    today: Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd') });
}

// 처음 한 번: 탭 만들기 (이미 있으면 건드리지 않음)
function setup() {
  const ss = SpreadsheetApp.getActive();
  let cfg = ss.getSheetByName(TAB.cfg);
  if (!cfg) {
    cfg = ss.insertSheet(TAB.cfg);
    cfg.getRange(1, 1, 13, 2).setValues([
      ['항목', '값'],
      ['시즌 이름', 'RAW SEASON 1'],
      ['시즌 시작', '2026-11-16'],
      ['시즌 끝', '2026-12-31'],
      ['출석 1회 점수', 10],
      ['연속 보너스 (2주 연속부터 매주)', 5],
      ['CREW 기준 점수', 60],
      ['CORE 기준 점수', 150],
      ['RAW 기준 점수', 250],
      ['미션: 셀프캠', 5],
      ['미션: 사이퍼 참여', 10],
      ['미션: 팝업 참여', 10],
      ['미션: 공연·버스킹', 20],
    ]);
    cfg.setColumnWidth(1, 260).getRange('A1:B1').setFontWeight('bold');
  }
  const conf = Object.fromEntries(cfg.getDataRange().getValues().slice(1).map(r => [r[0], r[1]]));
  if (!ss.getSheetByName(TAB.att)) {
    const att = ss.insertSheet(TAB.att);
    const tz = ss.getSpreadsheetTimeZone();
    const ymd = v => v instanceof Date ? Utilities.formatDate(v, tz, 'yyyy-MM-dd') : String(v).slice(0, 10);
    const s = new Date(ymd(conf['시즌 시작']) + 'T00:00:00');
    const e = new Date(ymd(conf['시즌 끝']) + 'T00:00:00');
    const days = [];
    for (let d = new Date(s); d <= e; d.setDate(d.getDate() + 1)) if (d.getDay() >= 1 && d.getDay() <= 5) days.push(new Date(d));
    att.getRange(1, 1, 1, 2).setValues([['이름', '반']]);
    att.getRange(1, 3, 1, days.length).setValues([days]).setNumberFormat('MM/dd (ddd)');
    att.getRange(2, 3, 200, days.length).insertCheckboxes();
    att.setFrozenRows(1); att.setFrozenColumns(2);
    att.getRange('1:1').setFontWeight('bold');
  }
  if (!ss.getSheetByName(TAB.mis)) {
    const mis = ss.insertSheet(TAB.mis);
    mis.getRange(1, 1, 1, 3).setValues([['날짜', '이름', '미션']]).setFontWeight('bold');
    const names = Object.keys(conf).filter(k => k.startsWith('미션: ')).map(k => k.slice(4));
    mis.getRange(2, 3, 500, 1).setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(names).build());
    mis.getRange(2, 1, 500, 1).setNumberFormat('yyyy-mm-dd');
    mis.setFrozenRows(1);
  }
}
