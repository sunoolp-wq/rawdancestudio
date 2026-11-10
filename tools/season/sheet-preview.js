// 선생님이 보는 [출석] 탭 예시 그림 → content/2026-11-10_motivation-ideas/sheet-preview.png
const { launch } = require('../pw.js'); const path = require('path');
const rows = [['박지우','GIRLISH',[1,0,0,0,0]],['전가은','HIP HOP',[0,0,0,1,0]],['강다은','PRO 전문반',[0,0,0,0,1]],['배리아','취미 K-POP',[1,0,0,1,0]],['황시은','GIRLS HIPHOP',[0,0,0,0,1]],['이하은','성인 K-POP',[1,0,1,0,0]],['류나연','GIRLISH',[0,1,0,0,0]],['장하린','취미 K-POP',[1,0,0,0,0]]];
const days = ['12/07 (월)','12/08 (화)','12/09 (수)','12/10 (목)','12/11 (금)'];
const box = c => c ? '<span class="cb on">✓</span>' : '<span class="cb"></span>';
const html = `<html><head><meta charset="utf-8"><style>body{margin:0;background:#fff;font-family:"Noto Sans KR",sans-serif}
.bar{background:#f1f3f4;border-bottom:1px solid #dadce0;padding:10px 16px;font-size:15px;color:#3c4043}
table{border-collapse:collapse;font-size:16px}td,th{border:1px solid #e2e3e3;height:40px;padding:0 14px;text-align:center}
th{background:#f8f9fa;font-weight:700;color:#3c4043}th.today{background:#e8f0fe;color:#1a73e8}td.n{text-align:left;font-weight:700;min-width:80px}td.c{color:#5f6368;min-width:110px}
td.today{background:#f4f8ff}.cb{display:inline-block;width:18px;height:18px;border:2px solid #5f6368;border-radius:3px;vertical-align:middle}
.cb.on{background:#1a73e8;border-color:#1a73e8;color:#fff;font-size:14px;line-height:18px;font-weight:900}
.tabs{display:flex;gap:2px;background:#f1f3f4;padding:6px 10px;border-top:1px solid #dadce0;font-size:14px}.tabs span{padding:6px 16px;color:#5f6368}.tabs span.a{background:#fff;color:#1a73e8;font-weight:700;border-radius:0 0 4px 4px}</style></head><body>
<div class="bar">RAW SEASON 1 출석 — 선생님은 오늘 날짜 칸에 체크만</div>
<table><tr><th>이름</th><th>반</th>${days.map((d, i) => `<th class="${i == 3 ? 'today' : ''}">${d}</th>`).join('')}</tr>
${rows.map(r => `<tr><td class="n">${r[0]}</td><td class="c">${r[1]}</td>${r[2].map((c, i) => `<td class="${i == 3 ? 'today' : ''}">${i <= 3 ? box(c) : '<span class="cb" style="opacity:.35"></span>'}</td>`).join('')}</tr>`).join('')}</table>
<div class="tabs"><span class="a">출석</span><span>미션</span><span>설정</span></div></body></html>`;
(async () => { const b = await launch(); const p = await b.newPage({ viewport: { width: 900, height: 470 }, deviceScaleFactor: 2 });
  await p.setContent(html); await p.evaluate(() => document.fonts.ready);
  const el = await p.$('body'); await el.screenshot({ path: path.join(__dirname, '../../content/2026-11-10_motivation-ideas/sheet-preview.png') }); await b.close(); })();
