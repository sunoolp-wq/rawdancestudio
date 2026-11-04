// 수업 영상 → 15초 릴스/스토리 (원장님 편집 스타일: 액자 + 강사 이름 + 요일·시간 스티커 + 장르 테이프 + 끝 로고)
// 사용: node make_reel.js --video 원본.mp4 --start 32 --dur 15 --name KIRY --genre JAZZ --when "WED 20:50" --out 결과.mp4
const { launch } = require('../pw.js');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const START = +(A.start || 0), DUR = +(A.dur || 15), END = 1.2;
const box = { x: 183, y: 450, w: 714, h: 990 };
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'reel-'));
const P = 420, ANG = 10 * Math.PI / 180;
(async () => {
  const b = await launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'layers.html'));
  const shot = async (kind, o, file, w, h) => {
    await p.setViewportSize({ width: w, height: h });
    await p.evaluate(([k, o]) => window.build(k, o), [kind, o]);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(tmp, file), omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
  };
  const o = { box, name: A.name, genre: A.genre, when: A.when };
  await shot('bg', o, 'bg.png', 1080, 1920);
  await shot('fg', o, 'fg.png', 1080, 1920);
  await shot('tape', { genre: A.genre, P, len: 1080 + 2 * P + 400 }, 'tape.png', 1080 + 2 * P + 400, 120);
  await shot('end', o, 'end.png', 1080, 1920);
  await b.close();
  const f = (n) => path.join(tmp, n);
  // 테이프 2: 기울인 버전 (ffmpeg rotate)
  const T1Y = box.y + box.h + 70, T2Y = T1Y + 60;
  const graph = [
    `[1:v]trim=start=${START}:duration=${DUR},setpts=PTS-STARTPTS,fps=30,scale=${box.w}:${box.h}:force_original_aspect_ratio=increase,crop=${box.w}:${box.h}[v]`,
    `[0:v][v]overlay=${box.x}:${box.y}:shortest=1[a]`,
    `[3:v]split[t1][t2s]`,
    `[t2s]format=rgba,rotate=-${ANG}:ow=rotw(${ANG}):oh=roth(${ANG}):c=none[t2]`,
    `[a][t1]overlay=x='-mod(t*70\\,${P})':y=${T1Y}:shortest=1[b]`,
    `[b][t2]overlay=x='-200-mod(t*55\\,${P})*cos(${ANG})':y='${T2Y - 120}+mod(t*55\\,${P})*sin(${ANG})':shortest=1[c]`,
    `[c][2:v]overlay=0:0:shortest=1,fade=t=in:st=0:d=0.35,format=yuv420p[main]`,
    `[4:v]trim=duration=${END},setpts=PTS-STARTPTS,fps=30,format=yuv420p[endv]`,
    `[main][endv]xfade=transition=fade:duration=0.35:offset=${DUR - 0.35}[vout]`,
    `[1:a]atrim=start=${START}:duration=${DUR},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.3,afade=t=out:st=${DUR - 1.0}:d=1.0,apad=pad_dur=${END}[aout]`,
  ].join(';');
  execFileSync('ffmpeg', ['-y', '-v', 'error',
    '-loop', '1', '-framerate', '30', '-i', f('bg.png'), '-i', A.video,
    '-loop', '1', '-framerate', '30', '-i', f('fg.png'), '-loop', '1', '-framerate', '30', '-i', f('tape.png'),
    '-loop', '1', '-framerate', '30', '-i', f('end.png'),
    '-filter_complex', graph, '-map', '[vout]', '-map', '[aout]', '-t', String(DUR - 0.35 + END),
    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', A.out], { stdio: 'inherit' });
  console.log(A.out);
})();
