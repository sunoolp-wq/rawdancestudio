# 사용: python3 make_carousel.py  → slide1.html, slide2.html (인스타 캐러셀 1080x1350)
# 원칙: 휴대폰에서 읽히게 본문 최소 24px, 회색 글씨 최소화
BG='#0e0d12'; FG='#f4f2ee'; MUTE='#c3bfcc'; LINE='rgba(244,242,238,.22)'; ACC='#b9a6ff'
HEAD=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Montserrat:wght@500;600&display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1350px}}
body{{font-family:"Noto Sans KR",sans-serif;background:{BG};color:{FG};position:relative;overflow:hidden}}
.glow{{position:absolute;width:1100px;height:1100px;border-radius:50%;left:-420px;bottom:-560px;background:radial-gradient(circle,rgba(124,92,255,.32),rgba(124,92,255,0) 62%)}}
.p{{position:absolute;inset:72px 76px 64px}}
.logo{{height:58px}}
'''

s1=HEAD+f'''
.kick{{margin-top:150px;font-size:60px;font-weight:400;letter-spacing:-1.5px}}
.big{{margin-top:16px;font-weight:900;font-size:322px;line-height:.98;letter-spacing:-20px;margin-left:-12px}}
.big .a{{color:{ACC}}}
.meta{{margin-top:56px;font-size:40px;font-weight:500;letter-spacing:-1px;line-height:1.4}}
.meta span{{color:{ACC}}}
.bot{{position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:flex-end;font-size:30px;font-weight:700}}
</style></head><body><div class="glow"></div><div class="p">
<img class="logo" src="raw-logo.png">
<div class="kick">예고 · 대학</div>
<div class="big">입시반<br><span class="a">모집</span></div>
<div class="meta">2028학년도 입시 대비<br><span>현 중2 · 고2</span></div>
<div class="bot">자세히 보기 →</div>
</div></body></html>'''

s2=HEAD+f'''
.h{{margin-top:44px;font-size:64px;font-weight:900;letter-spacing:-2.5px}}
.h span{{color:{ACC}}}
.list{{margin-top:30px}}
.it{{display:flex;align-items:baseline;gap:26px;padding:20px 0;border-top:1px solid {LINE};font-size:38px;font-weight:700;letter-spacing:-1px}}
.it:last-child{{border-bottom:1px solid {LINE}}}
.it i{{font-style:normal;font-family:Montserrat;font-weight:600;font-size:26px;color:{ACC}}}
.track{{margin-top:44px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
.st{{border-top:3px solid {FG};padding-top:14px}}
.st:last-child{{border-color:{ACC}}}
.st b{{display:block;font-size:34px;font-weight:900;letter-spacing:-1px}}
.st span{{display:block;margin-top:6px;font-size:25px;font-weight:500;color:{MUTE};line-height:1.35}}
.info{{margin-top:48px;display:flex;flex-direction:column;gap:14px}}
.info div{{font-size:38px;font-weight:700;letter-spacing:-1px}}
.info small{{font-size:28px;font-weight:500;color:{ACC};margin-right:18px}}
.bot{{position:absolute;left:0;right:0;bottom:0}}
.ct{{font-size:30px;font-weight:700;letter-spacing:-0.5px;line-height:1.45}}
.lg{{margin-top:14px;padding-top:14px;border-top:1px solid {LINE};font-size:21px;font-weight:400;color:{MUTE};line-height:1.55}}
</style></head><body><div class="glow"></div><div class="p">
<img class="logo" src="raw-logo.png">
<div class="h">RAW <span>입시반</span></div>
<div class="list">
 <div class="it"><i>01</i>전 클래스 프리패스 (K-POP 포함)</div>
 <div class="it"><i>02</i>연습실 상시 개방</div>
 <div class="it"><i>03</i>월말평가 · 모의고사 · 작품 레슨</div>
 <div class="it"><i>04</i>대회 · 공연 · 버스킹 무대</div>
</div>
<div class="track">
 <div class="st"><b>10~12월</b><span>상담 · 레벨 체크</span></div>
 <div class="st"><b>1~3월</b><span>기본기 · 작품 구상</span></div>
 <div class="st"><b>4~8월</b><span>작품 완성 · 대회</span></div>
 <div class="st"><b>9~10월</b><span>보완 · 모의고사</span></div>
</div>
<div class="info">
 <div><small>대상</small>현 중2 · 고2</div>
 <div><small>상담</small>DM · 카카오톡 예약 후 방문</div>
</div>
<div class="bot">
 <div class="ct">☎ 031-225-6600 · @rawdance_suwon<br>카카오톡 로우댄스수원점학원</div>
 <div class="lg">교습비 월 50만원 (전문반: 금 18:30~20:00 주 1회 + 전 클래스 프리패스)<br>콘서트·버스킹 참여 시 의상비 별도 · 수원시 팔달구 매산로 136, 4층 · 학원등록 제8189호</div>
</div>
</div></body></html>'''
open('slide1.html','w',encoding='utf-8').write(s1)
open('slide2.html','w',encoding='utf-8').write(s2)
