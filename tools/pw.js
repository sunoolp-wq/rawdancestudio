// 클라우드·맥 어디서나 같은 코드로 크롬 띄우기
const fs = require('fs');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
const CLOUD = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
module.exports.launch = () => pw.chromium.launch(fs.existsSync(CLOUD) ? { executablePath: CLOUD, args: ['--no-sandbox'] } : {});

// 장면을 여러 탭에서 동시에 그려 파일로 저장 (원장님 2026-11-17 "꽤 오래 걸리는데": 한 장씩 순서대로 → 코어 수만큼 동시에)
// render(t)가 t에만 달린 화면(앞 장면 상태 없음)이어야 함: style2.html, title.html, template.html 확인함
module.exports.renderFrames = async ({ file, setupArg, n, fps, dir, type = 'png', omit = true, w = 1080, h = 1920, workers, check, pipe }) => {
  const path = require('path'), os = require('os');
  if (!pipe) fs.mkdirSync(dir, { recursive: true });
  // pipe: 순서대로 ffmpeg에 바로 넣음 (그리는 동안 영상도 같이 만들어짐). 먼저 끝난 장면은 순서 올 때까지 잠깐 보관
  const ready = new Map(); let wrote = 0;
  const flush = async () => { while (ready.has(wrote)) { const buf = ready.get(wrote); ready.delete(wrote); wrote++; if (!pipe.write(buf)) await new Promise(r => pipe.once('drain', r)); } };
  workers = +process.env.RAW_WORKERS || workers || Math.max(2, Math.min(8, os.cpus().length - 2));
  const b = await module.exports.launch(); let next = 0, done = 0;
  await Promise.all(Array.from({ length: workers }, async () => {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + file); await p.evaluate(o => window.setup(o), setupArg); await p.evaluate(() => document.fonts.ready);
    if (check) await check(p);
    for (;;) {
      const i = next++; if (i >= n) break;
      await p.evaluate(t => window.render(t), i / fps);
      const opt = { type, omitBackground: omit, ...(type === 'jpeg' ? { quality: 95 } : {}) };
      if (pipe) { while (i - wrote > workers * 4) await new Promise(r => setTimeout(r, 5)); ready.set(i, await p.screenshot(opt)); await flush(); }
      else await p.screenshot({ path: path.join(dir, String(i).padStart(5, '0') + (type === 'png' ? '.png' : '.jpg')), ...opt });
      if (++done % 60 === 0) console.log(`장면 ${done}/${n}`);
    }
  }));
  await b.close();
  if (pipe) { await flush(); pipe.end(); return null; }
  return path.join(dir, '%05d' + (type === 'png' ? '.png' : '.jpg'));
};

// ffmpeg 실행 + 진행 표시. 원장님 맥 2026-11-17: '영상 합치는 중'에서 멈춘 것처럼 보임 → 몇 장째인지 보여 줌
// total: 전체 장 수(진행 표시용), label: 표시 이름
module.exports.ffmpeg = (args, total, label = '영상 합치는 중') => new Promise((res, rej) => {
  const { spawn } = require('child_process');
  const ff = spawn('ffmpeg', ['-nostdin', '-hide_banner', '-v', 'error', '-nostats', '-progress', 'pipe:1', ...args], { stdio: ['ignore', 'pipe', 'inherit'] });
  let buf = '', shown = -1;
  ff.stdout.on('data', d => { buf += d; const m = [...buf.matchAll(/frame=(\d+)/g)]; buf = buf.slice(-200);
    if (m.length) { const f = +m[m.length - 1][1]; if (f - shown >= 60 || (total && f >= total && shown < total)) { shown = f; console.log(`${label} ${f}${total ? '/' + total : ''}`); } } });
  ff.on('close', c => c ? rej(new Error(`ffmpeg 실패 (${label})`)) : res());
  ff.on('error', () => rej(new Error('ffmpeg를 못 찾았어요')));
});

// 장면을 임시 폴더에 다 그린 뒤 ffmpeg로 합치기 (원장님 맥 2026-11-17 '장면 420/510'에서 멈춤:
// 그리면서 ffmpeg에 바로 넣는 방식(pipe)이 맥 ffmpeg·node 최신판에서 서로 기다리다 멈춤 → 파이프 없이 파일로)
// steps(seq, tmp): seq = '임시폴더/%05d.png', tmp = 임시 폴더 → [{args, total, label}, ...] 순서대로 실행
module.exports.renderToVideo = async ({ steps, type = 'png', ...o }) => {
  const os = require('os'), path = require('path');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'raw-frames-'));
  try {
    const seq = await module.exports.renderFrames({ ...o, type, dir: path.join(dir, 'f') });
    for (const st of steps(seq, dir)) await module.exports.ffmpeg(st.args, st.total, st.label);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
};
