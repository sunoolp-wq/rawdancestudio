# 영상 공구함 (video-kit) — 영상편집팀 에이전트용

원장님 2026-11-25 "영상 편집에 필요한 에이전트 구축" → 그동안 반복된 문제(중복 영상, 박자 안 맞음, 글자 잘림·붙음, 수정마다 10분 렌더)를 도구로 막는다.

| 도구 | 하는 일 | 쓰는 에이전트 |
|---|---|---|
| `scout.py sheet` | 원본 영상 장면 미리보기(시각 표시) + 어두움·흐림·멈춤 구간 | footage-scout |
| `scout.py used` | 프로젝트별 '쓴 구간' 기록(`content/<폴더>/used-footage.json`) → 중복 방지 | footage-scout |
| `beats.py` | 음원에서 실제 쾅 시각·세기·구간 바뀜 측정 (BPM 격자 아님) | beat-sync |
| `qa_html.js` | HTML 화면을 여러 시각에 그려 글자 잘림·겹침·붙음·인스타 가림 영역 검사 | render-qa |
| `qa_video.py` | 완성 mp4의 중복 장면·검은 화면·무음·번쩍 튐 검사 + 0.5초 미리보기 | render-qa |

## 빠른 미리보기 (렌더 시간 줄이기)
`tools/pw.js`의 `renderFrames`는 환경 변수 `RAW_PREVIEW=1`이면 절반 크기(540×960)로 그린다 → 22초 예고편 약 10분 → 약 3분.
    RAW_PREVIEW=1 NODE_PATH=$(npm root -g) node content/2026-11-25_kidz-pro-teaser/make_trailer.js C 음원.wav   # → *_preview.mp4
원장님께 먼저 미리보기를 보내 OK를 받은 뒤 고화질로 만든다 (고칠 게 많을 때).

## 작업 순서 (메인 세션 = 총괄 PD)
1. 음악이 정해지면 → `beat-sync` (타이밍표)
2. 원본 영상이 오면 → `footage-scout` (구간 고르기, 쓴 구간 기록)
3. 메인 세션이 HTML·스크립트로 제작 → `render-qa`로 HTML 먼저 검사(렌더 전, 몇 초 걸림)
4. 미리보기 렌더(RAW_PREVIEW=1) → 원장님 확인 → 고화질 렌더
5. 완성 mp4 → `render-qa` (qa_video.py) → 문구는 `compliance-checker` → 원장님께 전송
영상·음원 파일은 커밋하지 않는다 (`.gitignore`). 검수 결과(json·jpg)는 프로젝트 폴더 `qa/`에 두되 커밋하지 않아도 된다.

## 필요한 것
python3 + numpy + Pillow, ffmpeg/ffprobe, node + playwright (클라우드 기본 설치). OpenCV 필요 없음.
