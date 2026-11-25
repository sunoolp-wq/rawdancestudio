// node make_trailer.js → KIDZ_SEASON1_trailer.mp4 (20초, 무음. 음악 받으면 HITS를 곡 박자에 맞추고 음원 입힘)
const { renderFrames } = require('../../tools/pw.js');
const { execFileSync } = require('child_process'); const path = require('path'), fs = require('fs'), os = require('os');
(async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kidz-trailer-')), FPS = 30, SEC = 20;
  await renderFrames({ file: path.join(__dirname, 'trailer.html'), setupArg: {}, n: SEC * FPS, fps: FPS, dir });
  const out = path.join(__dirname, 'KIDZ_SEASON1_trailer.mp4');
  execFileSync('ffmpeg', ['-nostdin', '-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, '%05d.png'), '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
    '-map', '0:v', '-map', '1:a', '-t', String(SEC), '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', out]);
  fs.rmSync(dir, { recursive: true, force: true }); console.log(out);
})();
