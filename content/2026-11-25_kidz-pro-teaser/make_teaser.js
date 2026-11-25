// node make_teaser.js → KIDZ_SEASON1_teaser.mp4 (11초, 무음 — 음악은 인스타 앱에서 직접 넣기)
const { renderFrames } = require('../../tools/pw.js');
const { execFileSync } = require('child_process'); const path = require('path'), fs = require('fs'), os = require('os');
(async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kidz-teaser-')), FPS = 30, SEC = 11;
  await renderFrames({ file: path.join(__dirname, 'teaser.html'), setupArg: {}, n: SEC * FPS, fps: FPS, dir });
  const out = path.join(__dirname, 'KIDZ_SEASON1_teaser.mp4');
  execFileSync('ffmpeg', ['-nostdin', '-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, '%05d.png'), '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
    '-map', '0:v', '-map', '1:a', '-t', String(SEC), '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', out]);
  fs.rmSync(dir, { recursive: true, force: true }); console.log(out);
})();
