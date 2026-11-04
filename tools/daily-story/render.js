// 사용: node render.js 2026-11-05 [초=15] → content/2026-11-05_daily-story/story.mp4
const { chromium } = require('/opt/node-tools/node_modules/playwright');
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
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'template.html'));
  await p.evaluate(d => window.setup(d), data);
  await p.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-movflags', '+faststart', out]);
  for (let f = 0; f < SEC * FPS; f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  await p; console.log(out);
})();
