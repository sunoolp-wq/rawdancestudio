#!/bin/bash
# 인스타 스토리 예약: 더블클릭 → 내일(또는 입력한 날짜) 예약 표 → y 누르면 Ego Lite가 예약
# 준비: Ego Lite 켜기(Meta 비즈니스 스위트 로그인 상태), 날짜 붙은 15초 영상(MMDD_쌤15초_쌤_장르.mp4)을 ~/Movies/RAW 영상공장 에 넣기
cd "$(dirname "$0")" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
echo "=== RAW 스토리 예약 ==="
read -r -p "날짜 (엔터 = 내일, 예: 2026-11-24): " D
if [ -z "$D" ]; then node tools/daily-story/schedule_stories.js --tomorrow; else node tools/daily-story/schedule_stories.js "$D"; fi
echo ""; read -n 1 -s -r -p "아무 키나 누르면 창이 닫혀요"; exit 0
