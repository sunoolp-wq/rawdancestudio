// 자막 시안 6종 렌더 → style-drafts/s1.png ~ s6.png (장면 3개 나란히) + all.jpg
// 사용: node render.js 배경폴더(bg_hook.jpg, bg_usp.jpg, bg_end.jpg)
const { launch } = require('../../../tools/pw.js'); const path = require('path'); const { execFileSync } = require('child_process');
const BG = process.argv[2], OUT = __dirname;
const NAMES = ['', '1 에디토리얼', '2 빅 타이포', '3 시네마', '4 스트릿 라벨', '5 LED 네온', '6 촬영 화면(HUD)'];
(async () => {
  const b = await launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (let s = 1; s <= 6; s++) {
    const shots = [];
    for (const sc of ['hook', 'usp', 'end']) {
      await p.goto(`file://${path.join(OUT, 'drafts.html')}?s=${s}&scene=${sc}&bg=${encodeURIComponent('file://' + path.join(BG, 'bg_' + sc + '.jpg'))}`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
      const f = path.join(BG, `s${s}_${sc}.png`); await p.screenshot({ path: f }); shots.push(f);
    }
    execFileSync('ffmpeg', ['-v', 'error', '-y', ...shots.flatMap(f => ['-i', f]), '-filter_complex',
      `[0][1][2]hstack=3,scale=1620:-1,pad=iw:ih+90:0:90:color=0x0e0d12,drawtext=fontfile=/root/.local/share/fonts/NotoSansKR-900.ttf:text='시안 ${NAMES[s]}':x=30:y=22:fontsize=46:fontcolor=white`,
      path.join(OUT, `s${s}.jpg`)]);
  }
  await b.close();
  execFileSync('ffmpeg', ['-v', 'error', '-y', ...[1, 2, 3, 4, 5, 6].flatMap(s => ['-i', path.join(OUT, `s${s}.jpg`)]), '-filter_complex', '[0][1][2][3][4][5]vstack=6', '-q:v', '3', path.join(OUT, 'all.jpg')]);
  console.log('ok');
})();
