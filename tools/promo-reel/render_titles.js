// 이어 붙인 세로 영상 위에 자막 얹기. 사용: node render_titles.js --video base.mp4 --cues cues.json --out 결과.mp4 [--html titles2.html --plan plan.json]
// --preview 1.2,5.5,... 를 주면 영상 대신 그 시각들의 미리보기 PNG를 --out 폴더에 저장
const { launch } = require('../pw.js'); const { spawn, execFileSync } = require('child_process'); const path = require('path'); const fs = require('fs');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
(async () => {
  const fr = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,nb_frames', '-of', 'csv=p=0', A.video]).toString().trim().split(',');
  const [fn, fd] = fr[0].split('/').map(Number), FPS = fn / fd, N = +fr[1];
  const cues = JSON.parse(fs.readFileSync(A.cues, 'utf8'));
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, A.html || 'titles.html'));
  const plan = A.plan ? JSON.parse(fs.readFileSync(A.plan, 'utf8')) : null;
  const cuts = plan ? plan.segments.map(s => s.t0) : [], END = plan ? plan.end : 1e9;
  await p.evaluate(([c, k, e]) => window.setup(c, k, e), [cues, cuts, END]); await p.evaluate(() => document.fonts.ready);
  if (A.preview) {   // 미리보기: 그 시각의 영상 프레임 + 자막 → PNG
    fs.mkdirSync(A.out, { recursive: true });
    for (const t of A.preview.split(',').map(Number)) {
      await p.evaluate(x => window.render(x), t); const ov = path.join(A.out, `ov_${t}.png`); await p.screenshot({ path: ov, omitBackground: true });
      execFileSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(t), '-i', A.video, '-i', ov, '-filter_complex', '[0:v][1:v]overlay', '-frames:v', '1', path.join(A.out, `pv_${String(t).padStart(5, '0')}.png`)]);
    }
    await b.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-i', A.video, '-f', 'image2pipe', '-framerate', fr[0], '-c:v', 'png', '-i', '-',
    '-filter_complex', '[1:v]format=rgba[o];[0:v][o]overlay=0:0:eof_action=pass,format=yuv420p,setsar=1[v]', '-map', '[v]',
    '-c:v', 'libx264', '-crf', '15', '-preset', 'slow', '-r', fr[0], '-an', A.out], { stdio: ['pipe', 'inherit', 'inherit'] });
  let empty = null;
  for (let f = 0; f < N; f++) {
    const t = f / FPS, has = A.html ? true : cues.some(c => t >= c.a && t < c.b);
    let buf;
    if (!has && empty) buf = empty;
    else { await p.evaluate(x => window.render(x), t); buf = await p.screenshot({ type: 'png', omitBackground: true }); if (!has) empty = buf; }
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log(A.out);
})();
