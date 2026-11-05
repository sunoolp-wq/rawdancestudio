// 영상 첫 부분에 TRACKPAD 느낌 제목(수업명 + 강사, 곡명은 선택)만 얹기. 나머지는 손대지 않음.
// node add_title.js --video 세로.mp4 --title "KIDZ K-POP" --name MINKYUNG [--track "곡"] [--y 820] --out 결과.mp4
const { launch } = require('../pw.js'); const { spawn } = require('child_process'); const path = require('path');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const { execFileSync } = require('child_process');
const T = 5.0;
(async () => {
  const fr = execFileSync('ffprobe', ['-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0', A.video]).toString().trim();
  const [fn, fd] = fr.split('/').map(Number); const FPS = fn / (fd || 1);
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'title.html'));
  await p.evaluate(o => window.setup(o), { title: A.title, name: A.name, track: A.track, y: A.y ? +A.y : undefined });
  await p.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-i', A.video, '-f', 'image2pipe', '-framerate', fr, '-c:v', 'png', '-i', '-',
    '-filter_complex', `[0:v]scale=1080:1920,setsar=1[v];[1:v]format=rgba[o];[v][o]overlay=0:0:eof_action=pass,format=yuv420p,setsar=1[vout]`,
    '-map', '[vout]', '-map', '0:a?', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', A.out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < Math.round(T * FPS); f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const buf = await p.screenshot({ type: 'png', omitBackground: true });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log(A.out);
})();
