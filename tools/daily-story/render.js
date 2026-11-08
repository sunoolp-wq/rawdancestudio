// 사용: node render.js 2026-11-05 [초=15] → content/2026-11-05_daily-story/story.mp4
const { launch } = require('../pw.js');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const dateStr = process.argv[2]; const SEC = +(process.argv[3] || 15); const FPS = 30;
if (!dateStr) { console.error('날짜를 넣어 주세요: node render.js 2026-11-05'); process.exit(1); }
const [Y, M, Dd] = dateStr.split('-').map(Number);
const dt = new Date(Date.UTC(Y, M - 1, Dd));
const DOW = ['SUN','MON','TUE','WED','THU','FRI','SAT'][dt.getUTCDay()];
const KR = {MON:'월요일',TUE:'화요일',WED:'수요일',THU:'목요일',FRI:'금요일',SAT:'토요일',SUN:'일요일'}[DOW];
const sched = JSON.parse(fs.readFileSync(path.join(__dirname, `schedule-${Y}-${String(M).padStart(2,'0')}.json`)));
let classes = sched.days[DOW] || [];
const extraPath = path.join(__dirname, 'extra.json');   // 날짜별 추가·변경 (대강, 팝업, 휴강)
if (fs.existsSync(extraPath)) {
  const ex = JSON.parse(fs.readFileSync(extraPath))[dateStr];
  if (ex) {
    if (ex.replace) classes = classes.map(c => ex.replace.find(r => r.start === c.start && r.name === c.name) ? { ...c, ...ex.replace.find(r => r.start === c.start && r.name === c.name).set } : c);
    if (ex.remove) classes = classes.filter(c => !ex.remove.some(r => r.start === c.start && r.name === c.name));
    if (ex.add) classes = classes.concat(ex.add);
    classes.sort((a, b) => a.start.localeCompare(b.start));
  }
}
if (!classes.length) { console.error(`${dateStr} (${DOW}) 수업 없음`); process.exit(1); }
const data = { dow: DOW, md: `${String(M).padStart(2,'0')}.${String(Dd).padStart(2,'0')}`, year: String(Y), krday: KR, classes };
const outDir = path.join(__dirname, '../../content', `${dateStr}_daily-story`); fs.mkdirSync(outDir, { recursive: true });
const out = path.join(outDir, 'story.mp4');
(async () => {
  const b = await launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'template.html'));
  await p.evaluate(d => window.setup(d), data);
  await p.evaluate(() => document.fonts.ready);
  // 글꼴이 없으면 명조체로 나옴(2026-11-07 사고) → 만들지 않고 멈춘다. 해결: bash tools/fonts/install.sh
  const miss = require('child_process').execSync('fc-list : family').toString();
  for (const f of ['Noto Sans KR', 'Montserrat']) if (!miss.includes(f)) { console.error(`글꼴 없음: ${f} → bash tools/fonts/install.sh 먼저`); process.exit(1); }
  // 음악: music.json {"file": "music/xxx.mp3", "start": 초} 또는 날짜별 {"2026-11-05": {...}} / 없으면 무음
  let mus = null; const mp = path.join(__dirname, 'music.json');
  if (fs.existsSync(mp)) { const mj = JSON.parse(fs.readFileSync(mp)); mus = mj[dateStr] || mj.default || null; }
  const audioIn = mus ? ['-ss', String(mus.start || 0), '-i', path.join(__dirname, mus.file)] : ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo'];
  const af = mus ? ['-af', `afade=t=in:st=0:d=0.4,afade=t=out:st=${SEC - 1.2}:d=1.2,volume=${mus.volume || 1}`] : [];
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    ...audioIn, '-map', '0:v', '-map', '1:a', '-t', String(SEC), ...af,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out]);
  for (let f = 0; f < SEC * FPS; f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  await p; console.log(out);
})();
