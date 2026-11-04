// 클라우드·맥 어디서나 같은 코드로 크롬 띄우기
const fs = require('fs');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
const CLOUD = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
module.exports.launch = () => pw.chromium.launch(fs.existsSync(CLOUD) ? { executablePath: CLOUD, args: ['--no-sandbox'] } : {});
