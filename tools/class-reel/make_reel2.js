// 수업 영상 → 15초 릴스·스토리 (RAW 스타일: 전체 화면 영상 + 강사 이름·장르 + 요일 칩 + 끝 화면)
// node make_reel2.js --video 원본.mp4 --start 32 --dur 15 --name KIRY --genre JAZZ --when "WED 20:50" --whenKr "매주 수 20:50" [--hall A] [--track "곡"] [--kicker "POP-UP CLASS"] --out 결과.mp4
const { renderToVideo } = require('../pw.js');
const { spawn } = require('child_process'); const path = require('path'); const fs = require('fs'), os = require('os');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = a[i + 1]; });
const START = +(A.start || 0), DUR = +(A.dur || 15), END = 2.0, FPS = 30, TOT = DUR + END;
(async () => {
  const N = Math.round(TOT * FPS);
  // 장면을 여러 탭에서 동시에 그려 임시 폴더에 저장 → ffmpeg 두 단계로 합침 (원장님 2026-11-17 속도·맥 멈춤)
  // 한 번에 복잡하게 합치면 맥 최신 ffmpeg에서 '영상 합치는 중'에 멈춤 → 단순한 두 단계로 나눔
  await renderToVideo({ file: path.join(__dirname, 'style2.html'), n: N, fps: FPS,
    setupArg: { name: A.name, genre: A.genre, when: A.when, whenKr: A.whenKr || A.when, hall: A.hall, track: A.track, kicker: A.kicker, dur: DUR },
    steps: (seq, tmp) => {
      const base = path.join(tmp, 'base.mp4');
      return [
        // 1) 원본에서 필요한 구간만(-ss/-t) → 세로 1080x1920, 끝 2초는 마지막 장면 정지, 소리 페이드
        { label: '영상 준비 중', total: N, args: ['-y', '-ss', String(START), '-t', String(DUR), '-i', A.video,
          '-vf', `fps=${FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,tpad=stop_mode=clone:stop_duration=${END},format=yuv420p`,
          '-af', `afade=t=in:st=0:d=0.3,afade=t=out:st=${DUR - 1.2}:d=1.2,apad=pad_dur=${END}`,
          '-t', String(TOT), '-c:v', 'libx264', '-crf', '10', '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '320k', base] },
        // 2) 글자·끝 화면 장면을 얹기
        { label: '영상 합치는 중', total: N, args: ['-y', '-i', base, '-framerate', String(FPS), '-i', seq,
          '-filter_complex', '[1:v]format=rgba[o];[0:v][o]overlay=0:0:format=auto,format=yuv420p[vout]', '-map', '[vout]', '-map', '0:a', '-t', String(TOT),
          '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-c:a', 'copy', '-movflags', '+faststart', A.out] }];
    } });
  console.log(A.out);
})();
