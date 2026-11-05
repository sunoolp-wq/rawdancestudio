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
    node tools/class-reel/add_title.js --video 세로.mp4 --title "KIDZ K-POP" --name MINKYUNG [--track "곡"] [--trkdy 29] --out 결과.mp4
- 원장님 자막 순서: 1줄 곡명(작게) / 2줄 강사(크게) / 3줄 장르  예) Dip - Jalen Santoy / NOFF / HIPHOP. 곡명 줄 높이는 원본마다 조금 다름(--trkdy, NOFF 원본은 29)
- 5초 (원장님 TRACKPAD 원본 분석, 2026-11-05): 글자마다 무작위 순서로 탁탁 켜짐(일부 회색으로 한 번 깜빡) → 자간이 쫀쫀하게 모였다가 천천히 벌어짐 → 4.3초부터 무작위로 사라락 꺼짐. 나머지 영상은 그대로
- 원장님 mogrt(TRACKPAD): After Effects 템플릿, 2줄(Line1 Arvo-Bold 120 / Line2 Montserrat-Regular 33, 자간 25), 1920x1080, 5초
- 곡명은 기본으로 넣지 않음 (--track 쓰면 맨 위 작은 줄)

### TRACKPAD 원본 분석 메모 (2026-11-05, 아직 원본만큼 안 됨 → 연구 중)
- mogrt 안 AE 프로젝트(Title_Templates v3.aep)에서 확인: 텍스트 애니메이터 4개 + Range Selector, **Randomize Order**(글자 순서 무작위), **Opacity**, **Tracking Amount**(자간), **Text Position 3D**(글자마다 위치 이동), Selector Smoothness
- 즉 원본은 글자마다 무작위 순서로 켜지는 것 + 자간 애니메이션 + **글자별 위치 이동**이 겹친 것. 지금 버전엔 위치 이동이 없음
- 원장님 실제 사용 글꼴: **GoGo Poster 2020** (Line1). 파일이 있어야 똑같이 나옴
- 2026-11-05 2차: 원장님 검은 바탕 5초 원본(24fps)을 프레임별로 재서 맞춤 — 큰 줄 0.04~0.42초 무작위 켜짐(직전 1프레임 엉뚱한 회색 글자), 자간: 켜지는 동안 0.25~0.50초 천천히 벌어짐(+0.028em) → 0.56초에 1프레임 만에 싹 모임(살짝 더 좁게) → 2프레임 동안 자리 잡음 (프레임별 폭 원본과 ±3px), 이름·곡명 0.55~0.585초 한 번에 켜짐(자간 고정), 퇴장: 이름·곡명 4.55~4.72초 → 큰 줄 4.59~4.96초, 무작위 순서로 거의 1프레임에 1글자씩 고르게(뭉쳐 꺼지면 렉 걸린 느낌), 대시가 마지막, 회색 깜빡은 드물게. 글꼴 GoGo Poster 2020(Italic 큰 줄/Regular 이름), 곡명 Montserrat 500. 크기·위치 원본과 ±1% (`TRACKPAD_compare.mp4` 왼쪽 원본/오른쪽 재현)
- GoGo Poster 2020 글꼴은 원장님 제공 파일 → 각 작업 환경 ~/.local/share/fonts 에 설치 필요 (저장소에 올리지 않음, 원장님 판단)

## 색감 보정 LUT (2026-11-05, 원장님 피드백 반영 2차)
    python3 tools/class-reel/make_lut.py tools/class-reel/luts/RAW_studio.cube      # 값 바꿀 때만
    ffmpeg -i 세로.mp4 -vf "lut3d=tools/class-reel/luts/RAW_studio.cube:interp=tetrahedral,setsar=1" -c:a copy 결과.mp4
- 1차(원장님 보정본을 그대로 학습한 LUT)는 버림: 보라 조명 영상으로만 배워서 빨간 조명·신발이 하늘색이 됨
- 2차 RAW_studio.cube 원칙: 색상(빨강·보라·파랑)은 그대로 / 뿌연 검정 걷기(블랙 0.04→0, 화이트 0.80까지 늘림, 부드러운 S커브) / 채도 1.25 / 피부톤 살리기(보라·분홍으로 찍힌 피부만 살구색 쪽으로 조금, 살짝 밝게)
- 같은 .cube를 프리미어 Lumetri → Creative → Look 에 넣어도 같은 색
- 순서: follow_yolo(트래킹) → lut3d(보정) → add_title(자막)
