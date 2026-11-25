const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const v of ['N','O','P','Q','R','S','T','U']) for(const s of ['k','t']){await p.goto('file://'+path.join(__dirname,'fonts3.html')+`?v=${v}&s=${s}`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(250);await p.screenshot({path:path.join(__dirname,`${v}_${s}.png`)});}
await b.close();})();
