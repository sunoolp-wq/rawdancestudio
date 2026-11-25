// node shot_carousel2.js → slide2~5.jpg (2차, 클로드 티 안 나게)
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(const s of [2,3,4,5]){await p.goto('file://'+path.join(__dirname,'carousel2.html')+'?s='+s);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:path.join(__dirname,`slide${s}.jpg`),type:'jpeg',quality:93});}await b.close();})();
