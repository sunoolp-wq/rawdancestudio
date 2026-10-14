# 사용: python3 make_cards.py → card1~5.html (1080x1350, 블로그·인스타 카드뉴스)
# 원칙: 휴대폰에서 읽히게 본문 최소 26px, 회색 최소화, 교습비는 블로그 규칙상 미기재
BG='#0e0d12'; FG='#f4f2ee'; MUTE='#c3bfcc'; LINE='rgba(244,242,238,.22)'; ACC='#b9a6ff'
HEAD=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Montserrat:wght@600&display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1350px}}
body{{font-family:"Noto Sans KR",sans-serif;background:{BG};color:{FG};position:relative;overflow:hidden}}
.glow{{position:absolute;width:1100px;height:1100px;border-radius:50%;left:-420px;bottom:-560px;background:radial-gradient(circle,rgba(124,92,255,.32),rgba(124,92,255,0) 62%)}}
.p{{position:absolute;inset:72px 76px 64px}}
.logo{{height:52px}}
.no{{position:absolute;right:0;top:8px;font-family:Montserrat;font-weight:600;font-size:24px;color:{MUTE}}}
.k{{font-size:34px;font-weight:700;color:{ACC};letter-spacing:-1px}}
.bot{{position:absolute;left:0;right:0;bottom:0;font-size:26px;font-weight:500;color:{MUTE}}}
'''
def page(n, css, body):
    return HEAD+css+f'</style></head><body><div class="glow"></div><div class="p"><img class="logo" src="raw-logo.png"><div class="no">{n}/5</div>'+body+'</div></body></html>'

cards={}
cards[1]=page(1,f'''
.kick{{margin-top:200px;font-size:52px;font-weight:500;letter-spacing:-1.5px}}
.big{{margin-top:20px;font-weight:900;font-size:150px;line-height:1.08;letter-spacing:-8px}}
.big .a{{color:{ACC}}}
.sub{{margin-top:44px;font-size:38px;font-weight:500;line-height:1.45;letter-spacing:-1px}}
.bot{{display:flex;justify-content:flex-end;color:{FG};font-weight:700;font-size:30px}}
''','''<div class="kick">예고 · 대학</div>
<div class="big">실용무용 입시<br><span class="a">언제부터?</span></div>
<div class="sub">준비 시기와 1년 순서를<br>한 번에 정리했어요</div>
<div class="bot">넘겨 보기 →</div>''')

cards[2]=page(2,f'''
.q{{margin-top:120px}}
.ans{{margin-top:26px;font-size:96px;font-weight:900;line-height:1.12;letter-spacing:-4px}}
.ans span{{color:{ACC}}}
.box{{margin-top:70px;border-top:1px solid {LINE};padding-top:40px;font-size:40px;font-weight:700;line-height:1.5;letter-spacing:-1px}}
.note{{margin-top:56px;font-size:28px;font-weight:500;color:{MUTE};line-height:1.55}}
''','''<div class="q"><div class="k">한 줄 답</div>
<div class="ans">시험 <span>1년 전</span>부터<br>시작하세요</div></div>
<div class="box">지금 중2 · 고2라면<br>이번 가을~겨울,<br>상담과 레벨 체크부터!</div>
<div class="note">※ 실기 일정과 종목은 학교 · 대학마다 달라요.<br>지원할 곳의 모집요강을 꼭 확인하세요.</div>''')

cards[3]=page(3,f'''
.h{{margin-top:80px;font-size:66px;font-weight:900;letter-spacing:-2.5px}}
.list{{margin-top:44px}}
.st{{display:flex;gap:36px;align-items:baseline;padding:34px 0;border-top:1px solid {LINE}}}
.st:last-child{{border-bottom:1px solid {LINE}}}
.st b{{flex:none;width:230px;font-size:46px;font-weight:900;letter-spacing:-1px}}
.st:first-child b{{color:{ACC}}}
.st span{{font-size:36px;font-weight:500;line-height:1.4;letter-spacing:-.8px}}
.now{{margin-top:34px;font-size:30px;font-weight:700;color:{ACC}}}
''','''<div class="k">로우댄스 수원점 입시반</div>
<div class="h">1년 준비 흐름</div>
<div class="list">
<div class="st"><b>10~12월</b><span>1:1 입시 상담<br>레벨 체크 · 목표 설정</span></div>
<div class="st"><b>1~3월</b><span>장르별 기본기 강화<br>입시 작품 구상</span></div>
<div class="st"><b>4~8월</b><span>입시 작품 완성<br>대회 · 공연 참가</span></div>
<div class="st"><b>9~10월</b><span>디테일 보완<br>모의고사 · 실전 대비</span></div>
</div>
<div class="now">지금이 바로 1단계예요</div>''')

cards[4]=page(4,f'''
.h{{margin-top:80px;font-size:66px;font-weight:900;letter-spacing:-2.5px;line-height:1.2}}
.grid{{margin-top:56px;display:grid;grid-template-columns:1fr 1fr;gap:22px}}
.c{{border:1px solid {LINE};border-radius:22px;padding:34px 30px;min-height:250px}}
.c i{{font-style:normal;font-family:Montserrat;font-weight:600;font-size:28px;color:{ACC}}}
.c b{{display:block;margin-top:14px;font-size:42px;font-weight:900;letter-spacing:-1.5px}}
.c span{{display:block;margin-top:12px;font-size:28px;font-weight:500;color:{MUTE};line-height:1.45}}
''','''<div class="k">지금 해 두면 좋은 것</div>
<div class="h">입시 준비,<br>이 4가지부터</div>
<div class="grid">
<div class="c"><i>01</i><b>기본기</b><span>리듬 · 그루브 · 라인<br>매주 꾸준히</span></div>
<div class="c"><i>02</i><b>여러 장르</b><span>나에게 맞는<br>장르 찾기</span></div>
<div class="c"><i>03</i><b>무대 경험</b><span>공연 · 버스킹으로<br>긴장 다루기</span></div>
<div class="c"><i>04</i><b>영상으로 보기</b><span>거울로 못 본 부분<br>스스로 찾기</span></div>
</div>''')

cards[5]=page(5,f'''
.h{{margin-top:70px;font-size:66px;font-weight:900;letter-spacing:-2.5px}}
.h span{{color:{ACC}}}
.it{{padding:24px 0;border-top:1px solid {LINE};font-size:36px;font-weight:700;letter-spacing:-1px}}
.it:last-of-type{{border-bottom:1px solid {LINE}}}
.list{{margin-top:36px}}
.who{{margin-top:40px;font-size:38px;font-weight:900;letter-spacing:-1px}}
.who small{{font-size:28px;color:{ACC};font-weight:700;margin-right:14px}}
.ct{{margin-top:14px;font-size:32px;font-weight:700;line-height:1.5}}
.bot{{font-size:20px;line-height:1.6}}
''','''<div class="k">로우댄스 수원점</div>
<div class="h">입시반 <span>상담 예약</span></div>
<div class="list">
<div class="it">전문반 고정수업 주 1회 (금 18:30~20:00)</div>
<div class="it">전 클래스 프리패스 · 연습실 상시 개방</div>
<div class="it">매월 마지막 주 금요일 월말평가</div>
<div class="it">대회 · 공연 · 버스킹 기회</div>
</div>
<div class="who"><small>대상</small>현 중2 · 고2 입시 준비생</div>
<div class="ct">카카오톡 채널 '로우댄스수원점학원'<br>DM @rawdance_suwon · ☎ 031-225-6600<br>방문 상담 시 레벨 체크</div>
<div class="bot">교습비 · 자세한 안내는 상담 시 · 콘서트·버스킹 참여 시 의상비 별도<br>수원시 팔달구 매산로 136, 4층 · 학원등록번호 제8189호</div>''')
for n,h in cards.items():
    open(f'card{n}.html','w',encoding='utf-8').write(h)
