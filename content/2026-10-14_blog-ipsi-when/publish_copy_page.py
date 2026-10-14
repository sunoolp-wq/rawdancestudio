"""tools/blog_copy_page.py 결과물(naver-blog-copy.html)을 아티팩트로 띄우기 좋게 다듬는다.
- 문서 껍데기(doctype/html/head/body) 제거, 제목 고정
- 맨 아래에 카드뉴스 5장·A/B홀 시간표 이미지와 '이미지 복사' 버튼 추가
사용: python3 tools/blog_copy_page.py content/2026-10-14_blog-ipsi-when/naver-blog.md
     python3 content/2026-10-14_blog-ipsi-when/publish_copy_page.py
"""
import re
from pathlib import Path

p = Path(__file__).with_name("naver-blog-copy.html")
s = p.read_text(encoding="utf-8")
s = re.sub(r"<!doctype html><html[^>]*><head><meta charset=\"utf-8\">\s*<meta name=\"viewport\"[^>]*>\s*", "", s)
s = s.replace("<title>블로그 붙여넣기용</title>", "<title>실용무용 입시 언제부터 복붙</title>")
s = s.replace("</style></head><body>", ":root{color-scheme:light}\n.imgs{display:flex;flex-direction:column;gap:14px}\n.imgs figure{margin:0;display:flex;flex-direction:column;gap:6px}\n.imgs img{width:100%;max-width:100%;border-radius:6px;display:block}\n.imgs figcaption{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted)}\n.wrap{padding-left:max(0px,env(safe-area-inset-left,0px));padding-right:max(0px,env(safe-area-inset-right,0px))}\n</style>")
s = s.replace("</script></body></html>", "</script>")

imgs = [(f"card{i}.png", f"카드뉴스 {i}장") for i in range(1, 6)] + [
    ("timetable-a-hall-2026-10.png", "A홀 10월 시간표"), ("timetable-b-hall-2026-10.png", "B홀 10월 시간표")]
figs = "".join(
    f'<figure><img src="{f}" alt="{a}" loading="lazy"><figcaption>{a}'
    f'<button data-img="{f}">이미지 복사</button><span class="ok"></span></figcaption></figure>' for f, a in imgs)
sec = (f'<section><div class="bar"><h2>4. 이미지 (파란 칸 자리에 넣기)</h2></div>'
       f'<p class="sub">이미지 복사 → 파란 칸 자리에 붙여넣기. 안 되면 이미지를 길게 눌러(PC는 우클릭) 저장한 뒤 올리세요.</p>'
       f'<div class="imgs">{figs}</div></section>\n')
js = """<script>
document.querySelectorAll('button[data-img]').forEach(b=>b.onclick=()=>{
 const ok=b.nextElementSibling;
 try{navigator.clipboard.write([new ClipboardItem({'image/png':fetch(b.dataset.img).then(r=>r.blob()).then(x=>new Blob([x],{type:'image/png'}))})])
  .then(()=>{ok.textContent='복사됨';setTimeout(()=>ok.textContent='',2000)})
  .catch(()=>{ok.textContent='복사 안 됨: 길게 눌러 저장'});}
 catch(e){ok.textContent='복사 안 됨: 길게 눌러 저장'}
});
</script>"""
s = s.replace("</div>\n<script>", sec + "</div>\n<script>", 1) + "\n" + js
p.write_text(s, encoding="utf-8")
print(p)
