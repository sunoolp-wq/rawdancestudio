# 학원 맥에서 영상 도구 쓰기 (처음 한 번)

    brew install ffmpeg node                 # Homebrew 없으면 https://brew.sh 먼저
    cd ~/rawdancestudio/tools && npm init -y >/dev/null && npm install playwright && npx playwright install chromium
    bash ~/rawdancestudio/tools/fonts/install.sh

## 수업 영상 → 15초 릴스 (RAW 스타일)
    node tools/class-reel/make_reel2.js --video "<영상>" --start 5 --dur 15 --name KIRY --genre JAZZ \
         --when "WED 20:50" --whenKr "매주 수 20:50" --hall A --out "content/<날짜>_<강사>-reel/reel.mp4"
- 강사·장르·요일·홀은 brand/brand-guide.md 시간표 기준. 곡 이름은 영상에 넣지 않는다 (--track 쓰지 않음).
- 결과 영상은 원장님 폴더(예: ~/Desktop/클로드의 데일리/완성)에도 복사해 바로 올릴 수 있게 한다.
- 릴스 캡션은 .claude/agents/caption-instagram.md 고정 양식.

## 매일 스토리 영상
    node tools/daily-story/render.js 2026-11-10
