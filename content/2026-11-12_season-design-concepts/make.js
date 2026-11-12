// 다음 시즌 디자인 시안 4종: 각 시안 = 시간표 스토리 · 선생님 영상 · 출석 순위표 (예시 이름은 지어낸 것)
// node content/2026-11-12_season-design-concepts/make.js → concept-a..d.png
const { launch } = require('../../tools/pw.js'); const fs = require('fs'), path = require('path');
const photo = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(__dirname, 'kiry-frame.jpg')).toString('base64');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '../../tools/daily-story/raw-logo.png')).toString('base64');
const CL = [['16:00', '유아 K-POP', 'YUNI'], ['17:00', '키즈 K-POP', 'YUNI'], ['19:30', '성인 K-POP', 'YUNI'], ['19:40', 'HEELSCHOREO', 'HEEONE'], ['20:50', 'CHOREO', 'RAEKU']];
const RK = [['서하은', 312, 4], ['김도윤', 298, 4], ['박지안', 271, 3], ['이서아', 240, 3], ['최유나', 205, 2], ['정다온', 160, 0]];
const FONTS = '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Black+Han+Sans&family=Do+Hyeon&family=Jua&family=Graduate&family=Press+Start+2P&family=Unbounded:wght@500;800;900&family=Noto+Sans+KR:wght@500;700;900&family=Montserrat:wght@600;800&display=swap" rel="stylesheet">';
const shell = (t, css, title, sub, story, reel, board) => `<!doctype html><html><head><meta charset="utf-8">${FONTS}<style>
*{margin:0;padding:0;box-sizing:border-box}body{width:1920px;height:1080px;overflow:hidden;position:relative;font-family:"Noto Sans KR",sans-serif}
.hd{position:absolute;left:60px;top:46px;right:60px;display:flex;align-items:flex-end;gap:24px}.hd b{font-family:Montserrat;font-weight:800;font-size:18px;letter-spacing:.3em}.hd h1{font-size:44px;font-weight:900;line-height:1}.hd p{font-size:20px;opacity:.7;margin-left:auto;text-align:right;max-width:760px}
.s{position:absolute;top:170px;width:360px;height:640px;overflow:hidden;border-radius:18px;box-shadow:0 20px 60px rgba(0,0,0,.25)}.s1{left:60px}.s2{left:450px}
.b{position:absolute;left:850px;top:170px;width:1010px;height:632px;overflow:hidden;border-radius:18px;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.lb{position:absolute;top:832px;font-family:Montserrat;font-weight:800;font-size:15px;letter-spacing:.24em;opacity:.6}
.ft{position:absolute;left:60px;bottom:40px;font-size:17px;opacity:.6}
${css}</style></head><body class="${t}">
<div class="hd"><div><b>${title[0]}</b><h1>${title[1]}</h1></div><p>${sub}</p></div>
<div class="s s1">${story}</div><div class="s s2">${reel}</div><div class="b">${board}</div>
<div class="lb" style="left:60px">TODAY'S CLASS · 스토리</div><div class="lb" style="left:450px">선생님 영상 15초</div><div class="lb" style="left:850px">로비 태블릿 · 출석 순위표</div>
<div class="ft">${title[2]}</div></body></html>`;

// ── A. CONCRETE: 종이 포스터 · 굵은 컨덴스드 · 빨간 테이프
const A = shell('A', `
body.A{background:#d9d5cc;color:#111}.A .paper{background:#ecE9e2;background-image:radial-gradient(rgba(0,0,0,.07) 1px,transparent 1.2px);background-size:5px 5px}
.A .tape{display:inline-block;background:#ff3b1f;color:#fff;font-family:Anton;letter-spacing:.06em;padding:4px 12px;transform:rotate(-3deg)}
.A .an{font-family:Anton;line-height:.85}.A .kr{font-family:"Black Han Sans"}`,
['SEASON 시안 A', 'CONCRETE 스트릿 포스터', '빛바랜 종이 · 검정 굵은 글씨 · 빨간 테이프 · 망점'],
'벽에 붙인 공연 포스터처럼. 거칠고 힙합스러운 무드. 순위는 큰 번호 + 도장.',
`<div class="paper" style="position:absolute;inset:0;padding:26px 24px">
  <div style="display:flex;justify-content:space-between;align-items:center"><img src="${logo}" style="height:18px;filter:invert(1)"><span class="tape" style="font-size:14px">TODAY'S CLASS</span></div>
  <div class="an" style="font-size:150px;margin-top:18px;letter-spacing:-.01em">MON</div>
  <div class="an" style="font-size:40px;color:#ff3b1f;margin-top:4px">11.16 / 6 CLASSES</div>
  <div style="margin-top:20px;display:grid;gap:7px">${CL.map(c => `<div style="display:flex;align-items:center;gap:12px;background:#111;color:#ecE9e2;padding:9px 12px"><span class="an" style="font-size:24px;width:66px">${c[0]}</span><span class="kr" style="font-size:19px;flex:1">${c[1]}</span><span style="font-family:Anton;font-size:13px;letter-spacing:.1em;opacity:.7">${c[2]}</span></div>`).join('')}</div>
  <div style="position:absolute;right:-30px;bottom:-30px;width:170px;height:170px;border-radius:50%;background:radial-gradient(#111 1.6px,transparent 1.8px);background-size:8px 8px;opacity:.6"></div></div>`,
`<div style="position:absolute;inset:0;background:url(${photo}) center/cover;filter:grayscale(1) contrast(1.15)"></div>
  <div style="position:absolute;left:0;right:0;bottom:0;height:230px;background:#ecE9e2;clip-path:polygon(0 14%,8% 10%,16% 15%,27% 9%,38% 14%,50% 8%,61% 13%,73% 9%,84% 14%,93% 10%,100% 13%,100% 100%,0 100%)"></div>
  <div style="position:absolute;left:22px;bottom:96px" class="an"><span style="font-size:104px;color:#111">KIRY</span></div>
  <div style="position:absolute;left:24px;bottom:58px"><span class="tape" style="font-size:22px">JAZZ</span><span style="font-family:Anton;font-size:18px;margin-left:14px;color:#111">WED 20:50 · A HALL</span></div>
  <div style="position:absolute;left:22px;bottom:22px;font-size:12px;color:#555;font-weight:700">RAW DANCE STUDIO SUWON</div>`,
`<div class="paper" style="position:absolute;inset:0;padding:34px 40px">
  <div style="display:flex;justify-content:space-between;align-items:flex-end"><div class="an" style="font-size:86px">RAW SEASON 1</div><span class="tape" style="font-size:24px;margin-bottom:12px">D-21</span></div>
  <div style="margin-top:18px;border-top:6px solid #111">${RK.map((r, i) => `<div style="display:grid;grid-template-columns:110px 1fr 140px 140px;align-items:center;border-bottom:2px solid #111;height:72px">
    <span class="an" style="font-size:${i < 3 ? 60 : 44}px;color:${i === 0 ? '#ff3b1f' : '#111'}">${String(i + 1).padStart(2, '0')}</span><span class="kr" style="font-size:32px">${r[0]}</span>
    <span style="justify-self:center;font-family:Anton;font-size:20px;border:3px solid #ff3b1f;color:#ff3b1f;border-radius:50%;width:66px;height:66px;display:flex;align-items:center;justify-content:center;transform:rotate(-12deg)">${r[2]}WK</span>
    <span class="an" style="font-size:40px;text-align:right">${r[1]}P</span></div>`).join('')}</div>
  <div style="position:absolute;left:0;right:0;bottom:0;height:46px;background:#111;color:#ecE9e2;display:flex;align-items:center;justify-content:center;font-family:'Black Han Sans';font-size:20px">내 이름을 눌러 출석 · 연습 체크 ✦ TAP YOUR NAME</div></div>`);

// ── B. ARCADE: 오락실 점수판 · 픽셀 글씨 · 네온 초록/노랑 · 주사선
const B = shell('B', `
body.B{background:#0b0c10;color:#e8ffe9}.B .px{font-family:"Press Start 2P"}.B .dh{font-family:"Do Hyeon"}
.B .scan{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0 2px,transparent 2px 4px);pointer-events:none}
.B .g{color:#39ff88;text-shadow:0 0 10px rgba(57,255,136,.7)}.B .y{color:#ffd400;text-shadow:0 0 10px rgba(255,212,0,.6)}`,
['SEASON 시안 B', 'ARCADE 오락실 점수판', '검정 화면 · 픽셀 글씨 · 네온 초록·노랑 · 주사선'],
'출석이 진짜 게임처럼. "HIGH SCORE", "1P", "INSERT COIN" 같은 오락실 말투로 시즌 내내 통일.',
`<div style="position:absolute;inset:0;background:#050608;padding:26px 22px">
  <div class="px g" style="font-size:11px">RAW SUWON · STAGE SELECT</div>
  <div class="px y" style="font-size:52px;margin-top:26px">MON</div><div class="px" style="font-size:12px;margin-top:10px;color:#8af">11.16 · 6 STAGES</div>
  <div style="margin-top:22px;display:grid;gap:10px">${CL.map((c, i) => `<div style="display:flex;align-items:center;gap:10px;border:2px solid ${i > 2 ? '#39ff88' : '#2a5'};padding:9px 10px;${i > 2 ? 'box-shadow:0 0 12px rgba(57,255,136,.35)' : ''}"><span class="px y" style="font-size:12px">${c[0]}</span><span class="dh" style="font-size:20px;flex:1">${c[1]}</span><span class="px" style="font-size:8px;color:#8af">${c[2]}</span></div>`).join('')}</div>
  <div class="px g" style="position:absolute;left:0;right:0;bottom:24px;text-align:center;font-size:10px">▶ PRESS START</div><div class="scan"></div></div>`,
`<div style="position:absolute;inset:0;background:#050608"></div><div style="position:absolute;left:14px;right:14px;top:60px;bottom:150px;background:url(${photo}) center/cover;image-rendering:pixelated;border:4px solid #39ff88;box-shadow:0 0 18px rgba(57,255,136,.5)"></div>
  <div class="px" style="position:absolute;left:16px;top:22px;font-size:10px;color:#ffd400">1P  KIRY</div><div class="px" style="position:absolute;right:16px;top:22px;font-size:10px;color:#39ff88">HI 20:50</div>
  <div class="px y" style="position:absolute;left:16px;bottom:92px;font-size:34px">KIRY</div><div class="px g" style="position:absolute;left:16px;bottom:62px;font-size:14px">CLASS: JAZZ</div>
  <div style="position:absolute;left:16px;right:16px;bottom:28px;height:14px;border:2px solid #39ff88"><i style="display:block;width:72%;height:100%;background:#39ff88"></i></div><div class="scan"></div>`,
`<div style="position:absolute;inset:0;background:#050608;padding:34px 48px">
  <div style="display:flex;justify-content:space-between"><span class="px y" style="font-size:40px">HIGH SCORE</span><span class="px g" style="font-size:16px;margin-top:14px">SEASON 1 · D-21</span></div>
  <div style="margin-top:30px;display:grid;gap:14px">${RK.map((r, i) => `<div style="display:flex;align-items:center;gap:24px;font-size:22px"><span class="px ${i < 3 ? 'y' : ''}" style="width:90px;font-size:22px;${i < 3 ? '' : 'color:#8af'}">${['1ST', '2ND', '3RD', '4TH', '5TH', '6TH'][i]}</span>
    <span class="dh" style="font-size:36px;width:200px">${r[0]}</span><span style="flex:1;border-bottom:4px dotted #2a5;margin-top:10px"></span><span class="px g" style="font-size:22px;width:120px;text-align:right">${String(r[1]).padStart(5, '0')}</span><span class="px" style="font-size:14px;width:110px;text-align:right;color:#ff6a3d">x${r[2]} 🔥</span></div>`).join('')}</div>
  <div class="px y" style="position:absolute;left:0;right:0;bottom:30px;text-align:center;font-size:18px">INSERT COIN → TAP YOUR NAME</div><div class="scan"></div></div>`);

// ── C. CHROME: Y2K 크롬 · 파스텔 · 둥근 버블 · 반짝이
const chrome = 'background:linear-gradient(180deg,#fff 0%,#c9d2e3 38%,#8a96ad 50%,#eef2f8 62%,#aab4c6 100%);-webkit-background-clip:text;color:transparent;-webkit-text-stroke:1.2px rgba(70,80,120,.5)';
const C = shell('C', `
body.C{background:linear-gradient(135deg,#e7ecff,#f7e8ff 55%,#e6fbff);color:#2a2f4a}.C .ub{font-family:Unbounded}.C .ju{font-family:Jua}
.C .gl{background:rgba(255,255,255,.55);border:1.5px solid rgba(255,255,255,.9);backdrop-filter:blur(6px);box-shadow:0 6px 20px rgba(120,110,200,.18)}
.C .sp{position:absolute;color:#fff;text-shadow:0 0 12px #c6b8ff}`,
['SEASON 시안 C', 'CHROME Y2K 크롬', '은빛 크롬 글씨 · 파스텔 하늘·보라 · 동글동글 유리 카드 · 반짝이'],
'요즘 K-POP 앨범·무대 같은 Y2K 무드. 밝고 반짝여서 키즈·K-POP 반 홍보에도 잘 맞음.',
`<div style="position:absolute;inset:0;background:linear-gradient(160deg,#dfe6ff,#f4dcff 60%,#d8f6ff);padding:26px 22px">
  <div style="display:flex;justify-content:space-between;align-items:center"><img src="${logo}" style="height:16px;filter:invert(.2)"><span class="ub" style="font-size:11px;font-weight:800;letter-spacing:.2em;color:#7d6bd8">TODAY ✦ CLASS</span></div>
  <div class="ub" style="font-size:92px;font-weight:900;line-height:.95;margin-top:16px;${chrome}">MON</div><div class="ub" style="font-size:20px;font-weight:800;color:#7d6bd8">11.16</div>
  <div style="margin-top:18px;display:grid;gap:8px">${CL.map(c => `<div class="gl" style="border-radius:30px;padding:9px 16px;display:flex;align-items:center;gap:12px"><span class="ub" style="font-weight:800;font-size:15px;color:#7d6bd8">${c[0]}</span><span class="ju" style="font-size:19px;flex:1">${c[1]}</span><span class="ub" style="font-size:10px;font-weight:500;opacity:.6">${c[2]}</span></div>`).join('')}</div>
  <span class="sp" style="right:30px;top:120px;font-size:40px">✦</span><span class="sp" style="right:70px;top:190px;font-size:18px">✦</span><span class="sp" style="left:250px;bottom:40px;font-size:28px">✧</span></div>`,
`<div style="position:absolute;inset:0;background:linear-gradient(160deg,#dfe6ff,#f4dcff)"></div><div style="position:absolute;left:18px;right:18px;top:40px;height:420px;border-radius:120px 120px 30px 30px;background:url(${photo}) center/cover;border:4px solid #fff;box-shadow:0 10px 30px rgba(120,110,200,.35)"></div>
  <div class="ub" style="position:absolute;left:0;right:0;top:438px;text-align:center;font-size:76px;font-weight:900;${chrome}">KIRY</div>
  <div style="position:absolute;left:0;right:0;top:536px;display:flex;justify-content:center;gap:8px"><span class="gl ju" style="border-radius:20px;padding:6px 16px;font-size:18px">JAZZ</span><span class="gl ub" style="border-radius:20px;padding:7px 14px;font-size:12px;font-weight:800;color:#7d6bd8">WED 20:50</span></div>
  <span class="sp" style="left:30px;top:20px;font-size:34px">✦</span><span class="sp" style="right:26px;top:400px;font-size:26px">✧</span>`,
`<div style="position:absolute;inset:0;background:linear-gradient(135deg,#dfe6ff,#f4dcff 55%,#d8f6ff);padding:34px 44px">
  <div style="display:flex;justify-content:space-between;align-items:center"><span class="ub" style="font-size:58px;font-weight:900;${chrome}">RAW SEASON 1</span><span class="gl ub" style="border-radius:30px;padding:10px 22px;font-weight:800;color:#7d6bd8;font-size:20px">D-21 ✦</span></div>
  <div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:14px">${RK.map((r, i) => `<div class="gl" style="border-radius:26px;height:${i < 2 ? 130 : 100}px;display:flex;align-items:center;gap:18px;padding:0 24px">
    <span class="ub" style="width:${i < 2 ? 76 : 58}px;height:${i < 2 ? 76 : 58}px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:${i < 2 ? 30 : 22}px;background:linear-gradient(180deg,#fff,#c9d2e3 45%,#8a96ad 55%,#eef2f8);color:#3b4260">${i + 1}</span>
    <span class="ju" style="font-size:${i < 2 ? 36 : 28}px;flex:1">${r[0]}</span><span class="ub" style="font-weight:800;font-size:${i < 2 ? 30 : 24}px;color:#7d6bd8">${r[1]}<small style="font-size:.5em">P</small></span></div>`).join('')}</div>
  <div class="ju" style="position:absolute;left:0;right:0;bottom:26px;text-align:center;font-size:24px;color:#7d6bd8">✦ 내 이름을 톡 눌러 체크 ✦</div></div>`);

// ── D. VARSITY: 스포츠 저지 · 네이비 + 골드 · 칼리지 글씨 · 리그 순위표
const D = shell('D', `
body.D{background:#0a1730;color:#f5efe0}.D .gr{font-family:Graduate}.D .bh{font-family:"Black Han Sans"}
.D .gold{color:#f2b705}.D .st{height:6px;background:linear-gradient(#f2b705 0 33%,transparent 33% 66%,#f2b705 66%)}`,
['SEASON 시안 D', 'VARSITY 스포츠 저지', '네이비 + 골드 · 미국 대학 저지 글씨 · 굵은 줄무늬 · 리그 순위표'],
'학원을 하나의 팀처럼. 전문반 = 대표팀, 순위표 = 리그 순위. 시즌 후드 디자인까지 이어 가기 좋음.',
`<div style="position:absolute;inset:0;background:#0b1d3a;padding:26px 24px">
  <div style="display:flex;justify-content:space-between;align-items:center"><img src="${logo}" style="height:18px"><span class="gr gold" style="font-size:13px;letter-spacing:.12em">RAW ATHLETICS</span></div>
  <div class="st" style="margin-top:18px"></div>
  <div class="gr" style="font-size:96px;line-height:1;margin-top:14px;color:#f5efe0;text-shadow:4px 4px 0 #f2b705">MON</div><div class="gr gold" style="font-size:22px">GAME DAY · 11.16</div>
  <div style="margin-top:18px;display:grid;gap:7px">${CL.map((c, i) => `<div style="display:flex;align-items:center;gap:12px;border:2px solid #f2b705;border-radius:8px;padding:8px 12px"><span class="gr gold" style="font-size:20px;width:64px">${c[0]}</span><span class="bh" style="font-size:19px;flex:1">${c[1]}</span><span class="gr" style="font-size:11px;opacity:.8">${c[2]}</span></div>`).join('')}</div>
  <div class="st" style="position:absolute;left:24px;right:24px;bottom:26px"></div></div>`,
`<div style="position:absolute;inset:0;background:url(${photo}) center/cover"></div><div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent 45%,rgba(10,23,48,.95) 78%)"></div>
  <div style="position:absolute;right:18px;top:18px;width:84px;height:84px;border-radius:50%;background:#f2b705;color:#0b1d3a;display:flex;flex-direction:column;align-items:center;justify-content:center" class="gr"><span style="font-size:11px">WED</span><span style="font-size:24px;line-height:1">20:50</span></div>
  <div class="gr" style="position:absolute;left:22px;bottom:104px;font-size:84px;line-height:1;color:#f5efe0;text-shadow:4px 4px 0 #f2b705">KIRY</div>
  <div class="gr gold" style="position:absolute;left:24px;bottom:72px;font-size:24px;letter-spacing:.06em">JAZZ · A HALL</div><div class="st" style="position:absolute;left:22px;right:22px;bottom:40px"></div>`,
`<div style="position:absolute;inset:0;background:#0b1d3a;padding:30px 44px">
  <div style="display:flex;justify-content:space-between;align-items:flex-end"><div><div class="gr gold" style="font-size:18px;letter-spacing:.16em">RAW ATHLETICS · PRO</div><div class="gr" style="font-size:56px;text-shadow:3px 3px 0 #f2b705">LEAGUE STANDINGS</div></div><div class="gr gold" style="font-size:30px">WEEK 4</div></div>
  <div class="st" style="margin-top:14px"></div>
  <div style="display:grid;grid-template-columns:80px 1fr 140px 160px;margin-top:14px;font-family:Graduate;font-size:16px;color:#f2b705;opacity:.8"><span>RK</span><span>PLAYER</span><span style="text-align:center">STREAK</span><span style="text-align:right">PTS</span></div>
  ${RK.map((r, i) => `<div style="display:grid;grid-template-columns:80px 1fr 140px 160px;align-items:center;height:66px;border-bottom:1px solid rgba(242,183,5,.3);${i === 0 ? 'background:rgba(242,183,5,.12)' : ''}">
    <span class="gr" style="font-size:34px;${i === 0 ? 'color:#f2b705' : ''}">${i + 1}</span><span class="bh" style="font-size:30px">${r[0]}</span><span class="gr" style="text-align:center;font-size:24px">W${r[2]}</span><span class="gr gold" style="text-align:right;font-size:34px">${r[1]}</span></div>`).join('')}
  <div class="bh" style="position:absolute;left:0;right:0;bottom:0;height:46px;background:#f2b705;color:#0b1d3a;display:flex;align-items:center;justify-content:center;font-size:21px">★ CHECK IN · 내 이름을 눌러 출석 ★</div></div>`);

(async () => {
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [k, h] of [['a', A], ['b', B], ['c', C], ['d', D]]) {
    await p.setContent(h); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(600);
    await p.screenshot({ path: path.join(__dirname, `concept-${k}.png`) });
  }
  await b.close(); console.log('ok');
})();
