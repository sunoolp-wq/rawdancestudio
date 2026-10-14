"""naver-blog.md → 네이버 블로그 붙여넣기용 HTML 페이지.

사용: python3 tools/blog_copy_page.py content/<폴더>/naver-blog.md
결과: 같은 폴더에 naver-blog-copy.html (크롬에서 열고 '복사' → 네이버 에디터에 붙여넣기)

naver-blog.md 본문(첫 번째와 두 번째 '---' 사이) 표기 규칙:
  <<소제목>>텍스트      → 맨 위 헤더 (24)
  <<중제목>>텍스트      → 본문 중간 소제목 (19)
  <<강조>>텍스트        → 핵심 문장·학생 한마디 (19)
  <<작게>>텍스트        → 보조 설명 (13)
  표시 없음             → 본문 (16), '•'·'✅'로 시작하면 목록 (15)
  고정 블록 영역은 15, 해시태그는 13
  [구분선]              → 파란 칸: 에디터 툴바에서 구분선 넣을 자리
  [사진 …] [GIF …] [영상 …] [지도 …] [링크 카드 …] [이미지 …] → 파란 칸: 넣을 자리
  (사진 설명) …  (영상 제목) … → 바로 위 파란 칸에 합쳐서 표시 (사진 설명 칸에 넣을 글)
  [확인필요: …]         → 빨간 칸
  '✅ 클래스'로 시작하는 줄 바로 앞의 [구분선]부터 → '고정 블록' 영역
  '#'로 시작하는 마지막 줄 → '해시태그' 영역
"""
import html
import re
import sys
from pathlib import Path

BASE = "font-family:'나눔다시시작해','NanumDaSiSiJagHae';text-align:center;font-weight:bold;margin:0;"
SIZE = {"head": 24, "sub": 19, "strong": 19, "body": 16, "list": 15, "small": 13}
MARK = {"<<소제목>>": "head", "<<중제목>>": "sub", "<<강조>>": "strong", "<<작게>>": "small"}


def style(size):
    return f"{BASE}font-size:{size}px;"


TXT = style(SIZE["body"])
SLOT = re.compile(r"\[(구분선|사진|GIF|영상|지도|링크 카드|이미지)[^\]]*\]")


def blocks(lines):
    out = []
    for raw in lines:
        l = raw.rstrip()
        if l.startswith("(사진 설명)") or l.startswith("(영상 제목)"):
            if out and out[-1][0] == "slot":
                out[-1][2].append(l)
                continue
        if SLOT.fullmatch(l.strip()):
            out.append(["slot", l.strip(), []])
        else:
            for mk, kind in MARK.items():
                if l.startswith(mk):
                    out.append([kind, l[len(mk):], []])
                    break
            else:
                out.append(["text", l, []])
    return out


def render(lines, default="body"):
    html_out = []
    for kind, text, extra in blocks(lines):
        if kind == "slot":
            label = "── 구분선 넣기 ──" if text == "[구분선]" else text
            sub = "".join(f"<br><span class='cap'>{html.escape(x)}</span>" for x in extra)
            html_out.append(f'<p class="ph" style="{TXT}">▶ {html.escape(label)}{sub}</p>')
        elif not text.strip():
            html_out.append(f'<p style="{style(SIZE[default])}"><br></p>')
        else:
            if kind == "text":
                kind = "list" if default == "body" and text.lstrip()[:1] in ("•", "✅") else default
            e = html.escape(text)
            e = re.sub(r"\[확인필요:[^\]]*\]", lambda m: f'<span class="chk">{m.group(0)}</span>', e)
            html_out.append(f'<p style="{style(SIZE[kind])}">{e}</p>')
    return "\n".join(html_out)


def main(src):
    src = Path(src)
    head, body, _ = src.read_text(encoding="utf-8").split("\n---\n", 2)
    m = re.search(r"제목 A \(추천\): (.*)", head) or re.search(r"제목[^:]*: (.*)", head)
    title = m.group(1).strip() if m else ""
    lines = body.strip("\n").split("\n")
    i_fix = next(i for i, l in enumerate(lines) if l.startswith("✅ 클래스"))
    while i_fix > 0 and (not lines[i_fix - 1].strip() or lines[i_fix - 1].strip() == "[구분선]"):
        i_fix -= 1
    i_tag = max(i for i, l in enumerate(lines) if l.startswith("#"))
    parts = {"본문": (lines[:i_fix], "body"), "고정 블록": (lines[i_fix:i_tag], "list"),
             "해시태그": (lines[i_tag:], "small")}

    secs = ""
    for n, (name, (ls, default)) in enumerate(parts.items()):
        secs += (
            f'<section><div class="bar"><h2>{n + 1}. {name}</h2>'
            f'<button data-t="s{n}">복사</button><span class="ok" id="ok{n}"></span></div>'
            f'<div class="paper" id="s{n}">{render(ls, default)}</div></section>\n'
        )

    page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>블로그 붙여넣기용</title>
<style>
:root{{--bg:#f4f4f2;--paper:#fff;--ink:#333;--muted:#777;--ph:#eef3ff;--phink:#3355aa;--chk:#ffe3e3;--chkink:#b00020;--btn:#03c75a}}
body{{background:var(--bg);color:var(--ink);font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;margin:0;padding:24px 16px}}
.wrap{{max-width:375px;margin:0 auto}}
h1{{font-size:18px;margin:0 0 4px}} .sub{{color:var(--muted);font-size:13px;margin:0 0 20px;line-height:1.7}}
.title{{background:var(--paper);padding:12px 14px;border-radius:8px;margin-bottom:20px;font-size:15px}}
section{{margin-bottom:28px}} .bar{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
h2{{font-size:15px;margin:0}}
button{{background:var(--btn);color:#fff;border:0;border-radius:6px;padding:7px 16px;font-size:14px;cursor:pointer}}
.ok{{color:var(--btn);font-size:13px}}
.paper{{background:var(--paper);padding:28px 0;border-radius:8px;line-height:1.9;width:343px;max-width:100%;margin:0 auto;box-sizing:content-box}}
.ph{{background:var(--ph);color:var(--phink)!important;font-weight:normal!important;font-size:13px;border-radius:4px;padding:6px 10px!important;margin:6px 0!important;line-height:1.6}}
.cap{{color:#555}}
.chk{{background:var(--chk);color:var(--chkink)}}
</style></head><body><div class="wrap">
<h1>네이버 블로그 붙여넣기용</h1>
<p class="sub">초록 <b>복사</b> → 네이버 에디터에 붙여넣기(⌘+V).<br>
<b>파란 칸</b> = 툴바에서 넣을 것 (사진·구분선·지도·링크). 넣은 뒤 파란 칸 줄은 삭제.<br>
'사진 설명'은 사진을 넣고 사진 아래 설명 칸에 옮겨 적기.<br>
<b>빨간 칸</b> = 발행 전 확인할 것.<br>
이 페이지 폭(약 휴대폰 화면)에서 줄이 끊기는 모양 그대로 모바일에서 보입니다.</p>
<div class="title">제목: <b>{html.escape(title)}</b></div>
{secs}</div>
<script>
document.querySelectorAll('button[data-t]').forEach((b,n)=>b.onclick=async()=>{{
 const el=document.getElementById(b.dataset.t), ok=document.getElementById('ok'+n);
 try{{
  await navigator.clipboard.write([new ClipboardItem({{
   'text/html':new Blob([el.innerHTML],{{type:'text/html'}}),
   'text/plain':new Blob([el.innerText],{{type:'text/plain'}})}})]);
 }}catch(e){{
  const r=document.createRange();r.selectNodeContents(el);const s=getSelection();
  s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges();
 }}
 ok.textContent='복사됨';setTimeout(()=>ok.textContent='',2000);
}});
</script></body></html>"""
    dst = src.with_name("naver-blog-copy.html")
    dst.write_text(page, encoding="utf-8")
    print(dst, {k: len(v[0]) for k, v in parts.items()})


if __name__ == "__main__":
    main(sys.argv[1])
