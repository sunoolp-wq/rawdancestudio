// 영상 첫 부분에 TRACKPAD 느낌 제목(수업명 + 강사, 곡명은 선택)을 얹고, 원하면 끝에 RAW 로고 엔딩.
// node add_title.js --video 세로.mp4 --title "KIDZ K-POP" --name MINKYUNG [--track "곡"] [--y 820] [--len 5] [--outro 2.5] --out 결과.mp4
//   --len   : 자막 길이(초, 1~5). 춤 시작 전 이 시간 동안 나오고 춤 시작에 딱 사라짐. 짧을수록 글자 켜지고 꺼지는 속도가 알아서 빨라짐 (원장님 2026-11-17)
//   --outro : 끝 로고 길이(초). 영상 마지막 이 시간 위에 검은 화면 + RAW 로고를 덮음. 소리는 영상 소리 그대로 이어짐 ("화면 전환되고도 음원이 이어지게")
//   --at / --end : 자막 시작 시각 / 자막이 끝나는 시각 (예전 방식)
const { renderFrames, ffmpeg } = require('../pw.js'); const fs = require('fs'), os = require('os'); const path = require('path');
const { execFileSync } = require('child_process');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const LEN = Math.min(5, Math.max(1, +(A.len || 5))), OUTRO = +(A.outro || 0);
//   --frames 폴더 --fps 30 --w 1920 --h 1080 : 자막 장면만 그려서 폴더에 저장하고 끝 (유튜브 이어붙이기가 한 번에 합칠 때 씀)
if (A.frames) {
  (async () => {
    const W = +(A.w || 1080), H = +(A.h || 1920), FPS = +(A.fps || 30);
    await renderFrames({ file: path.join(__dirname, 'title.html'), n: Math.round(LEN * FPS), fps: FPS, dir: A.frames, w: W, h: H,
      setupArg: { title: A.title, name: A.name, track: A.track, len: LEN, w: W, h: H } });
    console.log(A.frames);
  })();
  return;
}
if (A.end) A.at = Math.max(0, +A.end - LEN + 0.04);
const AT = +(A.at || 0);
const probe = (args) => execFileSync('ffprobe', ['-v', 'error', ...args, A.video]).toString().trim();
(async () => {
  const fr = probe(['-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0']);
  const [fn, fd] = fr.split('/').map(Number); const FPS = fn / (fd || 1);
  const VD = +probe(['-show_entries', 'format=duration', '-of', 'csv=p=0']);
  const hasA = probe(['-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0']) !== '';
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'raw-title-'));
  try {
    const seqT = await renderFrames({ file: path.join(__dirname, 'title.html'), n: Math.round(LEN * FPS), fps: FPS, dir: path.join(tmp, 't'),
      setupArg: { title: A.title, name: A.name, track: A.track, y: A.y ? +A.y : undefined, trkdy: A.trkdy ? +A.trkdy : 0, len: LEN } });
    const ins = ['-y', '-i', A.video, '-framerate', fr, '-i', seqT];
    let g = `[0:v]scale=1080:1920,setsar=1[v];[1:v]format=rgba,setpts=PTS+${AT}/TB[o];[v][o]overlay=0:0:eof_action=pass[v1]`, last = 'v1';
    if (OUTRO > 0) {
      const seqO = await renderFrames({ file: path.join(__dirname, 'outro.html'), n: Math.round(OUTRO * FPS), fps: FPS, dir: path.join(tmp, 'o') });
      ins.push('-framerate', fr, '-i', seqO);
      g += `;[2:v]format=rgba,setpts=PTS+${Math.max(0, VD - OUTRO).toFixed(3)}/TB[e];[v1][e]overlay=0:0:eof_action=repeat[v2]`; last = 'v2';
    }
    g += `;[${last}]format=yuv420p,setsar=1[vout]`;
    const aud = hasA ? ['-map', '0:a', '-af', `afade=t=out:st=${Math.max(0, VD - 1.5).toFixed(3)}:d=1.5`, '-c:a', 'aac', '-b:a', '256k'] : [];
    await ffmpeg([...ins, '-filter_complex', g, '-map', '[vout]', ...aud, '-t', VD.toFixed(3),
      '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-movflags', '+faststart', A.out], Math.round(VD * FPS));
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
  console.log(A.out);
})();
