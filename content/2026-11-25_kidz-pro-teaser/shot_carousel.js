const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(const s of [2,3,4,5]){await p.goto('file://'+path.join(__dirname,'carousel.html')+'?s='+s);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:path.join(__dirname,`slide${s}.png`)});}await b.close();})();
