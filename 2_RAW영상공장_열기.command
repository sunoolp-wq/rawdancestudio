#!/bin/bash
# RAW 영상공장 열기 → 크롬(기본 브라우저)에 화면이 떠요. 이 검은 창은 쓰는 동안 켜 두세요 (닫으면 멈춤)
cd "$(dirname "$0")"
for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
if [ ! -x .venv/bin/python ]; then echo "먼저 '1_설치하기.command'를 실행해 주세요"; read -n 1 -s; exit 1; fi
if curl -s -o /dev/null http://127.0.0.1:5577/; then open "http://127.0.0.1:5577"; exit 0; fi
(sleep 2; open "http://127.0.0.1:5577") &
.venv/bin/python tools/raw-studio/server.py
