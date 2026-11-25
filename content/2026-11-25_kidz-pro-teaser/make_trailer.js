// node make_trailer.js [음원.wav] → KIDZ_SEASON1_trailer.mp4 (22.5초. 음원 주면 처음부터 깔고 끝 1.5초 페이드, 없으면 무음)
const { renderFrames } = require('../../tools/pw.js');
const { execFileSync } = require('child_process'); const path = require('path'), fs = require('fs'), os = require('os');
(async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kidz-trailer-')), FPS = 30, SEC = 22.5, MUS = process.argv[2];
  await renderFrames({ file: path.join(__dirname, 'trailer.html'), setupArg: {}, n: SEC * FPS, fps: FPS, dir });
  const out = path.join(__dirname, 'KIDZ_SEASON1_trailer.mp4');
  execFileSync('ffmpeg', ['-nostdin', '-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, '%05d.png'), ...(MUS ? ['-i', MUS] : ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']),
    '-map', '0:v', '-map', '1:a', '-t', String(SEC), ...(MUS ? ['-af', `afade=t=out:st=${SEC - 1.5}:d=1.5`] : []), '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out]);
  fs.rmSync(dir, { recursive: true, force: true }); console.log(out);
})();
