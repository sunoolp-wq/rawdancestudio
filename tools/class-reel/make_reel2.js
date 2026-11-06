// 수업 영상 → 15초 릴스·스토리 (RAW 스타일: 전체 화면 영상 + 강사 이름·장르 + 요일 칩 + 끝 화면)
// node make_reel2.js --video 원본.mp4 --start 32 --dur 15 --name KIRY --genre JAZZ --when "WED 20:50" --whenKr "매주 수 20:50" [--hall A] [--track "곡"] [--kicker "POP-UP CLASS"] --out 결과.mp4
const { launch } = require('../pw.js');
const { spawn } = require('child_process'); const path = require('path');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const START = +(A.start || 0), DUR = +(A.dur || 15), END = 2.0, FPS = 30, TOT = DUR + END;
(async () => {
  const b = await launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'style2.html'));
  await p.evaluate(o => window.setup(o), { name: A.name, genre: A.genre, when: A.when, whenKr: A.whenKr || A.when, hall: A.hall, track: A.track, kicker: A.kicker, dur: DUR });
  await p.evaluate(() => document.fonts.ready);
  const graph = [
    `[0:v]trim=start=${START}:duration=${DUR},setpts=PTS-STARTPTS,fps=${FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v]`,
    // 끝 화면 2초: 검은 바탕(전체 길이)에 영상(끝나면 마지막 장면 유지) → 그 위에 글자·끝 화면. tpad는 파이프가 느리면 끝 2초가 잘림(2026-11-06)
    `color=c=black:s=1080x1920:r=${FPS}:d=${TOT},format=yuv420p[bg]`, `[bg][v]overlay=0:0:eof_action=repeat[bv]`,
    `[1:v]format=rgba[o]`, `[bv][o]overlay=0:0:format=auto:eof_action=repeat,format=yuv420p[vout]`,
    `[0:a]atrim=start=${START}:duration=${DUR},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.3,afade=t=out:st=${DUR - 1.2}:d=1.2,apad=pad_dur=${END}[aout]`].join(';');
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-i', A.video, '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-filter_complex', graph, '-map', '[vout]', '-map', '[aout]', '-t', String(TOT),
    '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', A.out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < TOT * FPS; f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const buf = await p.screenshot({ type: 'png', omitBackground: true });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log(A.out);
})();
