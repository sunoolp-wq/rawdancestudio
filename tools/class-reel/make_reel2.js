// 수업 영상 → 15초 릴스·스토리 (RAW 스타일: 전체 화면 영상 + 강사 이름·장르 + 요일 칩 + 끝 화면)
// node make_reel2.js --video 원본.mp4 --start 32 --dur 15 --name KIRY --genre JAZZ --when "WED 20:50" --whenKr "매주 수 20:50" [--hall A] [--track "곡"] [--kicker "POP-UP CLASS"] --out 결과.mp4
const { renderToVideo } = require('../pw.js');
const { spawn } = require('child_process'); const path = require('path'); const fs = require('fs'), os = require('os');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const START = +(A.start || 0), DUR = +(A.dur || 15), END = 2.0, FPS = 30, TOT = DUR + END;
(async () => {
  const graph = [
    `[0:v]setpts=PTS-STARTPTS,fps=${FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v]`,
    // 끝 화면 2초: 검은 바탕(전체 길이)에 영상(끝나면 마지막 장면 유지) → 그 위에 글자·끝 화면. tpad는 파이프가 느리면 끝 2초가 잘림(2026-11-06)
    `color=c=black:s=1080x1920:r=${FPS}:d=${TOT},format=yuv420p[bg]`, `[bg][v]overlay=0:0:eof_action=repeat[bv]`,
    `[1:v]format=rgba[o]`, `[bv][o]overlay=0:0:format=auto:eof_action=repeat,format=yuv420p[vout]`,
    `[0:a]atrim=duration=${DUR},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.3,afade=t=out:st=${DUR - 1.2}:d=1.2,apad=pad_dur=${END}[aout]`].join(';');
  // 장면을 여러 탭에서 동시에 그려 임시 폴더에 저장 → ffmpeg로 합침 (원장님 2026-11-17 속도·맥 멈춤)
  // 원본은 -ss/-t로 필요한 구간만 읽음 (4K 앞부분을 처음부터 풀지 않아 빠름)
  await renderToVideo({ file: path.join(__dirname, 'style2.html'), n: Math.round(TOT * FPS), fps: FPS,
    setupArg: { name: A.name, genre: A.genre, when: A.when, whenKr: A.whenKr || A.when, hall: A.hall, track: A.track, kicker: A.kicker, dur: DUR },
    ffArgs: seq => ['-y', '-v', 'error', '-ss', String(START), '-t', String(DUR), '-i', A.video, '-framerate', String(FPS), '-i', seq,
      '-filter_complex', graph, '-map', '[vout]', '-map', '[aout]', '-t', String(TOT),
      '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', A.out] });
  console.log(A.out);
})();
