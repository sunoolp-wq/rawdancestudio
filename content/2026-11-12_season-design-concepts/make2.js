// 다음 시즌 디자인 시안 2차 4종 (E~H): 각 시안 = 시간표 스토리 · 선생님 영상 · 출석 순위표 (예시 이름은 지어낸 것)
// node content/2026-11-12_season-design-concepts/make2.js → concept-e..h.png
const { launch } = require('../../tools/pw.js'); const fs = require('fs'), path = require('path');
const photo = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(__dirname, 'kiry-frame.jpg')).toString('base64');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '../../tools/daily-story/raw-logo.png')).toString('base64');
const CL = [['16:00', '유아 K-POP', 'YUNI'], ['17:00', '키즈 K-POP', 'YUNI'], ['19:30', '성인 K-POP', 'YUNI'], ['19:40', 'HEELSCHOREO', 'HEEONE'], ['20:50', 'CHOREO', 'RAEKU']];
const RK = [['서하은', 312, 4], ['김도윤', 298, 4], ['박지안', 271, 3], ['이서아', 240, 3], ['최유나', 205, 2], ['정다온', 160, 0]];
const FONTS = '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Black+Han+Sans&family=Do+Hyeon&family=Jua&family=Graduate&family=Press+Start+2P&family=Unbounded:wght@500;800;900&family=Noto+Sans+KR:wght@500;700;900&family=Montserrat:wght@600;800&family=Nanum+Gothic+Coding:wght@400;700&family=Bodoni+Moda:ital,opsz,wght@1,6..96,800;0,6..96,900&family=Archivo+Black&family=IBM+Plex+Mono:wght@500;700&display=swap" rel="stylesheet">';
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


const bar = n => Array.from({ length: n }, (_, i) => `<i style="display:inline-block;height:100%;width:${[2, 1, 3, 1, 2, 4, 1][i % 7]}px;margin-right:${[1, 2, 1, 3, 1, 1, 2][i % 7]}px;background:#111"></i>`).join('');

// ── E. SUBWAY 지하철 노선도: 흰 바탕 · 노선 색 · 역 표지판
const LC = '#7c5cff';
const E = shell('E', `
body.E{background:#f2f3f5;color:#1b1c20}.E .w{background:#fff}.E .bh{font-family:"Noto Sans KR";font-weight:900}
.E .stn{width:22px;height:22px;border-radius:50%;background:#fff;border:5px solid ${LC};flex:none;position:relative;z-index:1}
.E .num{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;background:${LC};color:#fff;font-family:Montserrat;font-weight:800;font-size:15px}`,
['SEASON 시안 E', 'SUBWAY 지하철 노선도', '흰 바탕 · 노선 하나(RAW선) · 역 = 수업 · 역 이름판 · 환승 표시'],
'수원 지하철 안내판처럼 익숙하고 깔끔. 수업은 역, 순위는 "RAW선" 위의 위치. 학부모도 한눈에 읽기 쉬움.',
`<div class="w" style="position:absolute;inset:0;padding:24px 22px">
  <div style="display:flex;align-items:center;gap:10px"><span class="num">R</span><span class="bh" style="font-size:20px">RAW선 · 오늘의 수업</span></div>
  <div style="margin-top:16px;background:#1b1c20;color:#fff;border-radius:10px;padding:14px 16px"><div class="bh" style="font-size:64px;line-height:1">월요일</div><div style="font-family:Montserrat;font-weight:800;font-size:16px;opacity:.7;margin-top:4px">MON · 11.16 · 6 STATIONS</div></div>
  <div style="position:relative;margin-top:22px;padding-left:4px"><div style="position:absolute;left:12px;top:10px;bottom:10px;width:8px;background:${LC};border-radius:4px"></div>
  ${CL.map((c, i) => `<div style="display:flex;align-items:center;gap:16px;height:62px"><span class="stn" style="${i === 3 ? 'border-color:#1b1c20' : ''}"></span><div><div class="bh" style="font-size:21px">${c[1]}</div><div style="font-family:Montserrat;font-weight:600;font-size:13px;color:#777">${c[0]} · ${c[2]}${i === 3 ? ' · <b style="color:#1b1c20">환승 HEELS</b>' : ''}</div></div></div>`).join('')}</div></div>`,
`<div style="position:absolute;inset:0;background:url(${photo}) center/cover"></div>
  <div style="position:absolute;left:16px;right:16px;bottom:30px;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.35)">
    <div style="height:10px;background:${LC}"></div><div style="padding:16px 18px;display:flex;align-items:center;gap:14px"><span class="num" style="width:48px;height:48px;font-size:22px">J</span>
    <div><div class="bh" style="font-size:40px;line-height:1">키리<span style="font-size:20px;margin-left:8px;color:#777">KIRY</span></div><div style="font-family:Montserrat;font-weight:800;font-size:14px;color:${LC};margin-top:4px">JAZZ선 · 수 20:50 · A홀</div></div></div>
    <div style="display:flex;justify-content:space-between;padding:8px 18px;background:#f2f3f5;font-size:12px;font-weight:700;color:#555"><span>← 19:40 왁킹</span><span>RAW DANCE 수원</span></div></div>`,
`<div class="w" style="position:absolute;inset:0;padding:32px 44px">
  <div style="display:flex;align-items:center;gap:14px"><span class="num" style="width:44px;height:44px;font-size:22px">R</span><span class="bh" style="font-size:44px">RAW선 시즌 1 운행 현황</span><span style="margin-left:auto;font-family:Montserrat;font-weight:800;color:${LC};font-size:22px">종착까지 21일</span></div>
  <div style="position:relative;margin-top:60px;height:300px"><div style="position:absolute;left:30px;right:30px;top:120px;height:12px;background:${LC};border-radius:6px"></div>
  ${RK.map((r, i) => { const x = 30 + (5 - i) * 175; return `<div style="position:absolute;left:${x - 70}px;top:${i % 2 ? 160 : 0}px;width:140px;text-align:center">
    ${i % 2 ? `<div style="height:0"></div>` : ''}<div style="${i % 2 ? 'margin-top:0' : ''}"><div class="bh" style="font-size:${i === 0 ? 30 : 24}px;${i === 0 ? 'color:' + LC : ''}">${r[0]}</div><div style="font-family:Montserrat;font-weight:800;font-size:16px;color:#777">${r[1]}P · ${i + 1}위</div></div></div>
    <span class="stn" style="position:absolute;left:${x - 16}px;top:111px;width:32px;height:32px;${i === 0 ? 'background:' + LC + ';border-color:#1b1c20' : ''}"></span>`; }).join('')}
  <div style="position:absolute;right:0;top:-40px;font-family:Montserrat;font-weight:800;font-size:14px;color:#777">종착(1위) →</div></div>
  <div class="bh" style="position:absolute;left:0;right:0;bottom:0;height:52px;background:#1b1c20;color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px">🚇 내 이름을 눌러 승차 체크 · 수업 출석 · 연습 · 운동 · 일지</div></div>`);

// ── F. RECEIPT 영수증·티켓: 감열지 · 고정폭 글씨 · 바코드 · 절취선
const F = shell('F', `
body.F{background:#2b2b2e;color:#f1efe9}.F .rc{background:#fbfaf6;color:#111;font-family:"Nanum Gothic Coding",monospace}
.F .cut{border-top:2px dashed #999}.F .zz{position:absolute;left:0;right:0;height:12px;background:linear-gradient(-45deg,transparent 6px,#fbfaf6 6px) 0 0/12px 12px,linear-gradient(45deg,transparent 6px,#fbfaf6 6px) 0 0/12px 12px}`,
['SEASON 시안 F', 'RECEIPT 영수증 · 공연 티켓', '감열지 영수증 · 고정폭 글씨 · 바코드 · 절취선 · 티켓 도장'],
'오늘 수업은 영수증, 선생님 영상은 공연 티켓, 순위표는 "시즌 정산서". 소소하게 귀엽고 캡처·공유하기 좋음.',
`<div style="position:absolute;inset:0;background:#3a3a3e"></div><div class="rc" style="position:absolute;left:30px;right:30px;top:30px;bottom:40px;padding:26px 22px">
  <div style="text-align:center;font-weight:700;font-size:22px">RAW DANCE SUWON</div><div style="text-align:center;font-size:12px;margin-top:4px">*** TODAY'S CLASS RECEIPT ***</div>
  <div style="margin-top:14px;font-size:13px;display:flex;justify-content:space-between"><span>DATE 2026-11-16 (MON)</span><span>NO.0316</span></div><div class="cut" style="margin:10px 0"></div>
  ${CL.map(c => `<div style="display:flex;font-size:15px;margin:9px 0"><span style="width:56px;font-weight:700">${c[0]}</span><span style="flex:1;font-weight:700">${c[1]}</span><span>${c[2]}</span></div>`).join('')}
  <div class="cut" style="margin:12px 0"></div><div style="display:flex;justify-content:space-between;font-weight:700;font-size:18px"><span>TOTAL</span><span>6 CLASSES</span></div>
  <div style="margin-top:18px;height:46px;text-align:center">${bar(40)}</div><div style="text-align:center;font-size:11px;margin-top:4px">THANK YOU · SEE YOU ON THE FLOOR</div>
  <div class="zz" style="bottom:-12px"></div></div>`,
`<div style="position:absolute;inset:0;background:#3a3a3e"></div><div style="position:absolute;left:24px;right:24px;top:30px;bottom:30px;background:#fbfaf6;border-radius:12px;overflow:hidden">
  <div style="height:340px;background:url(${photo}) center/cover;filter:sepia(.25) contrast(1.05)"></div>
  <div style="padding:16px 20px;color:#111;font-family:'Nanum Gothic Coding'"><div style="font-size:12px;letter-spacing:.2em">ADMIT ONE · WEEKLY CLASS</div><div style="font-family:'Archivo Black';font-size:52px;line-height:1;margin-top:6px">KIRY</div>
  <div style="display:flex;gap:16px;margin-top:8px;font-weight:700;font-size:15px"><span>JAZZ</span><span>WED 20:50</span><span>A HALL</span></div></div>
  <div class="cut" style="margin:6px 14px"></div><div style="padding:8px 20px;display:flex;justify-content:space-between;align-items:center"><div style="height:34px">${bar(26)}</div><span style="border:3px solid #e2342b;color:#e2342b;font-family:'Archivo Black';padding:2px 10px;transform:rotate(-8deg);font-size:16px">RAW</span></div></div>`,
`<div style="position:absolute;inset:0;background:#3a3a3e"></div><div class="rc" style="position:absolute;left:150px;right:150px;top:24px;bottom:0;padding:26px 40px">
  <div style="display:flex;justify-content:space-between;align-items:flex-end"><div><div style="font-weight:700;font-size:30px">RAW SEASON 1 정산서</div><div style="font-size:13px;margin-top:4px">PRO 전문반 · 2026.12 · 마감까지 21일</div></div><div style="height:40px">${bar(30)}</div></div>
  <div class="cut" style="margin:14px 0 6px"></div>
  ${RK.map((r, i) => `<div style="display:flex;align-items:center;font-size:24px;height:58px;${i === 0 ? 'font-weight:700' : ''}"><span style="width:60px">${String(i + 1).padStart(2, '0')}</span><span style="width:150px">${r[0]}</span><span style="flex:1;border-bottom:2px dotted #999;margin:0 14px 6px"></span><span style="width:110px;font-size:16px">🔥${r[2]}주</span><span style="width:110px;text-align:right">${r[1]}P</span></div>`).join('')}
  <div class="cut" style="margin:10px 0"></div><div style="text-align:center;font-weight:700;font-size:18px">▼ 내 이름을 눌러 체크 · 영수증은 매일 갱신 ▼</div></div>`);

// ── G. MAGAZINE 잡지 표지: 마스트헤드 · 커버 문구 · 핫핑크
const PK = '#ff2e88';
const G = shell('G', `
body.G{background:#f4f4f2;color:#111}.G .bd{font-family:"Bodoni Moda",serif;font-weight:900}.G .ab{font-family:"Archivo Black"}.G .kr{font-family:"Noto Sans KR";font-weight:900}`,
['SEASON 시안 G', 'MAGAZINE 패션 잡지 표지', '큰 잡지 제호 · 커버 문구 · 핫핑크 포인트 · 호수·바코드'],
'매주가 "RAW 매거진" 새 호. 선생님 영상은 표지 모델, 순위표는 "이번 호 TOP 10". 고급스럽고 사진이 주인공.',
`<div style="position:absolute;inset:0;background:#fff;padding:22px 20px">
  <div class="bd" style="font-size:96px;line-height:.85;letter-spacing:-.04em;font-style:italic">RAW</div><div style="display:flex;justify-content:space-between;font-family:Montserrat;font-weight:800;font-size:11px;letter-spacing:.2em;margin-top:6px"><span>DAILY ISSUE</span><span style="color:${PK}">11.16 MON</span></div>
  <div style="height:3px;background:#111;margin:10px 0 14px"></div><div class="kr" style="font-size:26px;line-height:1.15">오늘의 수업<br><span style="color:${PK}">6 CLASSES</span></div>
  <div style="margin-top:14px;display:grid;gap:10px">${CL.map(c => `<div style="display:flex;gap:12px;align-items:baseline;border-bottom:1px solid #ddd;padding-bottom:8px"><span class="ab" style="font-size:20px;color:${PK}">${c[0]}</span><span class="kr" style="font-size:18px;flex:1">${c[1]}</span><span style="font-family:Montserrat;font-weight:600;font-size:11px;letter-spacing:.12em">${c[2]}</span></div>`).join('')}</div>
  <div style="position:absolute;right:16px;bottom:16px;background:#fff;padding:4px;height:44px">${bar(22)}</div></div>`,
`<div style="position:absolute;inset:0;background:url(${photo}) center/cover"></div>
  <div class="bd" style="position:absolute;left:14px;top:6px;font-size:118px;line-height:1;color:#fff;font-style:italic;mix-blend-mode:difference;letter-spacing:-.04em">RAW</div>
  <div style="position:absolute;left:18px;top:140px;color:#fff;font-family:Montserrat;font-weight:800;font-size:12px;letter-spacing:.2em">ISSUE 47 · WEEKLY CLASS</div>
  <div style="position:absolute;left:18px;bottom:110px;color:#fff"><div class="kr" style="font-size:16px;background:${PK};display:inline-block;padding:3px 10px">COVER STORY</div><div class="ab" style="font-size:58px;line-height:1;margin-top:8px">KIRY</div><div class="kr" style="font-size:20px;margin-top:4px">수요일 밤의 재즈</div></div>
  <div style="position:absolute;right:16px;bottom:30px;color:#fff;text-align:right;font-family:Montserrat;font-weight:800;font-size:14px">JAZZ<br>WED 20:50<br>A HALL</div>`,
`<div style="position:absolute;inset:0;background:#fff;display:grid;grid-template-columns:330px 1fr">
  <div style="background:url(${photo}) center/cover;position:relative"><div class="bd" style="position:absolute;left:18px;top:6px;font-size:110px;color:#fff;font-style:italic;mix-blend-mode:difference">RAW</div><div class="kr" style="position:absolute;left:20px;bottom:24px;color:#fff;font-size:22px;background:${PK};padding:4px 12px">SEASON 1 · 47호</div></div>
  <div style="padding:30px 40px"><div class="ab" style="font-size:20px;letter-spacing:.1em;color:${PK}">THE RANKING</div><div class="bd" style="font-size:66px;line-height:1;font-style:italic">Top of the Season</div>
  <div style="margin-top:18px">${RK.map((r, i) => `<div style="display:flex;align-items:baseline;gap:20px;border-bottom:1px solid #ddd;height:62px;align-items:center"><span class="bd" style="font-size:${i === 0 ? 50 : 38}px;font-style:italic;width:60px;${i === 0 ? 'color:' + PK : ''}">${i + 1}</span><span class="kr" style="font-size:${i === 0 ? 30 : 24}px;flex:1">${r[0]}</span><span style="font-family:Montserrat;font-weight:600;font-size:14px;color:#888">🔥 ${r[2]} WEEKS</span><span class="ab" style="font-size:26px;width:100px;text-align:right">${r[1]}</span></div>`).join('')}</div>
  <div class="kr" style="margin-top:16px;font-size:18px;color:${PK}">→ 내 이름을 눌러 이번 호에 이름 올리기</div></div></div>`);

// ── H. MUSIC SHOW 음악방송 차트 · 직캠: 1위 발표 · ▲▼ 순위 변동 · REC
const H = shell('H', `
body.H{background:#0d0f1a;color:#fff}.H .kr{font-family:"Noto Sans KR";font-weight:900}.H .ab{font-family:"Archivo Black"}
.H .grad{background:linear-gradient(90deg,#3b5bff,#c13bff 55%,#ff3b9d)}.H .up{color:#3dffa0}.H .dn{color:#ff5a7a}`,
['SEASON 시안 H', 'MUSIC SHOW 음악방송 차트 · 직캠', '음방 1위 발표 · 순위 변동 ▲▼ · NEW · 직캠 REC · 방송 자막 띠'],
'K-POP 학원에 딱 맞는 "음방" 컨셉. 출석 순위 = 이번 주 차트, 선생님 영상 = 직캠, 1등 = "1위 트로피".',
`<div style="position:absolute;inset:0;background:radial-gradient(circle at 70% 10%,#3b2a8a,#0d0f1a 60%);padding:24px 20px">
  <div style="display:flex;justify-content:space-between;align-items:center"><span class="ab" style="font-size:14px;letter-spacing:.1em">RAW MUSIC</span><span style="background:#ff3b3b;font-family:Montserrat;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">● ON AIR</span></div>
  <div class="ab" style="font-size:22px;margin-top:22px;opacity:.7">TODAY'S CUE SHEET</div><div class="kr" style="font-size:58px;line-height:1.05">월요일 무대</div><div style="font-family:Montserrat;font-weight:800;color:#c13bff;font-size:16px">11.16 · 6 STAGES</div>
  <div style="margin-top:16px;display:grid;gap:8px">${CL.map((c, i) => `<div style="display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.07);border-radius:8px;padding:10px 12px"><span class="ab" style="font-size:12px;opacity:.6;width:24px">#${i + 1}</span><span class="ab" style="font-size:17px;width:58px">${c[0]}</span><span class="kr" style="font-size:18px;flex:1">${c[1]}</span><span style="font-size:11px;opacity:.7;font-family:Montserrat;font-weight:800">${c[2]}</span></div>`).join('')}</div></div>`,
`<div style="position:absolute;inset:0;background:url(${photo}) center/cover"></div>
  <div style="position:absolute;left:14px;top:14px;display:flex;gap:8px;align-items:center;font-family:Montserrat;font-weight:800;font-size:14px"><span style="width:12px;height:12px;border-radius:50%;background:#ff3b3b"></span>REC 00:15</div>
  <div style="position:absolute;right:14px;top:14px;font-family:'Archivo Black';font-size:12px;letter-spacing:.1em;opacity:.85">RAW FANCAM</div>
  <div style="position:absolute;left:0;right:0;bottom:44px"><div class="grad" style="padding:8px 16px;display:inline-block;border-radius:0 8px 8px 0"><span class="ab" style="font-size:30px">KIRY</span></div>
  <div style="background:rgba(13,15,26,.85);padding:8px 16px;margin-top:4px;display:inline-block;border-radius:0 8px 8px 0" class="kr"><span style="font-size:16px">수요일 재즈 직캠 · WED 20:50</span></div></div>`,
`<div style="position:absolute;inset:0;background:radial-gradient(circle at 80% 0%,#3b2a8a,#0d0f1a 55%);padding:30px 44px">
  <div style="display:flex;align-items:center;gap:16px"><span class="ab" style="font-size:16px;background:#ff3b3b;padding:4px 10px;border-radius:4px">LIVE</span><span class="ab" style="font-size:42px">RAW CHART · WEEK 4</span><span style="margin-left:auto;font-family:Montserrat;font-weight:800;opacity:.7;font-size:18px">시즌 1 · 마감 21일</span></div>
  <div style="display:grid;grid-template-columns:330px 1fr;gap:26px;margin-top:22px">
    <div class="grad" style="border-radius:20px;padding:24px;height:470px;position:relative"><div class="ab" style="font-size:22px">THIS WEEK</div><div class="ab" style="font-size:120px;line-height:1">1위</div><div class="kr" style="font-size:44px;margin-top:20px">${RK[0][0]}</div><div class="ab" style="font-size:28px;margin-top:8px">${RK[0][1]}P · 🔥4</div><div style="position:absolute;right:20px;bottom:16px;font-size:80px">🏆</div></div>
    <div>${RK.slice(1).map((r, i) => `<div style="display:flex;align-items:center;gap:18px;height:86px;border-bottom:1px solid rgba(255,255,255,.12)"><span class="ab" style="font-size:40px;width:56px">${i + 2}</span>
      <span class="ab ${['up', 'dn', 'up', '', 'dn'][i]}" style="font-size:16px;width:56px">${['▲1', '▼1', '▲2', 'NEW', '▼2'][i]}</span><span class="kr" style="font-size:30px;flex:1">${r[0]}</span><span class="ab" style="font-size:26px">${r[1]}</span></div>`).join('')}</div></div>
  <div class="grad kr" style="position:absolute;left:0;right:0;bottom:0;height:46px;display:flex;align-items:center;justify-content:center;font-size:20px">🎤 내 이름을 눌러 투표(출석)하기</div></div>`);

(async () => {
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [k, h] of [['e', E], ['f', F], ['g', G], ['h', H]]) {
    await p.setContent(h); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(700);
    await p.screenshot({ path: path.join(__dirname, `concept-${k}.png`) });
  }
  await b.close(); console.log('ok');
})();
