// 영상 첫 부분에 TRACKPAD 느낌 제목(수업명 + 강사, 곡명은 선택)만 얹기. 나머지는 손대지 않음.
// node add_title.js --video 세로.mp4 --title "KIDZ K-POP" --name MINKYUNG [--track "곡"] [--y 820] --out 결과.mp4
const { renderToVideo } = require('../pw.js'); const fs = require('fs'), os = require('os'); const { spawn } = require('child_process'); const path = require('path');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const { execFileSync } = require('child_process');
const T = 5.0; const AT = +(A.at || 0);   // 자막 시작 시각(초). --end 를 주면 자막이 그 시각에 끝나도록 자동 계산
if (A.end) A.at = Math.max(0, +A.end - 4.96);
(async () => {
  const fr = execFileSync('ffprobe', ['-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0', A.video]).toString().trim();
  const [fn, fd] = fr.split('/').map(Number); const FPS = fn / (fd || 1);
  await renderToVideo({ file: path.join(__dirname, 'title.html'), n: Math.round(T * FPS), fps: FPS,
    setupArg: { title: A.title, name: A.name, track: A.track, y: A.y ? +A.y : undefined, trkdy: A.trkdy ? +A.trkdy : 0 },
    ffArgs: seq => ['-y', '-v', 'error', '-i', A.video, '-framerate', fr, '-i', seq,
      '-filter_complex', `[0:v]scale=1080:1920,setsar=1[v];[1:v]format=rgba,setpts=PTS+${+(A.at||0)}/TB[o];[v][o]overlay=0:0:eof_action=pass,format=yuv420p,setsar=1[vout]`,
      '-map', '[vout]', '-map', '0:a?', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', A.out] });
  console.log(A.out);
})();
