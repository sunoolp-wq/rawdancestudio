# 강사 수업 영상 → 15초 릴스·스토리

    bash tools/fonts/install.sh          # 새 작업 환경이면 글꼴 먼저
    node tools/class-reel/make_reel.js --video 원본.mp4 --start 32 --dur 15 \
         --name KIRY --genre JAZZ --when "WED 20:50" --out content/<날짜>_<강사>-reel/reel.mp4

- 원장님 편집 스타일(2026-11-04 샘플): 구겨진 질감 배경 + 가운데 액자 영상 + 위 강사 이름(겹친 외곽선) + 오른쪽 요일·시간 스티커 + 아래 장르 테이프 2줄(흐름) + 끝 로고 1초
- 원본 소리 그대로 (앞 0.3초 페이드인, 끝 1초 페이드아웃). 1080x1920, 약 16초
- `--start`: 쓸 구간 시작 초 (원장님이 정해 주는 게 가장 정확)

## RAW 스타일 (기본, 2026-11-04 원장님 "너 스타일로")
    node tools/class-reel/make_reel2.js --video 원본.mp4 --start 32 --dur 15 --name KIRY --genre JAZZ \
         --when "WED 20:50" --whenKr "매주 수 20:50" --hall A --out 결과.mp4
- 영상 전체 화면(9:16) + 아래 요일·홀 칩, 큰 강사 이름, 보라 외곽선 장르, 진행 바
- 곡 이름은 영상에 넣지 않는다 (지난 수업 곡이 오늘 곡처럼 보임, 원장님 지시 2026-11-04). `--track`은 쓰지 않는다
- 끝 2초: 다크·보라 끝 화면 (T. 강사 / 장르 · 요일 시간 / 문의) — 스토리 영상·시간표와 같은 색
- 위 `make_reel.js`는 원장님 기존 편집 스타일(액자형) 재현본

## 가로 영상 → 선생님 따라가는 세로 자르기 (2026-11-04 원장님 요청: "선생님이 계속 화면 가운데")
    pip install "opencv-python-headless<5" numpy
    python3 tools/class-reel/follow_crop.py --video 원본.mp4 --start 5 --dur 15 --out 세로.mp4
    node tools/class-reel/make_reel2.js --video 세로.mp4 --start 0 --dur 15 ...
- 사람 찾기(HOG) + 움직임으로 선생님(앞 가운데·가장 큰 사람)을 따라 9:16 창을 부드럽게 옮긴다
- 세로 원본이면 그냥 9:16으로만 맞춤
- 단체 수업에서 학생을 잠깐 따라갈 수 있다 → 결과를 확인하고 이상하면 구간을 바꾼다
- 가로 원본은 4K일수록 선명 (1080p 가로를 세로로 자르면 화질이 떨어짐)
