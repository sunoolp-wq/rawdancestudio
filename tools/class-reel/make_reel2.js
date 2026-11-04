// 수업 영상 → 15초 릴스·스토리 (RAW 스타일: 전체 화면 영상 + 강사 이름·장르 + 요일 칩 + 끝 화면)
// node make_reel2.js --video 원본.mp4 --start 32 --dur 15 --name KIRY --genre JAZZ --when "WED 20:50" --whenKr "매주 수 20:50" [--hall A] [--track "곡"] --out 결과.mp4
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const { spawn } = require('child_process'); const path = require('path');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const START = +(A.start || 0), DUR = +(A.dur || 15), END = 2.0, FPS = 30, TOT = DUR + END;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'style2.html'));
  await p.evaluate(o => window.setup(o), { name: A.name, genre: A.genre, when: A.when, whenKr: A.whenKr || A.when, hall: A.hall, track: A.track, dur: DUR });
  await p.evaluate(() => document.fonts.ready);
  const graph = [
    `[0:v]trim=start=${START}:duration=${DUR},setpts=PTS-STARTPTS,fps=${FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,tpad=stop_mode=clone:stop_duration=${END}[v]`,
    `[1:v]format=rgba[o]`, `[v][o]overlay=0:0:format=auto,format=yuv420p[vout]`,
    `[0:a]atrim=start=${START}:duration=${DUR},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.3,afade=t=out:st=${DUR - 1.2}:d=1.2,apad=pad_dur=${END}[aout]`].join(';');
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-i', A.video, '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-filter_complex', graph, '-map', '[vout]', '-map', '[aout]', '-t', String(TOT),
    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', A.out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < TOT * FPS; f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const buf = await p.screenshot({ type: 'png', omitBackground: true });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log(A.out);
})();
