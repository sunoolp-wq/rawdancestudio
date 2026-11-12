// 학원 구조 도안 v2: 원장님 손그림 배치(2026-11-12) + 소개 영상 디테일 → plan2.png
const { launch } = require('../../tools/pw.js'); const path = require('path');
const K = .92, X = x => (x - 55) * K + 40, Y = y => (y - 58) * K + 36;
const R = (x1, y1, x2, y2, name, sub, c, fs = 24) => `<div class="rm" style="left:${X(x1)}px;top:${Y(y1)}px;width:${(x2 - x1) * K}px;height:${(y2 - y1) * K}px;border-color:${c}"><b style="color:${c};font-size:${fs}px">${name}</b>${sub ? `<span>${sub}</span>` : ''}</div>`;
const door = (x, y, dir, label = '') => `<div class="door" style="left:${X(x)}px;top:${Y(y)}px"><i style="transform:translate(-50%,-50%) rotate(${dir}deg)">▲</i>${label ? `<em>${label}</em>` : ''}</div>`;
const html = `<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Noto+Sans+KR:wght@500;700;900&display=swap" rel="stylesheet"><style>
*{margin:0;padding:0;box-sizing:border-box}body{width:1920px;height:1080px;background:#0e0d12;color:#f4f2ee;font-family:"Noto Sans KR";position:relative;overflow:hidden}
.hd{position:absolute;left:60px;top:40px}.hd b{font-family:Montserrat;font-weight:800;font-size:16px;letter-spacing:.3em;color:#b9a6ff}.hd h1{font-size:40px;font-weight:900;margin-top:6px}.hd p{font-size:17px;color:#a7a2b5;margin-top:6px}
.plan{position:absolute;left:60px;top:170px;width:1140px;height:760px;border-radius:8px;background:#15141b;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:36px 36px}
.lobby{position:absolute;left:${X(55)}px;top:${Y(58)}px;width:${(1205 - 55) * K}px;height:${(777 - 58) * K}px;border:3px solid #6f6a7c;border-radius:4px;background:rgba(245,190,70,.04)}
.rm{position:absolute;border:2.5px solid;border-radius:4px;background:#1b1a22;padding:12px 14px;overflow:hidden}.rm b{display:block;font-weight:900;line-height:1.15}.rm span{display:block;font-size:13px;color:#a7a2b5;margin-top:5px;line-height:1.45}
.door{position:absolute;width:0;height:0}.door i{position:absolute;font-style:normal;color:#5fd0ff;font-size:22px;text-shadow:0 0 10px #5fd0ff}.door em{position:absolute;left:16px;top:-10px;font-style:normal;font-size:12px;font-weight:700;color:#5fd0ff;white-space:nowrap}
.tag{position:absolute;font-size:12px;font-weight:700;border-radius:5px;padding:3px 8px;white-space:nowrap;color:#0e0d12}
.logo{position:absolute;height:7px;background:#fff;box-shadow:0 0 12px #fff;border-radius:2px}
.side{position:absolute;left:1240px;top:170px;width:620px}
.side h2{font-size:22px;font-weight:900;margin-bottom:12px}.side ul{list-style:none;display:grid;gap:9px;font-size:15px;line-height:1.55;color:#d6d2e0}.side li b{color:#f4f2ee}
.q{margin-top:22px;border:1.5px solid rgba(245,190,70,.55);border-radius:14px;padding:16px 20px;font-size:15px;line-height:1.7}.q b{color:#f5be46}
.lg{position:absolute;left:60px;top:950px;display:flex;gap:24px;font-size:14px;color:#a7a2b5;align-items:center}.lg i{display:inline-block;width:20px;height:8px;border-radius:2px;margin-right:6px;vertical-align:1px}
</style></head><body>
<div class="hd"><b>RAW DANCE STUDIO SUWON · 구조 도안 v2</b><h1>원장님 배치도 + 소개 영상 디테일</h1><p>방 위치는 원장님 그림 그대로 · 크기 비율은 대략 · 문(▲)은 들어가는 방향</p></div>
<div class="plan">
  <div class="lobby"></div>
  <div style="position:absolute;left:${X(560)}px;top:${Y(400)}px;font-size:34px;font-weight:900;color:rgba(245,190,70,.55)">로비</div>
  <div style="position:absolute;left:${X(520)}px;top:${Y(445)}px;font-size:13px;color:#a7a2b5">광택 회색 타일 · 천장 사각 조명 프레임</div>
  ${R(55, 58, 282, 420, 'A홀 (메인홀)', '가장 넓음 · 검은 벽·노출 천장<br>트랙 조명 + 빨간 점 조명<br>RAW 백라이트 로고', '#b9a6ff', 26)}
  ${R(55, 422, 282, 657, 'C홀', '전문반 연습실', '#5fd0ff', 26)}
  ${R(282, 58, 333, 193, '짐<br>놓는 데', '', '#c9a77c', 15)}
  ${R(480, 58, 686, 117, '탈의실', '', '#6fe3a6', 18)}${R(480, 117, 686, 178, '탈의실', '', '#6fe3a6', 18)}
  ${R(686, 58, 967, 178, '원장실', '', '#c3bfcc', 20)}
  ${R(480, 178, 833, 258, '인포데스크', '곡선 데스크 · 뒤에 RAW 로고', '#f5be46', 20)}
  ${R(900, 232, 965, 491, '흰<br>소파', '', '#f4f2ee', 16)}
  ${R(967, 60, 1130, 492, 'B홀', '메인홀 2 · 검은 벽<br>RAW 로고<br>유리 벽', '#b9a6ff', 26)}
  ${R(741, 632, 987, 777, '여자 화장실', '', '#ff9db5', 18)}${R(987, 632, 1205, 777, '남자 화장실', '', '#5fd0ff', 18)}
  ${R(1173, 588, 1205, 630, '', '', '#5fd0ff')}<div class="tag" style="left:${X(1095)}px;top:${Y(598)}px;background:#5fd0ff">정수기</div>
  <div style="position:absolute;left:${X(1138)}px;top:${Y(230)}px;writing-mode:vertical-rl;font-size:15px;font-weight:700;color:#a7a2b5;letter-spacing:.2em">비상구 복도</div>
  <div class="rm" style="left:${X(388)}px;top:${Y(718)}px;width:${112 * K}px;height:${59 * K}px;border-color:#5fd0ff;background:rgba(95,208,255,.1)"><b style="color:#5fd0ff;font-size:14px">출입문<br>(자동문)</b></div>
  <div class="logo" style="left:${X(560)}px;top:${Y(184)}px;width:${120 * K}px"></div>
  ${door(282, 380, -90, 'A홀 문')}${door(282, 465, -90, 'C홀 문')}${door(917, 182, 0, '유리문')}${door(1015, 492, 0, 'B홀 문')}${door(947, 632, 0)}${door(1032, 632, 0)}${door(444, 718, 0, '입구')}
</div>
<div class="lg"><span><i style="background:#b9a6ff"></i>메인홀 A·B</span><span><i style="background:#5fd0ff"></i>C홀(전문반)</span><span><i style="background:#f5be46"></i>로비·인포데스크</span><span><i style="background:#6fe3a6"></i>탈의실</span><span style="color:#5fd0ff">▲ 문</span><span><i style="background:#fff;box-shadow:0 0 8px #fff"></i>RAW 로고</span></div>
<div class="side"><h2>온라인 연습실에는 이렇게 옮겨요</h2><ul>
  <li>🚪 <b>자동문으로 입장</b> → 로비 한가운데서 시작. 정면에 <b>인포데스크 + RAW 로고</b></li>
  <li>🛋 오른쪽 <b>흰 소파</b>에 앉기(쉬기) · <b>정수기</b>에서 💧 물 마시기·건네기</li>
  <li>🟣 왼쪽 <b>A홀 문</b>으로 들어가면 메인홀: 빨간 점 조명 + 트랙 조명, 여기서 8카운트·프리스타일</li>
  <li>🟣 오른쪽 <b>B홀</b>: 메인홀 2. 사람이 많으면 다른 홀로 (산사의 "산사 03"처럼 방 나누기)</li>
  <li>🔵 <b>C홀</b>: 전문반 연습실 → 온라인에선 "PRO 전용" 잠긴 문 + 이벤트용</li>
  <li>📝 소원 쪽지는 <b>로비 벽</b>(인포데스크 옆)에 붙이기 · 🎒 짐 놓는 데 = 내 캐릭터 옷 바꾸기</li>
  <li>🚻 탈의실·화장실·원장실은 문만 보이고 안 들어감</li></ul>
<div class="q"><b>2가지만 더 알려 주세요</b><br>① 각 홀 <b>거울은 어느 벽</b>인가요? (예: A홀은 로비 반대쪽 벽 전체)<br>② 각 홀 <b>RAW 로고는 어느 벽</b>인가요? (영상 보면 A홀은 문 맞은편 같아요)</div></div>
</body></html>`;
(async () => { const b = await launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); await p.setContent(html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  await p.screenshot({ path: path.join(__dirname, 'plan2.png') }); await b.close(); console.log('ok'); })();
