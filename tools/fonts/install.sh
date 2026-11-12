#!/usr/bin/env bash
# 카드·포스터·영상 렌더용 글꼴 설치 (새 작업 환경에서 한 번). 이미 있으면 건너뜀.
set -e
DIR="$HOME/.local/share/fonts"; mkdir -p "$DIR"
get() { # 패밀리(URL 표기) 굵기 파일명
  [ -s "$DIR/$3" ] && return 0
  url=$(curl -sS -m 20 "https://fonts.googleapis.com/css2?family=$1:wght@$2&display=swap" | grep -o 'https://fonts.gstatic.com[^)]*' | head -1)
  [ -n "$url" ] && curl -sS -m 60 -o "$DIR/$3" "$url" && echo "설치: $3"
}
for w in 300 400 500 700 900; do get "Noto+Sans+KR" $w "NotoSansKR-$w.ttf"; done
for w in 500 600 700 800; do get "Montserrat" $w "Montserrat-$w.ttf"; done
get "Montserrat" "700" "Montserrat-700.ttf"
get "Anton" 400 "Anton.ttf"; get "Bebas+Neue" 400 "BebasNeue.ttf"; get "Black+Han+Sans" 400 "BlackHanSans.ttf"
# 원장님 글꼴 (GoGo Poster 2020: TRACKPAD 자막용, 원장님 제공 파일, 2026-11-13 저장소에 보관)
for f in "$(dirname "$0")"/private/*.otf; do [ -e "$f" ] && { [ -s "$DIR/$(basename "$f")" ] || { cp "$f" "$DIR/" && echo "설치: $(basename "$f")"; }; }; done
fc-cache -f >/dev/null 2>&1 || true
