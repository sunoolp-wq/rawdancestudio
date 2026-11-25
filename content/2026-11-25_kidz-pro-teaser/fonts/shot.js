const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const v of ['A','B','C','D','E']) for(const s of ['k','t']){await p.goto('file://'+path.join(__dirname,'fonts.html')+`?v=${v}&s=${s}`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(250);await p.screenshot({path:path.join(__dirname,`${v}_${s}.png`)});}
await b.close();})();
