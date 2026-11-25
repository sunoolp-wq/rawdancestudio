// 화면 글자 검수 (원장님 2026-11-25 "글자 배치 전체적으로 손봐줘, 불편한 부분들이 있네" / "35초경에 로고가 갑자기")
// HTML 오버레이(window.setup + window.render(t))를 여러 시각에 그려서, 보이는 글자마다 위치를 재고 문제를 찾는다.
// 사용: node tools/video-kit/qa_html.js --file 화면.html [--arg '{"v":"A"}'] [--dur 22.5 --step 0.5 | --times 1,2.5,4] [--safe reels|reels-ad|story|none] [--out 폴더]
// 일부러 겹친 글자(예: 제목 위 SEASON 1 띠)는 그 요소에 data-qa="overlay" 를 붙이면 겹침 검사에서 빠짐
// 등급: fix = 고쳐야 함(잘림·겹침·가림) / check = 눈으로 확인(붙어 보임·작은 글씨 — 글자 상자가 실제 글자보다 클 수 있음)
// 찾는 것: ① 화면 밖으로 나감(잘림) ② 서로 다른 글자 덩어리끼리 겹침 ③ 인스타 화면 버튼·캡션에 가리는 자리(safe) ④ 너무 작은 글씨(18px 미만)
// 결과: <out>/qa-report.json + <out>/qa-sheet.jpg (문제 시각에 빨간 상자)
const path = require('path'), fs = require('fs');
const { launch } = require('../pw.js');
const A = {}; process.argv.slice(2).forEach((v, i, a) => { if (v.startsWith('--')) A[v.slice(2)] = (a[i + 1] && !a[i + 1].startsWith('--')) ? a[i + 1] : true; });
if (!A.file) { console.error('--file 필요'); process.exit(1); }
const W = +(A.w || 1080), H = +(A.h || 1920);
// 가림 영역(px): 인스타 릴스 기본 화면 = 위 220(계정·음악), 아래 340(캡션·버튼), 오른쪽 아래 버튼 줄 140 / 광고 릴스 = Meta 권장 위 14%·아래 35%
const SAFE = { reels: { top: 220, bottom: 340, right: 110, rightFrom: 0.6 }, 'reels-ad': { top: 270, bottom: 670, right: 110, rightFrom: 0.6 }, story: { top: 250, bottom: 250, right: 0, rightFrom: 1 }, none: null }[A.safe || 'reels'];
const times = A.times ? String(A.times).split(',').map(Number) : Array.from({ length: Math.floor(+(A.dur || 10) / +(A.step || 0.5)) + 1 }, (_, i) => +(i * +(A.step || 0.5)).toFixed(2));
const out = A.out || path.join(path.dirname(A.file), 'qa'); fs.mkdirSync(out, { recursive: true });
(async () => {
  const b = await launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto(require('url').pathToFileURL(path.resolve(A.file)).href);
  await p.evaluate(o => window.setup && window.setup(o), A.arg ? JSON.parse(A.arg) : {}); await p.evaluate(() => document.fonts.ready);
  const report = [], shots = [];
  for (const t of times) {
    await p.evaluate(t => window.render && window.render(t), t);
    const boxes = await p.evaluate(() => {
      const op = el => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +cs.opacity; } return o; };
      const out = [];
      document.querySelectorAll('body *').forEach(el => {
        const own = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).map(n => n.textContent.trim()).join(' ');
        if (!own) return; const o = op(el); if (o < 0.15) return;
        // 글자 실제 범위 (줄마다) → 합친 상자
        // 자기 글자(텍스트 노드)만 잼 — 범위 전체를 재면 안에 있는 블록 요소 상자(가로 꽉 참)까지 들어감
        const rs = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).flatMap(n => { const r = document.createRange(); r.selectNodeContents(n); return [...r.getClientRects()]; }).filter(q => q.width > 1 && q.height > 1);
        if (!rs.length) return;
        const x0 = Math.min(...rs.map(q => q.left)), y0 = Math.min(...rs.map(q => q.top)), x1 = Math.max(...rs.map(q => q.right)), y1 = Math.max(...rs.map(q => q.bottom));
        const id = el.id || (el.closest('[id]') || {}).id || el.tagName;
        out.push({ ov: !!el.closest('[data-qa="overlay"]'), id, text: own.slice(0, 40), x0, y0, x1, y1, px: parseFloat(getComputedStyle(el).fontSize), o: +o.toFixed(2), path: (() => { const a = []; for (let e = el; e && e.nodeType === 1; e = e.parentElement) a.push(e); return a; })().length });
      });
      return out;
    });
    const issues = [];
    for (const q of boxes) {
      const pad = 2;
      if (q.x0 < -pad || q.x1 > W + pad || q.y0 < -pad || q.y1 > H + pad) issues.push({ lv: 'fix', kind: '잘림(화면 밖)', text: q.text, box: [q.x0, q.y0, q.x1, q.y1].map(Math.round) });
      if (q.px < 18 && q.o > 0.5) issues.push({ lv: 'check', kind: '글씨 너무 작음', text: q.text, px: q.px });
      if (SAFE) {
        const inTop = q.y0 < SAFE.top, inBot = q.y1 > H - SAFE.bottom, inRight = q.x1 > W - SAFE.right && q.y1 > H * SAFE.rightFrom;
        if (inTop || inBot || inRight) issues.push({ lv: 'fix', kind: '인스타 가림 영역', where: [inTop && '위', inBot && '아래', inRight && '오른쪽 버튼'].filter(Boolean).join('·'), text: q.text, box: [q.x0, q.y0, q.x1, q.y1].map(Math.round) });
      }
    }
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], c = boxes[j]; if (a.id === c.id || a.ov || c.ov) continue;
      const ix = Math.max(0, Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0)), iy = Math.max(0, Math.min(a.y1, c.y1) - Math.max(a.y0, c.y0));
      const small = Math.min((a.x1 - a.x0) * (a.y1 - a.y0), (c.x1 - c.x0) * (c.y1 - c.y0));
      if (ix * iy > 0.08 * small) issues.push({ lv: 'fix', kind: '글자끼리 겹침', text: `${a.text} ↔ ${c.text}`, area: Math.round(100 * ix * iy / small) + '%' });
    }
    // 가까움: 위아래로 12px 안쪽이면 '붙어 보임'
    for (let i = 0; i < boxes.length; i++) for (let j = 0; j < boxes.length; j++) {
      const a = boxes[i], c = boxes[j]; if (i === j || a.id === c.id) continue;
      const hov = Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0); const gap = c.y0 - a.y1;
      if (hov > 20 && gap >= 0 && gap < 12) issues.push({ lv: 'check', kind: '너무 붙음', text: `${a.text} / ${c.text}`, gap: Math.round(gap) });
    }
    if (issues.length) { report.push({ t, issues }); const f = path.join(out, `qa_${String(t).replace('.', '_')}.png`);
      await p.evaluate(list => { document.querySelectorAll('.__qa').forEach(e => e.remove()); list.forEach(b => { if (!b) return; const d = document.createElement('div'); d.className = '__qa'; Object.assign(d.style, { position: 'fixed', left: b[0] + 'px', top: b[1] + 'px', width: (b[2] - b[0]) + 'px', height: (b[3] - b[1]) + 'px', outline: '4px solid #ff2d55', zIndex: 99999, pointerEvents: 'none' }); document.body.appendChild(d); }); },
        issues.map(x => x.box).filter(Boolean));
      await p.screenshot({ path: f }); await p.evaluate(() => document.querySelectorAll('.__qa').forEach(e => e.remove())); shots.push([t, f]); }
  }
  await b.close();
  // 같은 문제는 시각만 모아서 요약
  const sum = {}; report.forEach(({ t, issues }) => issues.forEach(x => { const k = x.lv + ' | ' + x.kind + ' | ' + x.text + (x.where ? ' | ' + x.where : ''); (sum[k] = sum[k] || []).push(t); }));
  const summary = Object.entries(sum).map(([k, ts]) => ({ issue: k, from: ts[0], to: ts[ts.length - 1], n: ts.length }));
  fs.writeFileSync(path.join(out, 'qa-report.json'), JSON.stringify({ file: A.file, arg: A.arg || null, safe: A.safe || 'reels', summary, detail: report }, null, 1));
  if (shots.length) {
    const { execFileSync } = require('child_process');
    const pick = shots.filter((_, i) => i % Math.ceil(shots.length / 12) === 0).slice(0, 12);
    execFileSync('python3', ['-c', `import sys\nfrom PIL import Image, ImageDraw\nfs=sys.argv[2:];n=len(fs);c=Image.new('RGB',(n*270,500),'#111');d=ImageDraw.Draw(c)\nfor i,f in enumerate(fs):\n  t,pth=f.split('|');c.paste(Image.open(pth).convert('RGB').resize((270,480)),(i*270,20));d.text((i*270+4,4),t+'s',fill='#fff')\nc.save(sys.argv[1],quality=85)`, path.join(out, 'qa-sheet.jpg'), ...pick.map(([t, f]) => `${t}|${f}`)]);
    shots.forEach(([, f]) => fs.rmSync(f));
  }
  console.log(JSON.stringify({ ok: !summary.some(x => x.issue.startsWith('fix')), summary, sheet: shots.length ? path.join(out, 'qa-sheet.jpg') : null }, null, 1));
})();
