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
- 팝업 강사: `--when "POP-UP" --whenKr "팝업 클래스" --kicker "POP-UP CLASS"` (홀 칩 없음, 날짜는 지어내지 않음)
- 2026-11-06 고침: 전엔 끝 2초 화면이 잘려 15초에서 끝났음 → 지금은 17초(영상 15 + 끝 화면 2). 화질 crf 14
- 시간표 스토리 뒤에 올리는 지난주 선생님 영상 = 이 스타일 (원장님 2026-11-06)
- 이 영상은 **인스타 스토리용 → 캡션 만들지 않음** (원장님 2026-11-11 "캡션은 왜 주냐 이거 스토리용인데"). 영상만 보내기
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
- 작업 환경 'rawdancestudio'는 시작할 때 글꼴과 `.venv`(ultralytics)를 자동 설치함 (2026-11-10). 그 환경이면 설치 없이 `.venv/bin/python` 바로 사용
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
- GoGo Poster 2020 글꼴: 원장님 제공 파일을 `tools/fonts/private/`에 보관 (2026-11-13 원장님 "글꼴 저장해놔"). `bash tools/fonts/install.sh`가 자동 설치

## 색감 보정 LUT (2026-11-05, 원장님 피드백 반영 2차)
    python3 tools/class-reel/make_lut.py tools/class-reel/luts/RAW_studio.cube      # 값 바꿀 때만
    ffmpeg -i 세로.mp4 -vf "lut3d=tools/class-reel/luts/RAW_studio.cube:interp=tetrahedral,setsar=1" -c:a copy 결과.mp4
- 1차(원장님 보정본을 그대로 학습한 LUT)는 버림: 보라 조명 영상으로만 배워서 빨간 조명·신발이 하늘색이 됨
- 3차 RAW_studio.cube (원장님: 뒷벽 얼룩 안 보이게, 사람 너무 빨갛지 않게): 색상 그대로 / 뿌연 검정 걷기 + 부드러운 S커브 / **무채색 어두운 곳(검은 벽·바닥)만 추가로 눌러 얼룩 줄임**(벽 밝기 40→9, 얼룩 차이 절반 이하, 파란 벽·조명·피부는 제외) / 채도 1.12 / 붉게 뜬 피부 채도 살짝 낮춤 / 보라빛 피부는 살구색 쪽으로 약하게
- 1·2차 교훈: 전체 밝기로 누르면 파란 벽·사람까지 꺼짐 → '무채색+어두움' 조건으로만
- 같은 .cube를 프리미어 Lumetri → Creative → Look 에 넣어도 같은 색
- 순서: follow_yolo(트래킹) → lut3d(보정) → add_title(자막)

## 한 번에: 원본 → 노이즈 제거·색 보정·트래킹 → 안무 시작에 맞춰 자막 (2026-11-05)
    .venv/bin/python tools/class-reel/follow_yolo.py --video 원본.MP4 --start 0 --dur <길이> --lut $PWD/tools/class-reel/luts/RAW_studio.cube --out 보정.mp4
    node tools/class-reel/add_title.js --video 보정.mp4 --title NOFF --name HIPHOP --track "Dip - Jalen Santoy" --trkdy 29 --end 8.6 --out 완성.mp4
- `--end` = 안무 시작 시각(초): 자막이 그 순간 사라지도록 약 5초 전부터 시작 (`--at`으로 시작 시각 직접 지정도 가능)
- 안무 시작 찾기: 음악이 잠깐 비는 구간(브레이크) 뒤 첫 박 + 쌤 첫 동작을 같이 확인 (C2208: 7.5~8.5초 음악 빔 → 8.6초 첫 박·첫 스텝)

## 인스타용 수업영상 표준 순서 (2026-11-06, 원장님 확정 방향: 색 보정 없이 넘김 → 원장님이 LUT·음원)
1. 안무 시작·끝 찾기: 쌤 위치·몸 움직임(YOLO) + 프레임 확인. 자막 시작 = 안무 시작 - 4.96초 (영상은 자막 시작부터)
2. `follow_yolo.py --start <자막시작> --dur <안무끝+1-자막시작> --denoise 0 --crf 14` (보정·노이즈 처리 없음)
3. `add_title.js --at 0` (TRACKPAD: 곡명/강사/장르)
4. `finish.sh 입력 <안무끝(새 영상 기준)> 출력 9x16` → 1초 크로스디졸브 → 로고 엔딩 2.5초 (ending-9x16.png: 원장님 제공 로고 raw-logo-full.png, 2026-11-06)
- 원본 소리 유지(디졸브 때 페이드아웃, 엔딩은 무음). 1080x1920, 화면비 1:1, H.264 crf 14
- **2026-11-13 원장님: 로고 엔딩은 원장님이 직접 붙임** → 4번(finish.sh) 생략, 트래킹 + 앞부분 TRACKPAD 자막까지만 넘긴다
- 릴스용(풀 안무)은 캡션 있음(Track 줄 포함), 스토리용 15초 강사 영상은 캡션 없음
