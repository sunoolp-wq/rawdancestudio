/**
 * RAW SEASON (전문반) — 구글 시트 + 학원 태블릿 한 대
 *  - 태블릿 화면 = 순위표 (🔥 금요일 연속 출석·점수·지금 연습 중·포폴 영상 1등)
 *  - 내 이름 → 수업 출석 / 연습 시작·끝 / 운동 완료 / 연습일지 → 비밀번호 4자리 → [기록] 탭에 한 줄
 *  - 운동·연습일지는 집에서 해도 됨 → 오늘/어제 골라 체크, 증거는 단톡방 (원장님 확인)
 * 점수 (2026-11-10 원장님): 장르 수업 10P · 전문반 고정수업 20P · 운동 10P · 연습일지 10P · 개인연습(하루 합계 30분+) 10P
 *  - 수업 출석: 시작 20분 전~시작 15분 후 정상, 그 뒤 수업 끝까지 지각(점수 절반, 🔥 유지). K-POP 제외. 휴강일 없음
 *  - 원장님 비밀번호로 누르면 시간 제한 없이 대신 처리 (기록 E열 '원장님 처리')
 *  - 연습은 수업 시간에 시작 불가, 연습 분에서 수업 시간 제외. 월말평가 준비는 기록만
 *  - [순위] 탭: 태블릿 화면 순위를 그대로 저장 / [리포트] 탭: 매주 일요일 20시 학부모 문자 문구 자동 생성
 *  - 매일 23시 원장님께 오늘 요약 메일 (단톡 인증 확인할 운동·연습일지 목록) / 시트 메뉴 '새 시즌 시작'으로 기록 보관 후 시즌 전환
 * 설치: tools/season/README.md
 */
const TAB = { stu: '학생', log: '기록', cfg: '설정', tt: '시간표', rank: '순위', rep: '리포트' };
// [시간표] 탭 처음 내용 = 2026년 11월 시간표 (tools/daily-story/schedule-2026-11.json). 시간표가 바뀌면 탭에서 고치면 됨
const TIMETABLE = [["월", "16:00", "17:00", "유아 K-POP", "YUNI", "A"], ["월", "17:00", "18:00", "키즈 K-POP", "YUNI", "A"], ["월", "18:00", "19:10", "취미 K-POP", "YUNI", "B"], ["월", "19:30", "20:30", "성인 K-POP", "YUNI", "B"], ["월", "19:40", "20:50", "HEELSCHOREO", "HEEONE", "A"], ["월", "20:50", "22:00", "CHOREO", "RAEKU", "A"], ["화", "16:00", "17:00", "유아 K-POP", "MINKYUNG", "A"], ["화", "17:00", "18:00", "키즈 K-POP", "MINKYUNG", "A"], ["화", "18:00", "19:10", "취미 K-POP", "MINKYUNG", "B"], ["화", "18:30", "19:40", "BASIC", "GAON", "A"], ["화", "19:40", "20:50", "GIRLISH", "ARIN", "A"], ["수", "16:00", "17:00", "유아 K-POP", "YUNI", "A"], ["수", "17:00", "18:00", "키즈 K-POP", "YUNI", "A"], ["수", "18:00", "19:10", "취미 K-POP", "YUNI", "B"], ["수", "19:30", "20:30", "성인 K-POP", "YUNI", "B"], ["수", "19:40", "20:50", "WAACKING", "J", "A"], ["수", "20:50", "22:00", "JAZZ", "KIRY", "A"], ["목", "16:00", "17:00", "유아 K-POP", "MINKYUNG", "A"], ["목", "17:00", "18:00", "키즈 K-POP", "MINKYUNG", "A"], ["목", "18:00", "19:10", "취미 K-POP", "MINKYUNG", "B"], ["목", "18:30", "19:40", "BASIC", "GAON", "A"], ["목", "19:40", "20:50", "HIP HOP", "NOFF", "A"], ["목", "20:50", "22:00", "CHOREO", "HWAN.U", "A"], ["금", "18:30", "20:00", "PRO 전문반", "YELLS", "A"], ["금", "20:10", "21:20", "GIRLS HIPHOP", "MINKYUNG", "A"], ["토", "13:00", "14:00", "유아 K-POP", "REGINA", "A"], ["토", "14:00", "15:00", "키즈 K-POP", "REGINA", "A"], ["토", "15:00", "16:10", "취미 K-POP", "REGINA", "A"]];
// 처음 setup 때 [학생] 탭에 넣을 명단 [이름, 상태]. 상태에 '휴원'이 들어가면 화면에 안 나오고 체크도 안 됨
const ROSTER = [];
// 처음 setup 때 [설정] 탭에 넣을 시즌 (나중엔 [설정] 탭에서 고침)
const SEASON = { name: 'RAW SEASON 1', start: '2026-11-13', end: '2026-12-25' };
const KINDS = ['수업 출석', '연습 시작', '연습 끝', '운동 완료', '연습일지'];
const DAILY = ['운동 완료', '연습일지']; // 오늘/어제 골라서, 날짜마다 1회
const PRAC_TYPES = ['개인연습', '월말평가 준비'];
const MASTER_KEY = '원장님 비밀번호'; // [설정] 항목. 화면(getData)으로는 절대 보내지 않음

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Board').setTitle('RAW SEASON')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
}
function onOpen() {
  SpreadsheetApp.getUi().createMenu('RAW SEASON').addItem('이번 주 리포트 만들기', 'weeklyReport').addItem('오늘 요약 메일 지금 보내기', 'dailySummary')
    .addSeparator().addItem('새 시즌 시작 (기록 보관)', 'newSeasonMenu').addItem('설치·업데이트 (setup)', 'setup').addToUi();
}

const tz_ = () => SpreadsheetApp.getActive().getSpreadsheetTimeZone();
const fmt_ = (d, f) => Utilities.formatDate(d, tz_(), f || 'yyyy-MM-dd HH:mm:ss');
const P_ = x => Date.parse(String(x).replace(' ', 'T')); // 시트 시간대 글자끼리 비교 (스크립트 시간대와 무관)
const DAYS_ = ['일', '월', '화', '수', '목', '금', '토'];
const PRO_ = /전문반|PRO/;
// 출석 포인트 제외 수업: [설정] '출석 제외 수업'에 쉼표로 (기본 K-POP, 원장님 2026-11-10)
const skip_ = (name, skip) => String(skip || '').split(',').map(x => x.trim()).filter(Boolean).some(x => String(name).indexOf(x) >= 0);
const hm_ = v => { const m = /(\d{1,2}):(\d{2})/.exec(String(v)); return m ? (+m[1]) * 60 + (+m[2]) : null; };
const hhmm_ = n => String(Math.floor(n / 60)).padStart(2, '0') + ':' + String(n % 60).padStart(2, '0');
const mins_ = s => (+String(s).slice(11, 13)) * 60 + (+String(s).slice(14, 16));
// 날짜 글자 계산 (스크립트 시간대와 무관하게 UTC로)
const addDays_ = (s, n) => { const [y, m, d] = s.split('-').map(Number); return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10); };
const dow_ = s => { const [y, m, d] = s.split('-').map(Number); return new Date(Date.UTC(y, m - 1, d)).getUTCDay(); };
const base_ = note => String(note || '').replace(' (지각)', '').trim(); // 'HH:MM 수업명'
// 그날 수업 [{s, e, label: 'HH:MM 수업명', range, teacher}]. 태블릿 화면(Board.html)에도 같은 계산이 있음
function classesOn_(tt, dateS, skip) {
  const day = DAYS_[dow_(dateS)];
  return tt.slice(1).filter(r => String(r[0]).trim().charAt(0) === day && hm_(r[1]) != null && hm_(r[2]) != null && !skip_(r[3], skip))
    .map(r => ({ s: hm_(r[1]), e: hm_(r[2]), label: `${hhmm_(hm_(r[1]))} ${String(r[3]).trim()}`, range: `${hhmm_(hm_(r[1]))}~${hhmm_(hm_(r[2]))} ${String(r[3]).trim()}`, teacher: String(r[4] || '').trim() }));
}
// 연습 분 = 시작~끝에서 수업 시간과 겹치는 분을 뺀 것 (같은 날)
function pracMin_(tt, startS, endS, skip) {
  const a = mins_(startS), b = mins_(endS);
  const over = classesOn_(tt, String(startS).slice(0, 10), skip).reduce((t, c) => t + Math.max(0, Math.min(b, c.e) - Math.max(a, c.s)), 0);
  return { total: b - a, over, min: b - a - over };
}
// 지금 출석: open = 시작 before분 전~시작 after분 후 (정상), late = 그 뒤~수업 끝 (지각), next = 다음 수업
function classesAt_(tt, nowS, before, after, skip) {
  const list = classesOn_(tt, nowS.slice(0, 10), skip), m = mins_(nowS);
  return { all: list, open: list.filter(c => m >= c.s - before && m <= c.s + after), late: list.filter(c => m > c.s + after && m <= c.e),
    next: list.filter(c => c.s - before > m).sort((a, b) => a.s - b.s)[0] || null };
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
const num_ = (v, d) => v === '' || v == null || isNaN(+v) ? d : +v;
// 오늘 개인연습 세션들 (연습 시작 → 연습 끝 '개인연습') 분 합계
function pracToday_(rows, tt, skip) {
  let open = null, sum = 0;
  rows.forEach(x => { if (x.k === '연습 시작') open = x; else if (x.k === '연습 끝' && open) { if (x.note !== '월말평가 준비') sum += pracMin_(tt, open.t, x.t, skip).min; open = null; } });
  return sum;
}

// 태블릿 화면이 1분마다·기록 직후 부름 (학생 비밀번호·원장님 비밀번호는 보내지 않음)
function getData() {
  const stu = read_(TAB.stu).filter((r, i) => i === 0 || String(r[3] || '').indexOf('휴원') < 0).map(r => [r[0], '', r[2]]);
  const cfg = read_(TAB.cfg).filter(r => String(r[0]).trim().indexOf(MASTER_KEY) !== 0 && String(r[0]).trim().indexOf('요약 메일') !== 0);
  return JSON.stringify({ stu, log: read_(TAB.log), cfg, tt: read_(TAB.tt), now: fmt_(new Date()) });
}

// 태블릿에서 누르면 기록 한 줄. note = 수업 출석: 'HH:MM 수업명' / 연습 끝: '개인연습' | '월말평가 준비' / 운동 완료·연습일지: 'yyyy-MM-dd'
function checkIn(name, pin, kind, note) {
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    if (KINDS.indexOf(kind) < 0) return { ok: false, msg: '알 수 없는 버튼이에요' };
    const row = read_(TAB.stu).slice(1).find(r => String(r[0]).trim() === name);
    if (!row) return { ok: false, msg: '명단에 없는 이름이에요' };
    if (String(row[3] || '').indexOf('휴원') >= 0) return { ok: false, msg: '휴원 중인 학생이에요' };
    const g = cfg_(), master = String(g(MASTER_KEY) || '').trim(), isMaster = master.length >= 4 && String(pin).trim() === master;
    // 학생 비밀번호 5번 틀리면 5분 잠금 (친구 번호 맞히기 방지). 원장님 비밀번호는 잠금 없음
    const cache = CacheService.getScriptCache(), ck = 'pinfail_' + name, fails = +(cache.get(ck) || 0);
    if (!isMaster) {
      if (fails >= 5) return { ok: false, msg: '비밀번호를 5번 틀려서 5분 동안 잠겼어요' };
      if (String(row[1]).trim().padStart(4, '0') !== String(pin).trim().padStart(4, '0')) { cache.put(ck, String(fails + 1), 300); return { ok: false, msg: '비밀번호가 달라요' }; }
      cache.remove(ck);
    }
    const now = new Date(), nowS = fmt_(now), today = nowS.slice(0, 10);
    const S = String(g('시즌 시작')).slice(0, 10), E = String(g('시즌 끝')).slice(0, 10);
    if (S && today < S) return { ok: false, msg: `시즌은 ${S}부터 시작해요` };
    if (E && today > E) return { ok: false, msg: '시즌이 끝났어요. 다음 시즌을 기다려 주세요!' };
    const holi = String(g('휴강일') || '').match(/\d{4}-\d{2}-\d{2}/g) || [], isHoli = holi.indexOf(today) >= 0;
    const TT = isHoli ? [[]] : read_(TAB.tt), skipS = g('출석 제외 수업') === '' ? 'K-POP' : g('출석 제외 수업');
    const mine = read_(TAB.log).slice(1).filter(r => String(r[1]).trim() === name && String(r[0]).slice(0, 10) === today)
      .map(r => ({ t: String(r[0]), k: String(r[2]).trim(), note: String(r[3] || '').trim() }));
    const lastT = k => { const a = mine.filter(x => x.k === k); return a.length ? a[a.length - 1].t : ''; };
    const openS = (a, b) => lastT(a) > lastT(b); // 시작만 있고 끝이 없음
    let late = false;
    if (kind === '수업 출석') {
      const w = classesAt_(TT, nowS, num_(g('출석: 시작 몇 분 전부터'), 20), num_(g('출석: 시작 후 몇 분까지'), 15), skipS);
      let c = null;
      if (isMaster) c = w.all.find(x => x.label === note) || null;
      else {
        c = w.open.find(x => x.label === note) || w.late.find(x => x.label === note) || null;
        if (!c && w.open.length + w.late.length === 1) c = w.open[0] || w.late[0];
        if (!c && !w.open.length && !w.late.length) return { ok: false, msg: (isHoli ? '오늘은 휴강일이에요' : '지금은 수업 출석 시간이 아니에요') + (w.next ? ` · 다음 ${w.next.label}` : '') };
        late = !!c && w.late.indexOf(c) >= 0;
      }
      if (!c) return { ok: false, msg: '어느 수업인지 골라 주세요' };
      const cls = mine.filter(x => x.k === '수업 출석');
      if (cls.some(x => base_(x.note) === c.label)) return { ok: false, msg: `${c.label} 출석은 이미 했어요` };
      if (cls.length >= 3) return { ok: false, msg: '수업 출석은 하루 3번까지예요' };
      note = c.label + (late ? ' (지각)' : '');
    }
    if (DAILY.indexOf(kind) >= 0) {
      const yest = fmt_(new Date(now.getTime() - 864e5), 'yyyy-MM-dd');
      if (note !== today && note !== yest) return { ok: false, msg: '오늘이나 어제만 고를 수 있어요' };
      const dup = read_(TAB.log).slice(1).some(r => String(r[1]).trim() === name && String(r[2]).trim() === kind && String(r[3]).slice(0, 10) === note);
      if (dup) return { ok: false, msg: `${note === today ? '오늘' : '어제'} ${kind}는 이미 체크했어요` };
    }
    if (kind === '연습 시작' && openS('연습 시작', '연습 끝')) return { ok: false, msg: '이미 연습 중이에요. 끝나면 [연습 끝]' };
    if (kind === '연습 시작' && !isMaster) {
      const m = mins_(nowS), c = classesOn_(TT, today, skipS).find(c => m >= c.s && m < c.e);
      if (c) return { ok: false, msg: `수업 시간에는 연습을 시작할 수 없어요 · ${c.range}` };
    }
    if (kind === '연습 끝' && !openS('연습 시작', '연습 끝')) return { ok: false, msg: '[연습 시작]을 먼저 눌러야 해요' };
    if (kind === '연습 끝' && PRAC_TYPES.indexOf(note) < 0) return { ok: false, msg: '개인연습인지 월말평가 준비인지 골라 주세요' };
    SpreadsheetApp.getActive().getSheetByName(TAB.log).appendRow([nowS, name, kind, note || '', isMaster ? '원장님 처리' : '']);
    let msg = '';
    if (kind === '연습 끝') {
      const pm = pracMin_(TT, lastT('연습 시작'), nowS, skipS), need = num_(g('연습 인정 최소 분'), 30);
      const ex = pm.over ? ` (수업 시간 ${pm.over}분 제외)` : '';
      if (note === '월말평가 준비') msg = `월말평가 준비 ${pm.min}분 기록${ex} · 점수 없음`;
      else { const sum = pracToday_(mine.concat([{ t: nowS, k: '연습 끝', note }]), TT, skipS);
        msg = `개인연습 ${pm.min}분${ex} · 오늘 합계 ${sum}분` + (sum >= need ? ' 🔥 인정!' : ` · ${need}분부터 인정`); }
    }
    if (DAILY.indexOf(kind) >= 0) msg = `${note === today ? '오늘' : '어제'} ${kind} ✓ · 단톡방에 인증 올려 주세요`;
    if (kind === '수업 출석') msg = note + (late ? ' · 점수 절반, 🔥는 유지' : '');
    if (isMaster) msg = '원장님 처리 · ' + msg;
    return { ok: true, name, kind, time: nowS.slice(11, 16), msg };
  } finally { lock.releaseLock(); }
}

// 태블릿 화면이 계산한 순위를 [순위] 탭에 저장 (바뀌었을 때만). 원장님이 시트에서 바로 보고, 주간 리포트에도 씀
function saveBoard(json) {
  const rows = JSON.parse(json), key = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, json, Utilities.Charset.UTF_8));
  const props = PropertiesService.getScriptProperties();
  if (props.getProperty('boardHash') === key) return false;
  const ss = SpreadsheetApp.getActive(); let sh = ss.getSheetByName(TAB.rank);
  if (!sh) sh = ss.insertSheet(TAB.rank);
  sh.clearContents();
  const head = ['순위', '이름', '점수', '🔥 연속(주)', '상태', '금요일 도장', '장르 수업', '개인연습(일)', '운동(일)', '연습일지(일)'];
  sh.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold');
  if (rows.length) sh.getRange(2, 1, rows.length, head.length).setValues(rows.map(r => head.map((h, i) => r[i] == null ? '' : r[i])));
  sh.getRange(rows.length + 3, 1).setValue('업데이트 ' + fmt_(new Date()) + ' (태블릿 화면 기준)');
  props.setProperty('boardHash', key); return true;
}

// 매주 일요일 20시 (트리거) 또는 시트 메뉴 → [리포트] 탭에 이번 주 학생별 학부모 문자 문구
function weeklyReport() {
  const g = cfg_(), now = new Date(), today = fmt_(now, 'yyyy-MM-dd'), dow = dow_(today);
  // 이번 주 월~일 (일요일 20시에 돌면 그 주 전체)
  const last = dow === 0 ? today : addDays_(today, 7 - dow), first = addDays_(last, -6);
  const md = s => (+s.slice(5, 7)) + '/' + (+s.slice(8, 10));
  const TT = read_(TAB.tt), skipS = g('출석 제외 수업') === '' ? 'K-POP' : g('출석 제외 수업'), need = num_(g('연습 인정 최소 분'), 30);
  const FW = num_(g('고정수업 요일'), 5), holi = String(g('휴강일') || '').match(/\d{4}-\d{2}-\d{2}/g) || [];
  const log = read_(TAB.log).slice(1).map(r => ({ t: String(r[0]), d: String(r[0]).slice(0, 10), n: String(r[1]).trim(), k: String(r[2]).trim(), note: String(r[3] || '').trim() }))
    .filter(x => x.d >= first && x.d <= last).sort((a, b) => a.t < b.t ? -1 : 1);
  const rank = {}; read_(TAB.rank).slice(1).forEach(r => { if (r[1]) rank[String(r[1]).trim()] = r; });
  const stu = read_(TAB.stu).slice(1).filter(r => String(r[0]).trim() && String(r[3] || '').indexOf('휴원') < 0);
  let fri = null; for (let i = 0; i < 7; i++) { const d = addDays_(first, i); if (dow_(d) === FW) fri = d; }
  const total = stu.length, out = [];
  stu.forEach(r => {
    const n = String(r[0]).trim(), mine = log.filter(x => x.n === n);
    const cls = mine.filter(x => x.k === '수업 출석'), genre = cls.filter(x => !PRO_.test(x.note) && x.note).length;
    const proRow = fri ? cls.find(x => x.d === fri && (PRO_.test(x.note) || !x.note)) : null;
    const shield = fri && String(r[2] || '').indexOf(fri) >= 0;
    const friS = !fri ? '-' : holi.indexOf(fri) >= 0 ? '휴강' : fri > today ? '예정' : proRow ? (proRow.note.indexOf('지각') >= 0 ? '지각 출석' : '출석') : shield ? '보호권 사용' : '결석';
    const days = [...new Set(mine.map(x => x.d))];
    const prac = days.filter(d => pracToday_(mine.filter(x => x.d === d), TT, skipS) >= need).length;
    const ex = new Set(mine.filter(x => x.k === '운동 완료').map(x => x.note.slice(0, 10))).size;
    const jr = new Set(mine.filter(x => x.k === '연습일지').map(x => x.note.slice(0, 10))).size;
    const rk = rank[n] || [];
    const msg = `[로우댄스 수원점 · 전문반 주간 리포트]\n${n} 학생 (${md(first)}~${md(last)})\n\n` +
      `✅ 금요일 전문반 : ${friS}\n🔥 금요일 연속 출석 : ${rk[3] !== undefined && rk[3] !== '' ? rk[3] + '주' : '-'}\n` +
      `📚 장르 수업 ${genre}회 · 개인연습 ${prac}일 · 운동 ${ex}일 · 연습일지 ${jr}일\n` +
      `🏆 시즌 순위 ${rk[0] ? rk[0] + '위' : '-'} / ${total}명 (${rk[2] !== undefined && rk[2] !== '' ? rk[2] + 'P' : '-'})\n\n문의 031-225-6600`;
    out.push([n, friS, genre, prac, ex, jr, cls.length + prac + ex + jr, rk[0] || '', rk[2] || '', msg]);
  });
  const ss = SpreadsheetApp.getActive(); let sh = ss.getSheetByName(TAB.rep); if (!sh) sh = ss.insertSheet(TAB.rep);
  sh.clearContents();
  sh.getRange(1, 1).setValue(`주간 리포트 ${md(first)}~${md(last)} · 만든 시각 ${fmt_(now)} · 이번 주 체크 합계 = 수업 출석 + 개인연습일 + 운동일 + 연습일지일`).setFontWeight('bold');
  const head = ['이름', '금요일 전문반', '장르 수업', '개인연습(일)', '운동(일)', '연습일지(일)', '이번 주 체크 합계', '시즌 순위', '점수', '학부모 문자 (복사해서 보내기)'];
  sh.getRange(3, 1, 1, head.length).setValues([head]).setFontWeight('bold');
  if (out.length) sh.getRange(4, 1, out.length, head.length).setValues(out.sort((a, b) => b[6] - a[6]));
  sh.setColumnWidth(10, 420); sh.getRange(4, 10, Math.max(1, out.length), 1).setWrap(true);
  return out.length;
}

// 매일 23시 (트리거) 또는 시트 메뉴 → 원장님께 오늘 요약 메일 (원장님 2026-11-11 D2)
function dailySummary() {
  const g = cfg_(), to = String(g('요약 메일') || '').trim();
  if (!to) return 'no-mail';
  const today = fmt_(new Date(), 'yyyy-MM-dd'), md = s => (+s.slice(5, 7)) + '/' + (+s.slice(8, 10));
  const log = read_(TAB.log).slice(1).map(r => ({ t: String(r[0]), n: String(r[1]).trim(), k: String(r[2]).trim(), note: String(r[3] || '').trim(), memo: String(r[4] || '').trim() }))
    .filter(x => x.t.slice(0, 10) === today).sort((a, b) => a.t < b.t ? -1 : 1);
  const verify = log.filter(x => DAILY.indexOf(x.k) >= 0), late = log.filter(x => x.k === '수업 출석' && x.note.indexOf('(지각)') >= 0), byMaster = log.filter(x => x.memo === '원장님 처리');
  const open = {}; log.forEach(x => { if (x.k === '연습 시작') open[x.n] = x.t; else if (x.k === '연습 끝') delete open[x.n]; });
  const names = [...new Set(log.map(x => x.n))];
  const line = x => `- ${x.t.slice(11, 16)} ${x.n} · ${x.k}${x.note ? ' · ' + (DAILY.indexOf(x.k) >= 0 ? (x.note === today ? '오늘' : md(x.note)) : x.note) : ''}`;
  const body = [`RAW SEASON 오늘 요약 (${md(today)})`, '',
    `오늘 체크한 학생 ${names.length}명 · 기록 ${log.length}줄`, '',
    `■ 단톡방 인증 확인할 것 (운동·연습일지) ${verify.length}건`, ...(verify.length ? verify.map(line) : ['- 없음']),
    '  → 인증이 없으면 시트 [기록] 탭에서 그 줄을 삭제하면 점수가 빠져요', '',
    `■ 지각 출석 ${late.length}건`, ...(late.length ? late.map(line) : ['- 없음']), '',
    `■ 원장님 처리 ${byMaster.length}건`, ...(byMaster.length ? byMaster.map(line) : ['- 없음']), '',
    `■ 연습 끝을 안 누른 학생 (오늘 연습 불인정)`, ...(Object.keys(open).length ? Object.entries(open).map(([n, t]) => `- ${n} · ${t.slice(11, 16)} 시작`) : ['- 없음']), '',
    '■ 오늘 전체 기록', ...(log.length ? log.map(line) : ['- 없음'])].join('\n');
  MailApp.sendEmail(to, `[RAW SEASON] ${md(today)} 오늘 요약 · 인증 확인 ${verify.length}건`, body);
  return body;
}

// 새 시즌: [기록]·[순위]를 '기록 (시즌 이름)'·'순위 (시즌 이름)'으로 보관 → 기록 비우기, 보호권 칸 비우기, [설정] 시즌 이름·날짜 바꾸기 (원장님 2026-11-11 D3)
function newSeasonMenu() {
  const ui = SpreadsheetApp.getUi(), g = cfg_(), old = String(g('시즌 이름') || 'RAW SEASON').trim();
  const ask = (q, d) => { const r = ui.prompt('새 시즌 시작', `${q}\n(비우면: ${d})`, ui.ButtonSet.OK_CANCEL); if (r.getSelectedButton() !== ui.Button.OK) throw new Error('취소'); return r.getResponseText().trim() || d; };
  try {
    const m = old.match(/^(.*?)(\d+)$/), nm = ask('새 시즌 이름', m ? m[1] + (+m[2] + 1) : old + ' 2');
    const st = ask('시작 날짜 (예 2026-12-01)', ''), en = ask('끝 날짜 (예 2026-12-31)', '');
    if (!/^\d{4}-\d{2}-\d{2}$/.test(st) || !/^\d{4}-\d{2}-\d{2}$/.test(en) || st > en) { ui.alert('날짜를 2026-12-01 처럼 써 주세요. 아무것도 바꾸지 않았어요.'); return; }
    if (ui.alert('새 시즌 시작', `'${old}' 기록을 보관 탭으로 옮기고\n${nm} (${st} ~ ${en})을 시작할까요?\n보호권 칸도 비워져요.`, ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
    ui.alert(newSeason_(nm, st, en));
  } catch (e) { if (String(e.message) !== '취소') throw e; }
}
function newSeason_(name, start, end) {
  const ss = SpreadsheetApp.getActive(), old = String(cfg_()('시즌 이름') || 'RAW SEASON').trim();
  [TAB.log, TAB.rank].forEach(t => { const sh = ss.getSheetByName(t); if (!sh) return;
    let nm = `${t} (${old})`, i = 2; while (ss.getSheetByName(nm)) nm = `${t} (${old}) ${i++}`;
    sh.copyTo(ss).setName(nm);
    const last = sh.getLastRow(); if (t === TAB.log) { if (last > 1) sh.deleteRows(2, last - 1); } else sh.clearContents(); });
  const stu = ss.getSheetByName(TAB.stu); if (stu && stu.getLastRow() > 1) stu.getRange(2, 3, stu.getLastRow() - 1, 1).clearContent();
  const c = ss.getSheetByName(TAB.cfg), v = c.getDataRange().getValues();
  v.forEach((r, i) => { const k = String(r[0]).trim(), set = x => c.getRange(i + 1, 2).setNumberFormat('@').setValue(x);
    if (k.indexOf('시즌 이름') === 0) set(name); else if (k.indexOf('시즌 시작') === 0) set(start); else if (k.indexOf('시즌 끝') === 0) set(end); });
  PropertiesService.getScriptProperties().deleteProperty('boardHash');
  return `${name} 시작 준비 끝 (${start} ~ ${end}).\n지난 기록은 '${TAB.log} (${old})' 탭에 보관했어요. 태블릿은 1분 안에 새 시즌으로 바뀌어요.`;
}

// 처음 한 번: 탭 만들기. 이미 설치했으면 다시 실행해도 됨 (없는 탭·설정 항목·트리거만 추가, 기존 내용은 그대로)
function setup() {
  const ss = SpreadsheetApp.getActive();
  if (ss.getSpreadsheetTimeZone() !== 'Asia/Seoul') ss.setSpreadsheetTimeZone('Asia/Seoul');
  const stuPins = ss.getSheetByName(TAB.stu) ? ss.getSheetByName(TAB.stu).getDataRange().getValues().slice(1).map(r => String(r[1])) : [];
  let mp; do { mp = String(1000 + Math.floor(Math.random() * 9000)); } while (stuPins.indexOf(mp) >= 0);
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
    ['연습 인정 최소 분 (하루 합계)', 30],
    ['보호권 (시즌당)', 1],
    ['고정수업 요일 (0=일 … 5=금)', 5],
    ['고정수업 시간', '18:30'],
    ['출석: 시작 몇 분 전부터', 20],
    ['출석: 시작 후 몇 분까지', 15],
    ['지각 출석 점수 (%)', 50],
    ['출석 제외 수업 (이름에 들어가면 제외, 쉼표로)', 'K-POP'],
    ['휴강일 (날짜를 쉼표로 · 그날은 출석·금요일 도장 없음)', ''],
    [MASTER_KEY + ' (4자리 · 학생과 다르게 · 학생에게 알려 주지 않기)', mp],
    ['요약 메일 받을 주소 (비우면 안 보냄)', Session.getEffectiveUser().getEmail()],
  ];
  let c = ss.getSheetByName(TAB.cfg);
  if (!c) {
    c = ss.insertSheet(TAB.cfg);
    c.getRange(1, 1, rows.length, 2).setNumberFormat('@').setValues(rows.map(r => r.map(String)));
    c.setColumnWidth(1, 300).setColumnWidth(2, 420).getRange('A1:B1').setFontWeight('bold');
  } else { // 이미 있으면 없는 항목만 아래에 추가 (원장님이 고친 값은 그대로)
    const have = c.getDataRange().getValues().map(r => String(r[0]).trim());
    rows.filter(r => !have.some(h => h.split(' (')[0] === String(r[0]).split(' (')[0])).forEach(r => { c.appendRow([r[0], String(r[1])]); c.getRange(c.getLastRow(), 2).setNumberFormat('@'); });
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
    const used = {}; used[mp] = 1;
    const pin = () => { let p; do { p = String(1000 + Math.floor(Math.random() * 9000)); } while (used[p]); used[p] = 1; return p; };
    if (ROSTER.length) s.getRange(2, 1, ROSTER.length, 4).setValues(ROSTER.map(([n, st]) => [n, pin(), '', st || '']));
  }
  if (!ss.getSheetByName(TAB.log)) {
    const l = ss.insertSheet(TAB.log);
    l.getRange(1, 1, 1, 5).setValues([['시각', '이름', '종류', '수업 / 연습 종류 / 해당 날짜', '비고']]).setFontWeight('bold');
    l.getRange('A:A').setNumberFormat('@'); l.getRange('D:D').setNumberFormat('@'); l.setFrozenRows(1);
  }
  // 매주 일요일 20시 주간 리포트 (한 번만 만듦)
  if (!ScriptApp.getProjectTriggers().some(t => t.getHandlerFunction() === 'weeklyReport'))
    ScriptApp.newTrigger('weeklyReport').timeBased().onWeekDay(ScriptApp.WeekDay.SUNDAY).atHour(20).create();
  // 매일 23시 원장님 요약 메일 (한 번만 만듦)
  if (!ScriptApp.getProjectTriggers().some(t => t.getHandlerFunction() === 'dailySummary'))
    ScriptApp.newTrigger('dailySummary').timeBased().everyDays(1).atHour(23).create();
}
