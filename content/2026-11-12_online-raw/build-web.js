// 학원 홈페이지용(로그인 없이 공개) 버전 만들기: node build-web.js → web/index.html
// firebase-config.json 에 원장님 Firebase 웹 앱 설정을 넣어 두면 친구들끼리 서로 보임 (없으면 혼자 하는 버전)
const fs = require('fs'), path = require('path');
const dir = __dirname, src = fs.readFileSync(path.join(dir, 'raw-online.html'), 'utf8');
let cfg = null; try { cfg = JSON.parse(fs.readFileSync(path.join(dir, 'firebase-config.json'), 'utf8')); } catch (e) {}
const V = '10.12.2', fb = cfg ? ['app', 'auth', 'database'].map(m => `<script src="https://www.gstatic.com/firebasejs/${V}/firebase-${m}-compat.js"></script>`).join('\n') + `\n<script>window.RAW_FB = ${JSON.stringify(cfg)};</script>\n` : '';
const head = `<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="로우댄스학원 수원점 온라인 연습실. 친구들이랑 같이 들어와서 거울 보고 춤춰요.">
<meta property="og:title" content="RAW 온라인 연습실"><meta property="og:description" content="로우댄스학원 수원점을 3D로 걸어 다니며 같이 춤춰요">
<style>*{box-sizing:border-box;margin:0}html,body{height:100%;background:#0e0d12}</style>
</head><body>
`;
// 메인 스크립트(three.js 다음) 앞에 Firebase를 넣는다
const out = head + src.replace('<script>\n(() => {', fb + '<script>\n(() => {') + '\n</body></html>\n';
if (!out.includes('(() => {')) throw new Error('main script not found');
fs.mkdirSync(path.join(dir, 'web'), { recursive: true });
fs.writeFileSync(path.join(dir, 'web', 'index.html'), out);
console.log('web/index.html', cfg ? '(같이 보이기 켜짐: ' + cfg.projectId + ')' : '(혼자 버전: firebase-config.json 없음)', out.length, 'bytes');
