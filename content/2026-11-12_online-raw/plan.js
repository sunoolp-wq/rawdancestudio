// 학원 구조 도안 (소개 영상 분석, 2026-11-12) → plan.png · 위치·크기는 영상으로 본 추정
const { launch } = require('../../tools/pw.js'); const fs = require('fs'), path = require('path');
const img = n => 'data:image/jpeg;base64,' + fs.readFileSync(path.join(__dirname, 'ref', n + '.jpg')).toString('base64');
const room = (x, y, w, h, name, sub, c, extra = '') => `<div class="rm" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;border-color:${c}"><b style="color:${c}">${name}</b><span>${sub}</span>${extra}</div>`;
const pin = (x, y, n) => `<i class="pin" style="left:${x}px;top:${y}px">${n}</i>`;
const html = `<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Noto+Sans+KR:wght@500;700;900&display=swap" rel="stylesheet"><style>
*{margin:0;padding:0;box-sizing:border-box}body{width:1920px;height:1240px;background:#0e0d12;color:#f4f2ee;font-family:"Noto Sans KR";position:relative;overflow:hidden}
.hd{position:absolute;left:60px;top:44px}.hd b{font-family:Montserrat;font-weight:800;font-size:16px;letter-spacing:.3em;color:#b9a6ff}.hd h1{font-size:42px;font-weight:900;margin-top:6px}.hd p{font-size:18px;color:#a7a2b5;margin-top:6px}
.plan{position:absolute;left:60px;top:190px;width:1020px;height:960px;border:3px solid #6f6a7c;border-radius:6px;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:40px 40px}
.rm{position:absolute;border:2.5px solid;border-radius:6px;background:rgba(255,255,255,.03);padding:14px 16px}.rm b{display:block;font-size:24px;font-weight:900}.rm span{display:block;font-size:14px;color:#a7a2b5;margin-top:4px;line-height:1.5}
.obj{position:absolute;font-size:12px;font-weight:700;color:#0e0d12;border-radius:5px;padding:3px 7px;white-space:nowrap}
.logo{position:absolute;height:8px;background:#fff;box-shadow:0 0 14px #fff;border-radius:2px}.logo.v{width:8px;height:auto}
.pin{position:absolute;width:30px;height:30px;border-radius:50%;background:#f5be46;color:#0e0d12;font-style:normal;font-family:Montserrat;font-weight:800;font-size:15px;display:flex;align-items:center;justify-content:center;transform:translate(-50%,-50%)}
.door{position:absolute;background:#0e0d12;border:2px dashed #5fd0ff}
.lg{position:absolute;left:60px;top:1160px;display:flex;gap:26px;font-size:15px;color:#a7a2b5}.lg span{display:flex;align-items:center;gap:8px}.lg i{display:inline-block;width:22px;height:8px;border-radius:2px}
.ph{position:absolute;left:1120px;top:190px;width:740px;display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.ph div{position:relative}.ph img{width:100%;height:240px;object-fit:cover;border-radius:10px;display:block}.ph em{position:absolute;left:8px;top:8px;font-style:normal;background:#f5be46;color:#0e0d12;font-family:Montserrat;font-weight:800;font-size:13px;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.ph span{position:absolute;left:0;right:0;bottom:0;background:linear-gradient(transparent,rgba(0,0,0,.85));font-size:13px;font-weight:700;padding:18px 8px 7px;border-radius:0 0 10px 10px}
.q{position:absolute;left:1120px;top:972px;width:740px;border:1.5px solid rgba(245,190,70,.5);border-radius:14px;padding:16px 20px;font-size:15px;line-height:1.7;color:#e9e5f2}.q b{color:#f5be46}
</style></head><body>
<div class="hd"><b>RAW DANCE STUDIO SUWON · 구조 도안 v1</b><h1>소개 영상으로 그린 학원 평면도</h1><p>약 100평 · 위치와 크기는 영상 장면으로 짐작한 것 (추정) — 틀린 곳을 알려 주시면 고칠게요</p></div>
<div class="plan">
  ${room(30, 30, 560, 470, 'A홀 (메인)', '가장 넓음 · 검은 벽·검은 천장(노출 보)<br>트랙 스포트 조명 + 빨간 점 조명 줄 · 조명 색 바뀜<br>밝은 회색 콘크리트 바닥', '#b9a6ff')}
  <div class="logo" style="left:200px;top:46px;width:220px"></div><div class="obj" style="left:250px;top:62px;background:#fff">RAW 백라이트 로고</div>
  ${room(30, 530, 350, 400, 'B홀 (메인)', '메인홀 2개 중 하나 · 검은 벽<br>RAW 로고 · 한쪽에 유리(거울?) 벽', '#b9a6ff')}
  <div class="logo" style="left:110px;top:546px;width:170px"></div>
  ${room(400, 530, 200, 190, '전문반 연습실', '전문반 전용<br>작은 검은 방', '#5fd0ff')}
  ${room(400, 740, 95, 190, '남', '탈의실<br>창문·거울', '#6fe3a6')}${room(505, 740, 95, 190, '여', '탈의실', '#6fe3a6')}
  <div class="rm" style="left:615px;top:30px;width:130px;height:900px;border-color:#6f6a7c;border-style:dashed"><b style="color:#c3bfcc;font-size:18px">복도</b><span>회색 벽<br>정수기<br>휴지통<br>비상구</span></div>
  ${room(760, 30, 230, 900, '로비', '광택 회색 타일 바닥<br>천장 사각 조명 프레임', '#f5be46')}
  <div class="obj" style="left:790px;top:330px;background:#c3bfcc">프런트 데스크 (곡선)</div><div class="logo" style="left:800px;top:300px;width:150px"></div>
  <div class="obj" style="left:790px;top:470px;background:#fff">흰 벤치</div><div class="obj" style="left:880px;top:420px;background:#8a8a90">TV</div>
  <div class="obj" style="left:790px;top:620px;background:#fff">RAW 큰 로고 판넬</div><div class="obj" style="left:790px;top:680px;background:#c9a77c">선반 (철제+나무)</div>
  <div class="door" style="left:830px;top:918px;width:100px;height:16px"></div><div class="obj" style="left:790px;top:885px;background:#5fd0ff">입구 (유리문·매트)</div>
  ${pin(960, 870, 1)}${pin(960, 340, 2)}${pin(860, 480, 3)}${pin(960, 630, 4)}${pin(300, 260, 5)}${pin(500, 420, 6)}${pin(680, 420, 7)}${pin(200, 760, 8)}${pin(340, 880, 9)}${pin(570, 690, 10)}${pin(960, 690, 11)}${pin(450, 880, 12)}
</div>
<div class="lg"><span><i style="background:#b9a6ff"></i>메인 홀</span><span><i style="background:#5fd0ff"></i>전문반 연습실</span><span><i style="background:#6fe3a6"></i>탈의실</span><span><i style="background:#f5be46"></i>로비</span><span><i style="background:#fff;box-shadow:0 0 8px #fff"></i>RAW 로고</span><span>● 노란 번호 = 오른쪽 사진</span></div>
<div class="ph">${[['entrance', '입구 · 바닥 매트'], ['lobby-desk', '로비 프런트'], ['lobby-bench', '로비 벤치'], ['raw-panel', 'RAW 로고 판넬'], ['a-hall', 'A홀 · 빨간 점 조명'], ['a-hall-wide', 'A홀 전체'], ['corridor', '복도 · 정수기'], ['b-hall', 'B홀'], ['b-hall-glass', 'B홀 유리 벽'], ['pro-room', '전문반 연습실'], ['locker', '선반 · 창문'], ['changing', '탈의실']].map((p, i) => `<div><img src="${img(p[0])}"><em>${i + 1}</em><span>${p[1]}</span></div>`).join('')}</div>
<div class="q"><b>확인 부탁드려요</b> ① A홀·B홀·로비가 실제로 어느 쪽에 붙어 있는지 ② 거울 벽은 홀마다 어느 벽인지 (영상은 거울 쪽에서 찍어 안 보여요)<br>③ 탈의실·전문반 연습실 위치 ④ 화장실 위치 — 대충 손으로 그린 사진 한 장이면 충분해요</div>
</body></html>`;
(async () => { const b = await launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1240 } }); await p.setContent(html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  await p.screenshot({ path: path.join(__dirname, 'plan.png') }); await b.close(); console.log('ok'); })();
