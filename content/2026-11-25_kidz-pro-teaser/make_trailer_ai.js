// RAW_AD=1 node make_trailer_ai.js … → 광고용(_ad: 끝 화면을 광고 가림 영역 밖으로, 상담 줄 뺌)
// node make_trailer_ai.js <A|C> <음원.wav> <AI영상폴더> [bg] → KIDZ_SEASON1_trailer_<V>_ai.mp4
// 원장님 2026-11-25: Gemini(Veo)로 만든 AI 영상을 "AI 티 안 나게 뒷배경으로 어둡게" → 어둡게·붉은 톤·살짝 흐림·필름 입자·비네팅 후 글자 카드 뒤에 깔기
// 컷은 쾅(번쩍) 시각에 바꿔서 번쩍 효과가 이음새를 가림. RAW_PREVIEW=1 이면 540×960 미리보기
const { renderFrames } = require('../../tools/pw.js');
const { execFileSync } = require('child_process'); const path = require('path'), fs = require('fs'), os = require('os');
const V = process.argv[2] || 'A', MUS = process.argv[3], AI = process.argv[4];
const PV = !!process.env.RAW_PREVIEW, W = PV ? 540 : 1080, H = PV ? 960 : 1920, FPS = 30, SEC = 22.5;
// [파일, 원본 시작초, 길이(초), 밝기(낮을수록 어두움), 속도(1=그대로, 0.7=느리게)] — 시각은 trailer.html CARDS·T_TITLE과 같음
// [파일, 원본 시작초, 길이(초), 밝기, 속도(0.7=느리게), 확대, 가로 기준(0왼~1오), 세로 기준]
// 구간은 원장님 11-25 "이상한 부분도 꽤 있거덩" → 0.5초씩 보고 이상한 곳 뺌 (아래 메모)
// 2차 (원장님 11-25 "1번으로"): 사람 나오는 AI 장면(운동화·아이 실루엣·발·팀 대형) 전부 뺌 — 실제 장면처럼 보이면 'AI 정보' 표시가 필요하고,
// 개강 전 반이 수업 중인 것처럼 보일 수 있음 → 연출 배경 3개(커튼 스포트라이트·큰 무대 조명·불꽃/붉은 연기)만, 구간·각도를 바꿔 씀
const SEG_BG = [
  ['gemini_c866cea3.mp4', 2.0, 4.16, 0.50, 1, 1.08, 0.5, 0.5],     // 0~4.66 첫 화면: 커튼 앞 스포트라이트 전체 (0~1.5초 테두리 이상 → 2초부터)
  ['Stage_lights.mp4', 3.0, 2.09, 0.42, 1, 1.35, 0.25, 0.3],       // 4.66~6.75 무대 조명 왼쪽 가까이 (1~2.5초 조명 V자 이상 → 3초부터)
  ['gemini_c866cea3.mp4', 6.2, 3.14, 0.45, 1, 1.45, 0.1, 0.12],    // 6.75~9.89 스포트라이트 빛줄기 위쪽 가까이 (연기 흐름)
  ['Stage_lights.mp4', 5.3, 1.82, 0.40, 0.88, 1.25, 0.85, 0.3],    // 9.89~11.71 무대 조명 오른쪽 가까이
  ['gemini_c866cea3.mp4', 9.4, 0.79, 0.45, 1, 1.7, 0.6, 0.78],     // 11.71~12.50 바닥 동그란 조명 가까이
  ['Stage_lights.mp4', 6.95, 0.91, 0.42, 1, 1.1, 0.5, 0.4],        // 12.50~13.41 큰 무대 전체 (아래 스피커는 시네마 바에 가림)
  ['Red_smoke.mp4', 0.6, 9.09, 0.38, 0.7, 1.12, 0.5, 0.5],         // 13.41~ RAW KIDZ 뒤 불꽃→붉은 연기 (왼쪽 검은 홈 가리게 확대)
];
// 3차 (원장님 11-25 "사람 있는 걸로 해줘 그냥" → 'AI 정보' 표시 켜고 올림): 기본 = 사람 장면 버전. 5번째 인자 bg 면 연출 배경만
const SEG_PEOPLE = [
  ['gemini_c866cea3.mp4', 2.0, 4.16, 0.50, 1, 1.08, 0.5, 0.5],          // 0~4.66 첫 화면: 커튼 스포트라이트 (0~1.5초 테두리 이상, 6.5초~ 흰 점 → 2.0~6.2만)
  ['gemini_13420bdf.mp4', 7.0, 2.09, 0.45, 1, 1.32, 0.72, 0.62],        // 4.66~6.75 흰 운동화 (뒤쪽 떠 있는 다리 가리게 오른쪽 확대, 5초쯤 발 꺾임 피함)
  ['Child_dancer_standing_in_room.mp4', 0.3, 3.14, 0.42, 0.8, 1.05, 0.5, 0.5], // 6.75~9.89 아이 실루엣 (5초~ 팔이 녹아내림 → 앞 2.5초만 느리게)
  ['Children_dancing_in_practice_room.mp4', 3.0, 1.82, 0.40, 1, 1.1, 0.5, 0.5], // 9.89~11.71 연습실 발 (1초 공중 발·5초~ 발 뭉개짐 피함)
  ['Children_dancers_standing_on_stage.mp4', 1.5, 0.79, 0.42, 1, 1.08, 0.5, 0.5], // 11.71~12.50 팀 대형 (6.5초~ 몸 모양 이상)
  ['Stage_lights.mp4', 4.4, 0.91, 0.42, 1, 1.1, 0.5, 0.4],             // 12.50~13.41 큰 무대 (1~2.5초 조명 V자 이상, 아래 스피커 녹음은 시네마 바에 가림)
  ['Red_smoke.mp4', 0.6, 9.09, 0.38, 0.7, 1.12, 0.5, 0.5],             // 13.41~ RAW KIDZ 뒤 불꽃→붉은 연기 (왼쪽 검은 홈 가리게 확대)
];
const SEG = process.argv[5] === 'bg' ? SEG_BG : SEG_PEOPLE;
(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'kidz-ai-')); const bg = path.join(tmp, 'bg.mp4');
  const inputs = [], fl = [];
  SEG.forEach(([f, ss, d, br, sp, k, cx, cy], i) => {
    inputs.push('-ss', String(ss), '-t', String(d * sp + 0.2), '-i', path.join(AI, f));
    // 어둡게 + 채도 낮추고 붉은 톤 + 살짝 흐림(AI 디테일 숨김) + 비네팅 + 필름 입자
    fl.push(`[${i}:v]setpts=PTS/${sp},fps=${FPS},scale=${Math.round(W * k / 2) * 2}:${Math.round(H * k / 2) * 2}:force_original_aspect_ratio=increase,crop=${W}:${H}:(iw-${W})*${cx}:(ih-${H})*${cy},` +
      `eq=saturation=0.55:contrast=1.12,colorchannelmixer=rr=1.0:gg=0.72:bb=0.72,colorchannelmixer=rr=${br}:gg=${br}:bb=${br},` +
      `gblur=sigma=${PV ? 1.2 : 2.4},vignette=angle=PI/3.2,noise=alls=${PV ? 6 : 10}:allf=t,trim=duration=${d},setpts=PTS-STARTPTS[s${i}]`);
  });
  fl.push(SEG.map((_, i) => `[s${i}]`).join('') + `concat=n=${SEG.length}:v=1:a=0,format=yuv420p[v]`);
  execFileSync('ffmpeg', ['-nostdin', '-v', 'error', '-y', ...inputs, '-filter_complex', fl.join(';'), '-map', '[v]', '-t', String(SEC), '-c:v', 'libx264', '-crf', '14', bg]);
  const dir = path.join(tmp, 'f');
  await renderFrames({ file: path.join(__dirname, 'trailer.html'), setupArg: { v: V, overlay: true, ad: !!process.env.RAW_AD }, n: SEC * FPS, fps: FPS, dir });
  const out = path.join(__dirname, `KIDZ_SEASON1_trailer_${V}_ai${process.env.RAW_AD ? '_ad' : ''}${PV ? '_preview' : ''}.mp4`);
  execFileSync('ffmpeg', ['-nostdin', '-v', 'error', '-y', '-i', bg, '-framerate', String(FPS), '-i', path.join(dir, '%05d.png'), '-i', MUS,
    '-filter_complex', `[1:v]scale=${W}:${H}[o];[0:v][o]overlay=0:0:format=auto[v]`, '-map', '[v]', '-map', '2:a', '-t', String(SEC),
    '-af', `afade=t=out:st=${SEC - 1.5}:d=1.5`, '-c:v', 'libx264', '-crf', PV ? '20' : '17', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out]);
  fs.rmSync(tmp, { recursive: true, force: true }); console.log(out);
})();
