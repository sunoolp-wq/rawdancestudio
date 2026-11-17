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
