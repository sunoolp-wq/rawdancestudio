# 강사 수업 영상 → 15초 릴스·스토리

    bash tools/fonts/install.sh          # 새 작업 환경이면 글꼴 먼저
    node tools/class-reel/make_reel.js --video 원본.mp4 --start 32 --dur 15 \
         --name KIRY --genre JAZZ --when "WED 20:50" --out content/<날짜>_<강사>-reel/reel.mp4

- 원장님 편집 스타일(2026-11-04 샘플): 구겨진 질감 배경 + 가운데 액자 영상 + 위 강사 이름(겹친 외곽선) + 오른쪽 요일·시간 스티커 + 아래 장르 테이프 2줄(흐름) + 끝 로고 1초
- 원본 소리 그대로 (앞 0.3초 페이드인, 끝 1초 페이드아웃). 1080x1920, 약 16초
- `--start`: 쓸 구간 시작 초 (원장님이 정해 주는 게 가장 정확)
