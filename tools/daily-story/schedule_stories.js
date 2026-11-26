#!/usr/bin/env node
// 인스타 스토리 하루치 자동 예약 (원장님 맥 · Ego Lite · Meta 비즈니스 스위트)
// 원장님 2026-11-23: "방금 예약에 쓴 스크립트를 살려서 매일 자동 예약으로" — 자동 실행(--yes)은 확인 없이 예약해도 된다고 허락함
//
// 사용:
//   node tools/daily-story/schedule_stories.js 2026-11-24          표 보여 주고 y 누르면 예약
//   node tools/daily-story/schedule_stories.js 2026-11-24 --yes    확인 없이 예약 (launchd 자동 실행용)
//   node tools/daily-story/schedule_stories.js --tomorrow [--yes]  내일 날짜
//   --no-update  최신 받기 건너뜀 / --check  예약 안 하고 점검만 (브라우저 로그인 확인까지) / --force  이미 예약한 날도 다시
//   --at HH:MM  시작 시각 바꾸기 (기본 00:00). 원장님 2026-11-27 "지금 예약으로 올릴 순 없나": 이미 지난 날 다시 올릴 때 예) --at 01:20 → 01:20 시간표, 01:21·01:22 수업
//
// 순서: 최신 받기(3_업데이트와 같은 방식, 대강·팝업은 클라우드 것 그대로) → render.js → plan.js → 영상 찾기 → Ego Lite로 00:00부터 예약
// 같은 날 두 번 예약 방지: ~/Library/Application Support/raw-story/<날짜>.json 에 예약한 칸을 적어 둔다
// 로그: ~/Library/Logs/raw-story.log / 끝나면 macOS 알림
const fs = require('fs'), path = require('path'), os = require('os');
const { spawnSync } = require('child_process');

const HOME = os.homedir();
process.env.PATH = ['/opt/homebrew/bin', '/usr/local/bin', path.join(HOME, '.local/bin'), process.env.PATH || '/usr/bin:/bin'].join(':');
const ROOT = path.resolve(__dirname, '../..');
const BR = 'claude/low-dance-marketing-agents-lisndi';
const MOVIES = path.join(HOME, 'Movies', 'RAW 영상공장');
const STATE_DIR = path.join(HOME, 'Library', 'Application Support', 'raw-story');
const LOG = path.join(HOME, 'Library', 'Logs', 'raw-story.log');
const COMPOSER = 'https://business.facebook.com/latest/story_composer/?asset_id=1071678762703338&business_id=1608704040226408';
const PLANNER = 'https://business.facebook.com/latest/content_calendar?asset_id=1071678762703338&business_id=1608704040226408';

// ---------- 공통 ----------
fs.mkdirSync(path.dirname(LOG), { recursive: true });
const stamp = () => new Date().toLocaleString('sv-SE').replace('T', ' ');
const log = (...a) => { const s = a.join(' '); console.log(s); fs.appendFileSync(LOG, `[${stamp()}] ${s}\n`); };
const notify = (msg) => { log('알림:', msg); spawnSync('osascript', ['-e', `display notification ${JSON.stringify(msg)} with title "RAW 스토리 예약"`]); };
const run = (cmd, args, opt = {}) => {
  const r = spawnSync(cmd, args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 << 20, ...opt });
  const out = (r.stdout || '') + (r.stderr || '');
  if (out.trim()) fs.appendFileSync(LOG, out.split('\n').map(l => `    ${l}`).join('\n') + '\n');
  return { ok: r.status === 0, out, stdout: r.stdout || '', status: r.status, error: r.error };
};
const norm = s => String(s || '').toUpperCase().replace(/[^0-9A-Z가-힣]/g, '');
const pad = n => String(n).padStart(2, '0');

// ---------- 인자 ----------
const argv = process.argv.slice(2);
const flag = f => argv.includes(f);
const YES = flag('--yes'), CHECK = flag('--check'), FORCE = flag('--force'), NO_UPDATE = flag('--no-update');
const AT = (argv[argv.indexOf('--at') + 1] || '').match(/^(\d{1,2}):(\d{2})$/) && argv.includes('--at') ? argv[argv.indexOf('--at') + 1] : '00:00';
const AT_MIN = +AT.split(':')[0] * 60 + +AT.split(':')[1];
const hhmm = m => `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
let date = argv.find(a => /^\d{4}-\d{2}-\d{2}$/.test(a));
if (!date && (flag('--tomorrow') || argv.includes('tomorrow'))) {
  const now = new Date();
  if (YES && now.getHours() < 6) { notify('스토리 예약 확인 필요 (자정 넘어 실행돼 건너뜀)'); process.exit(1); }
  const t = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  date = `${t.getFullYear()}-${pad(t.getMonth() + 1)}-${pad(t.getDate())}`;
}
if (!date) { console.error('날짜를 넣어 주세요: node tools/daily-story/schedule_stories.js 2026-11-24 [--yes]  또는 --tomorrow'); process.exit(1); }
const [Y, M, D] = date.split('-').map(Number);
const MMDD = pad(M) + pad(D), MD = `${M}/${D}`;
const DOW = new Date(Y, M - 1, D).getDay();

function keepContent() {
  try { return fs.readFileSync(path.join(ROOT, 'tools/raw-studio/keep-content.txt'), 'utf8').split('\n').map(l => l.replace(/#.*/, '').trim()).filter(Boolean).map(l => `/content/${l}/`); }
  catch (e) { return []; }
}

// ---------- 1. 최신 받기 (3_업데이트.command와 같은 방식) ----------
function update() {
  const g = (...a) => run('git', a);
  const head = g('rev-parse', 'HEAD').stdout.trim();
  const known = g('rev-parse', '--verify', '-q', `refs/remotes/origin/${BR}`).stdout.trim();
  // 이 맥에서 만든 커밋이나 고친 파일이 있으면 reset --hard로 지워지므로 받지 않는다 (content는 괜찮음. extra.json은 클라우드 것을 그대로 씀)
  if (known && head !== known) { log('⚠ 최신 받기 건너뜀: 이 맥에 올리지 않은 커밋이 있음'); return false; }
  const dirty = g('status', '--porcelain', '-z', '--untracked-files=no').stdout.split('\0').filter(Boolean)
    .map(l => l.slice(3)).filter(p => p && p !== 'tools/daily-story/extra.json' && !p.startsWith('content/'));
  if (dirty.length) { log('⚠ 최신 받기 건너뜀: 고친 파일 있음 →', dirty.slice(0, 5).join(', ')); return false; }
  const pkg = () => { try { return fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'); } catch (e) { return ''; } };
  const pkgBefore = pkg();
  if (!g('fetch', '-q', '--depth', '1', 'origin', BR).ok) { log('⚠ 최신 받기 실패 (인터넷·GitHub 로그인 확인) → 지금 버전으로 계속'); return false; }
  g('reset', '-q', '--hard', 'FETCH_HEAD');
  g('sparse-checkout', 'set', '--no-cone', '/*', '!/content/', ...keepContent());   // 원장님 2026-11-23 "맥 용량": content는 안 받고 keep-content.txt 폴더만 남김
  // 대강·팝업(extra.json)은 클라우드(GitHub) 것을 그대로 씀 — 맥에서 고친 건 덮어씀 (원장님 2026-11-23 "대강은 클라우드에서만 고칠게")
  if (pkg() !== pkgBefore) run('npm', ['install', '--no-audit', '--no-fund', '--silent']);
  log('최신 받기 완료:', g('log', '-1', '--format=%h %s').stdout.trim());
  return true;
}

// ---------- 3. 수업 순서 ----------
function plan() {
  const r = run('node', [path.join(__dirname, 'plan.js'), date]);
  if (!r.ok) throw new Error('plan.js 실패: ' + r.out.trim());
  const classes = [];
  for (const line of r.stdout.split('\n')) {
    const m = line.match(/^00:(\d\d)\s{2}(\d\d:\d\d) (.+?)\s{2}T\. (.+?)(\s{2}\(.+\))?$/);
    if (m) classes.push({ min: +m[1], start: m[2], name: m[3], teacher: m[4] });
  }
  return classes;
}

// ---------- 4. 영상 찾기 ----------
function allVideos() {
  const out = [];
  const walk = (dir, depth) => {
    let ents = []; try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch (e) { return; }
    for (const e of ents) {
      const p = path.join(dir, e.name);
      if (e.isDirectory() && depth < 2) walk(p, depth + 1);
      else if (e.isFile() && /\.mp4$/i.test(e.name)) out.push({ p, name: e.name, mtime: fs.statSync(p).mtimeMs });
    }
  };
  walk(MOVIES, 0);
  return out;
}
// 파일 이름: MMDD_쌤15초_<쌤>_<장르>.mp4 / <시각>_TRACKPAD_<쌤>_<장르>.mp4
function parseClip(name) {
  const parts = name.replace(/\.mp4$/i, '').split('_');
  const i = parts.findIndex(x => x === '쌤15초' || x.toUpperCase() === 'TRACKPAD');
  if (i < 0 || !parts[i + 1]) return null;
  return { prefix: parts.slice(0, i).join('_'), kind: parts[i], teacher: norm(parts[i + 1]), genre: norm(parts.slice(i + 2).join(' ')) };
}
const genreOk = (cls, g) => !g || norm(cls).includes(g) || g.includes(norm(cls));
function findClip(videos, c) {
  const t = norm(c.teacher);
  const cands = videos.map(v => ({ ...v, c: parseClip(v.name) })).filter(v => v.c && v.c.teacher === t).sort((a, b) => b.mtime - a.mtime);
  const dated = cands.find(v => v.c.kind === '쌤15초' && v.c.prefix === MMDD && genreOk(c.name, v.c.genre)) || cands.find(v => v.c.kind === '쌤15초' && v.c.prefix === MMDD);
  if (dated) return { file: dated.p, how: '날짜 파일' };
  const recent = cands.find(v => genreOk(c.name, v.c.genre)) || cands[0];
  if (recent) return { file: recent.p, how: '최근 영상' };
  return null;
}
function duration(file) {
  const r = run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', file]);
  return parseFloat(r.stdout) || 0;
}

// ---------- 2. 시간표 스토리 ----------
function timetable(videos) {
  // 미리 만든 시간표 영상(MMDD_시간표.mp4)이 RAW 영상공장 폴더에 있으면 그걸 먼저 쓴다 (2026-11-23 원장님이 직접 준 영상)
  const pre = videos.filter(v => v.name === `${MMDD}_시간표.mp4`).sort((a, b) => b.mtime - a.mtime)[0];
  if (pre) return { file: pre.p, how: '미리 만든 영상' };
  log('시간표 스토리 만드는 중 (render.js)…');
  const r = run('node', [path.join(__dirname, 'render.js'), date], { timeout: 15 * 60e3 });
  const file = path.join(ROOT, 'content', `${date}_daily-story`, 'story.mp4');
  if (!r.ok || !fs.existsSync(file)) throw new Error('시간표 영상 만들기 실패: ' + r.out.trim().split('\n').slice(-3).join(' / '));
  return { file, how: /음원 없음/.test(r.out) ? 'render.js (음원 없음 → 무음)' : 'render.js' };
}

// ---------- 5. Ego Lite 예약 ----------
function egoScript(items, check) {
  return `
const ITEMS = ${JSON.stringify(items)};
const DATE = ${JSON.stringify(date)};
const task = await taskSpace(${JSON.stringify(`스토리 예약 ${date} ${Date.now() % 1e6}`)});
const page = task.page("p1");
console.log("SPACE " + task.spaceId);
async function loggedIn() {
  await page.goto(${JSON.stringify(COMPOSER)}, { timeout: 60000 });
  try { await page.waitForSelector("text=사진/동영상 추가", { timeout: 40000 }); }
  catch (e) { throw new Error("스토리 만들기 화면이 안 열림 (Meta 로그인 확인): " + (await page.url())); }
  await page.waitForTimeout(1500);
  const line = ((await page.snapshot()).split("\\n").find(l => l.includes("공유 대상 ")) || "").trim();
  if (!/공유 대상 rawdance_suwon"/.test(line)) throw new Error("공유 대상이 rawdance_suwon이 아님: " + line);
}
async function one({ file, t }) {
  const H = +t.slice(0, 2), MM = t.slice(3), AP = H < 12 ? "오전" : "오후", H12 = H % 12 || 12;
  await loggedIn();
  const cp = page.waitForFileChooser({ timeout: 15000 });
  await page.click("text=사진/동영상 추가", { label: "add video" });
  await (await cp).setFiles(file);
  await page.click("loc=role:button[name='예약']", { label: "choose schedule" });
  await page.waitForSelector('input[placeholder="yyyy-mm-dd"]', { timeout: 15000 });
  await page.click('input[placeholder="yyyy-mm-dd"]', { label: "date field" });
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.type(DATE);
  await page.keyboard.press("Enter");
  await page.waitForTimeout(800);
  await page.click('input[aria-label="오전/오후"]', { label: "AM/PM field" });
  await page.keyboard.type(H < 12 ? "A" : "P");
  await page.click('input[aria-label="시간"]', { label: "hour field" });
  await page.keyboard.type(String(H12).padStart(2, "0"));
  await page.click('input[aria-label="분"]', { label: "minute field" });
  await page.keyboard.type(MM);
  await page.waitForTimeout(1000);
  for (let i = 0; i < 60; i++) { if (await page.evaluate(() => { const t = document.body.innerText; return !/미디어 (처리|업로드) 중/.test(t) && /0:\\d+\\s*초/.test(t); })) break; await page.waitForTimeout(5000); }
  const st = await page.evaluate(() => ({
    date: document.querySelector('input[placeholder="yyyy-mm-dd"]')?.value,
    time: document.querySelector('input[aria-label="오전/오후"]')?.closest('[role=application]')?.innerText.replace(/\\s+/g, ""),
    busy: /미디어 (처리|업로드) 중/.test(document.body.innerText),
    media: (document.body.innerText.match(/0:\\d+\\s*초/g) || []).length,
  }));
  const [y, m, d] = DATE.split("-").map(Number);
  const ok = st.date && st.date.includes(y + "년 " + m + "월 " + d + "일") && new RegExp("^" + AP + "0?" + H12 + ":" + MM + "$").test(st.time || "") && !st.busy && st.media === 1;
  if (!ok) throw new Error("예약 전 확인 실패 (예약 안 누름): " + JSON.stringify(st));
  await page.click("xpath=(//*[@role='button' or self::button][normalize-space(.)='예약'])[last()]", { label: "confirm schedule" });
  await page.waitForFunction(() => document.body.innerText.includes("예약되었습니다"), undefined, { timeout: 30000 });
}
try {
  if (${check ? 'true' : 'false'}) { await loggedIn(); console.log("CHECK_OK"); }
  else for (const it of ITEMS) { await one(it); console.log("SLOT_OK " + it.t); }
} catch (e) {
  const shot = await page.screenshot({ path: ${JSON.stringify(path.join(STATE_DIR, `fail-${date}.png`))} }).catch(() => "");
  console.log("FAIL " + e.message + (shot ? " | 화면: " + shot : ""));
  process.exit(1);
}
await page.goto(${JSON.stringify(PLANNER)}, { timeout: 60000 }).catch(() => {});
await task.finish({ keep: [] });
console.log("DONE");
`;
}

// ---------- 실행 ----------
(async () => {
  log(`===== ${date} 스토리 예약 시작 ${YES ? '(자동 --yes)' : ''}${CHECK ? '(점검만)' : ''}`);
  if (DOW === 6) { log('토요일은 하지 않음'); return; }
  fs.mkdirSync(STATE_DIR, { recursive: true });
  const statePath = path.join(STATE_DIR, `${date}.json`);
  const state = fs.existsSync(statePath) ? JSON.parse(fs.readFileSync(statePath, 'utf8')) : { slots: {} };
  const save = () => fs.writeFileSync(statePath, JSON.stringify(state, null, 1));

  if (!NO_UPDATE && !CHECK) update();

  const classes = plan();
  const videos = allVideos();
  if (!videos.length) log('⚠ RAW 영상공장 폴더에서 영상을 못 찾음 (폴더 권한 확인):', MOVIES);
  const done = s => !FORCE && state.slots[s];
  const rows = [];
  // 이미 다 예약한 날이면 시간표 영상은 다시 만들지 않는다
  const allDone = done(hhmm(AT_MIN)) && classes.every(c => done(hhmm(AT_MIN + c.min)));
  const tt = allDone ? { file: state.slots[hhmm(AT_MIN)], how: '' } : timetable(videos);
  rows.push({ min: 0, label: '시간표 스토리', teacher: '', ...tt });
  for (const c of classes) rows.push({ min: c.min, label: `${c.start} ${c.name}`, teacher: c.teacher, ...(findClip(videos, c) || { file: null, how: '영상 없음' }) });
  for (const r of rows) {
    r.slot = hhmm(AT_MIN + r.min);
    if (r.file && !done(r.slot)) { const s = duration(r.file); if (!s || s > 60) { r.how = `영상 길이 이상(${s.toFixed(1)}초) → 건너뜀`; r.file = null; } }
  }

  log(`\n${MD} (${['일','월','화','수','목','금','토'][DOW]}) 예약 표`);
  log('예약 시각 | 수업 | 쌤 | 파일');
  for (const r of rows) log(`${r.slot} | ${r.label} | ${r.teacher || '—'} | ${done(r.slot) ? '✅ 이미 예약됨' : r.file ? path.basename(r.file) + (r.how ? `  (${r.how})` : '') : '❌ ' + r.how}`);

  const todo = rows.filter(r => r.file && !done(r.slot));
  if (CHECK) {
    const r = run('ego-browser', ['nodejs'], { input: egoScript([], true), timeout: 5 * 60e3 });
    if (/CHECK_OK/.test(r.out)) { log('점검 OK: 영상·Meta 로그인 확인'); notify(`점검 OK: 영상 ${videos.length}개 보임 · Meta 로그인 OK`); }
    else { log('점검 실패:', r.out.trim().split('\n').slice(-3).join(' / ')); notify('스토리 예약 확인 필요 (점검 실패)'); process.exitCode = 1; }
    return;
  }
  if (!todo.length) { log('예약할 것 없음 (이미 예약됨)'); if (YES) notify(`${MD} 이미 예약돼 있음`); return; }
  if (!YES) {
    if (!process.stdin.isTTY) { log('확인 없이 예약하려면 --yes'); return; }
    const rl = require('readline').createInterface({ input: process.stdin, output: process.stdout });
    const a = await new Promise(res => rl.question(`\n위 ${todo.length}개를 @rawdance_suwon 스토리로 예약할까요? (y/n) `, res)); rl.close();
    if (!/^y/i.test(a.trim())) { log('예약 안 함 (원장님 취소)'); return; }
  }

  log(`Ego Lite로 ${todo.length}개 예약 중…`);
  const r = run('ego-browser', ['nodejs'], { input: egoScript(todo.map(t => ({ file: t.file, t: t.slot })), false), timeout: 40 * 60e3 });
  for (const m of r.out.matchAll(/^SLOT_OK (\d\d:\d\d)$/gm)) { const t = todo.find(x => x.slot === m[1]); if (t) state.slots[t.slot] = t.file; }
  save();
  const okN = [...r.out.matchAll(/^SLOT_OK /gm)].length;
  const skipped = rows.filter(x => !x.file).length;
  if (r.ok && okN === todo.length) {
    log(`완료: ${MD} 예약 ${okN}개${skipped ? ` (영상 없음 ${skipped}개 건너뜀)` : ''}`);
    notify(`${MD} 예약 ${okN}개 완료${skipped ? ` · 영상 없음 ${skipped}개` : ''}${/무음/.test(rows[0].how) ? ' · 시간표 무음' : ''}`);
  } else {
    const why = (r.out.match(/^FAIL (.+)$/m) || [, r.error ? r.error.message : r.out.trim().split('\n').slice(-2).join(' / ')])[1];
    log(`실패: ${okN}/${todo.length}개만 예약됨 →`, why);
    notify(`스토리 예약 확인 필요 (${MD} ${okN}/${todo.length}개)`);
    process.exitCode = 1;
  }
})().catch(e => { log('오류:', e.stack || e.message); notify('스토리 예약 확인 필요'); process.exitCode = 1; });
