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

## (권장) YOLO로 선생님 따라가기 — `follow_yolo.py` (2026-11-04, HOG 방식보다 정확)
    python3 -m venv .venv && .venv/bin/pip install ultralytics lap      # 처음 한 번 (torch 포함, 용량 큼)
    .venv/bin/python tools/class-reel/follow_yolo.py --video 원본.mp4 --start 5 --dur 15 --out 세로.mp4 \
        --pick-x 0.5 --check 확인.jpg
- 모델: `tools/class-reel/yolo11s.pt` (없으면 github에서 자동 다운로드)
- 처음(--pick-t 초)에 --pick-x 위치(0 왼쪽 ~ 1 오른쪽)에 가장 크게 보이는 사람을 선생님으로 정하고, 번호(ByteTrack)로 끝까지 따라감. 번호를 잃으면 옷 색·위치·크기로 다시 찾음
- `--check` 사진: 보라 상자 = 선생님으로 잡은 사람, 흰 선 = 잘라 낸 세로 화면 → 원장님께 같이 보내 확인
- 원장님이 "선생님 옷·위치"를 알려 주면 --pick-x / --pick-t로 맞춘다
- 바닥 동작 등 선생님이 옆으로 넓으면 `--shape auto`가 4:5 넓은 창 + 흐린 배경으로 바꿈 (`--shape tall|wide`로 고정 가능)
- AV1 등 OpenCV가 못 읽는 코덱도 처리 (먼저 구간을 H.264로 자름)

## 드라이브 폴더에서 영상 목록 읽기 (공개 링크 폴더)
    curl -sL "https://drive.google.com/embeddedfolderview?id=<폴더ID>#list"  → file/d/<ID> 와 파일 이름
    curl -sL -o 영상.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"
- 원장님 수업영상 폴더 ID: 1u0hgxcHkLTTOnXkaoQn0DSfaay1EcHXa ("링크가 있는 모든 사용자" 공유, 2026-11-04)

## 원장님 스타일 제목만 얹기 (TRACKPAD mogrt 느낌, 2026-11-05)
    node tools/class-reel/add_title.js --video 세로.mp4 --title "KIDZ K-POP" --name MINKYUNG [--track "곡"] --out 결과.mp4
- 첫 0.3~3초: 큰 수업명(기울인 굵은 글씨) + 아래 강사 이름(글자 간격이 벌어지며 등장) → 사라짐. 나머지 영상은 그대로
- 원장님 mogrt(TRACKPAD): After Effects 템플릿, 2줄(Line1 Arvo-Bold 120 / Line2 Montserrat-Regular 33, 자간 25), 1920x1080, 5초
- 곡명은 기본으로 넣지 않음 (--track 쓰면 맨 위 작은 줄)
