// 자막 시안 6종 렌더 → style-drafts/s1.png ~ s6.png (장면 3개 나란히) + all.jpg
// 사용: node render.js 배경폴더(bg_hook.jpg, bg_usp.jpg, bg_end.jpg) [drafts2.html] [7,8,9,10,11,12] [all2.jpg]
const { launch } = require('../../../tools/pw.js'); const path = require('path'); const { execFileSync } = require('child_process');
const BG = process.argv[2], OUT = __dirname, HTML = process.argv[3] || 'drafts.html', IDS = (process.argv[4] || '1,2,3,4,5,6').split(',').map(Number), ALL = process.argv[5] || 'all.jpg';
const NAMES = ['', '1 에디토리얼', '2 빅 타이포', '3 시네마', '4 스트릿 라벨', '5 LED 네온', '6 촬영 화면(HUD)', '7 크롬 Y2K', '8 반복 아웃라인 포스터', '9 영상 품은 글자', '10 채팅 말풍선', '11 숏폼 자막', '12 글리치'];
(async () => {
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const s of IDS) {
    const shots = [];
    for (const sc of ['hook', 'usp', 'end']) {
      await p.goto(`file://${path.join(OUT, HTML)}?s=${s}&scene=${sc}&bg=${encodeURIComponent('file://' + path.join(BG, 'bg_' + sc + '.jpg'))}`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
      const f = path.join(BG, `s${s}_${sc}.png`); await p.screenshot({ path: f }); shots.push(f);
    }
    execFileSync('ffmpeg', ['-v', 'error', '-y', ...shots.flatMap(f => ['-i', f]), '-filter_complex',
      `[0][1][2]hstack=3,scale=1620:-1,pad=iw:ih+90:0:90:color=0x0e0d12,drawtext=fontfile=/root/.local/share/fonts/NotoSansKR-900.ttf:text='시안 ${NAMES[s]}':x=30:y=22:fontsize=46:fontcolor=white`,
      path.join(OUT, `s${s}.jpg`)]);
  }
  await b.close();
  execFileSync('ffmpeg', ['-v', 'error', '-y', ...IDS.flatMap(s => ['-i', path.join(OUT, `s${s}.jpg`)]), '-filter_complex', IDS.map((_, i) => `[${i}]`).join('') + `vstack=${IDS.length}`, '-q:v', '3', path.join(OUT, ALL)]);
  console.log('ok');
})();
