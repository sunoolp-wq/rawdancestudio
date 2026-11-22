# 인스타 스토리 예약 (원장님 맥 · Claude Code + Ego Lite)

> 원장님 2026-11-22: "스토리 만들면 이고 브라우저가 예약까지 자동으로" / 시간 = **그 날짜 오전 12:00(00:00)에 시간표 스토리, 이어서 00:01·00:02·00:03… 그날 장르 수업 순서대로 수업 영상** ("장르 수업만 스토리 예약하면 돼" — K-POP 수업은 예약 안 함)
> 이 문서는 **원장님 맥의 Claude Code**가 따라 한다 (클라우드 세션은 맥 브라우저를 못 씀). 원장님은 RAW 영상공장 폴더에서 `claude`를 열고 "docs/story-schedule.md 대로 다음 주 스토리 예약해줘"라고만 하면 된다.

## ★ 자동 예약 (2026-11-23~) — 먼저 이걸 쓴다
원장님 2026-11-23: "매일 자동 예약으로" → 아래 3가지가 이 문서의 1~3번을 대신한다. **Claude는 스크립트를 실행만 하고, 화면을 하나씩 누르지 않는다** (토큰 절약).
- **자동:** 맥 launchd(`~/Library/LaunchAgents/com.rawdance.story-schedule.plist`, 저장소에는 없음)가 **일·월·화·수·목 밤 21:00**에 `node tools/daily-story/schedule_stories.js --tomorrow --yes` 실행 → 다음 날(월~금) 스토리 예약. 금요일 밤(=토요일 것)은 쉼. 자동 실행은 확인 없이 예약해도 된다고 원장님이 허락함
- **손으로:** `4_스토리예약.command` 더블클릭 → 날짜(엔터 = 내일) → 표 → `y`. Claude가 할 때는 `node tools/daily-story/schedule_stories.js YYYY-MM-DD` (표만 보고 싶으면 입력 없이 실행하면 예약 안 함)
- 스크립트가 하는 일: 최신 받기(3_업데이트 방식, 이 맥에 안 올린 커밋·고친 파일이 있으면 건너뜀) → 시간표 영상(`~/Movies/RAW 영상공장/**/MMDD_시간표.mp4`가 있으면 그것, 없으면 render.js — 음원 파일 없으면 무음) → plan.js → 수업 영상(날짜 파일 → 그 쌤 최근 15초 → 없으면 건너뜀) → Ego Lite 예약(누르기 전 날짜·시각·업로드 확인, 다르면 멈춤)
- 두 번 예약 방지: `~/Library/Application Support/raw-story/<날짜>.json`에 예약한 칸 기록 (다시 하려면 `--force`). 점검만: `--check`
- 결과: macOS 알림("MM/DD 예약 N개 완료" / "스토리 예약 확인 필요"), 로그 `~/Library/Logs/raw-story.log`, 실패 화면 `~/Library/Application Support/raw-story/fail-<날짜>.png`
- 조건: 21:00에 맥이 켜져 있고(잠자기면 깨어날 때 실행, 자정 넘으면 건너뛰고 알림) Ego Lite가 Meta 비즈니스 스위트에 로그인돼 있어야 함

## 0. 준비 (매번 · 손으로 할 때)
1. 최신으로 받기: 원장님 맥은 `3_업데이트.command`와 같은 방식(얕게 받기 + content 제외)이라 `git pull` 대신 `git fetch --depth 1 origin claude/low-dance-marketing-agents-lisndi && git reset --hard FETCH_HEAD` (단, `tools/daily-story/extra.json`은 받기 전에 복사해 두고 받은 뒤 합친다 — 3_업데이트와 같음). 가장 쉬운 방법: 원장님께 `3_업데이트.command`를 먼저 더블클릭해 달라고 한다
   - content 폴더는 맥에 받지 않는다(용량, 2026-11-23). 스토리 영상은 render.js가 content 안에 새로 만든다
2. 예약할 날짜 = 다음 주 월~금 (원장님이 날짜를 말하면 그 날짜). 토요일은 하지 않는다.
3. 음원: `tools/daily-story/music.json`에 그 날짜가 있으면 `tools/daily-story/music/` 안에 그 mp3가 있어야 한다. 없으면 멈추고 원장님께 파일을 달라고 한다 (음원은 저장소에 없음).

## 1. 만들기
- 날짜마다 `node tools/daily-story/render.js YYYY-MM-DD` → `content/YYYY-MM-DD_daily-story/story.mp4`
- 날짜마다 `node tools/daily-story/plan.js YYYY-MM-DD` → 그날 예약 순서 (00:00 시간표, 00:01부터 수업 순서대로 쌤)

## 2. 장르 수업 영상 찾기
- **오디션반(수 19:30, YUNI)은 장르 수업처럼 예약한다** (원장님 2026-11-23 "오디션 넣어도 될 듯"). 영상 파일 이름은 `MMDD_쌤15초_YUNI_AUDITION.mp4`
- **K-POP 수업(유아·키즈·취미·성인 K-POP)은 예약하지 않는다.** `plan.js`가 이미 빼고, 장르 수업만 00:01부터 빈칸 없이 차례로 번호를 매긴다.
- **날짜가 붙은 파일이 1순위:** 파일 이름이 `MMDD_쌤15초_<쌤>_<장르>.mp4`(예: `1126_쌤15초_NOFF_HIP HOP.mp4`)이면 그 날짜 그 수업에 그대로 쓴다. 클라우드 Claude가 만들어 원장님이 `~/Movies/RAW 영상공장/` 아무 폴더에 넣어 둔 파일 (2026-11-23~)
- 날짜 파일이 없으면: 장르 수업(CHOREO, BASIC, GIRLISH, JAZZ, WAACKING, HIP HOP, 힐코레오, 팝업 등)마다 RAW 영상공장 결과 폴더 `~/Movies/RAW 영상공장/` (날짜별 폴더)에서 파일 이름에 **그 쌤 이름**이 들어간 15초 영상(`*_TRACKPAD_<쌤>_*.mp4` 또는 `*_쌤15초_<쌤>_*.mp4`) 중 장르가 맞는 **가장 최근** 파일을 쓴다.
- 영상이 없는 수업은 **건너뛰고** 표에 "영상 없음"으로 표시한다 (뒤 수업 시각은 그대로).
- 찾은 결과를 표로 보여 준다: `예약 시각 | 수업 | 쌤 | 파일`

## 3. 예약 (Ego Lite)
`/ego-browser`로 Meta 비즈니스 스위트에서 한 개씩:
1. https://business.facebook.com → 왼쪽 **플래너**(또는 콘텐츠) → **만들기 → 스토리**
2. 게시 위치는 **인스타그램 @rawdance_suwon만** (페이스북은 체크 해제)
3. 파일 업로드 → **예약** → 날짜·시간 입력 (00:00, 00:01, 00:02 …) → 예약 확정
4. 다음 영상 반복

## 4. 지킬 것
- **예약 버튼을 누르기 전에** 2번 표 전체를 원장님께 보여 주고 "ok"를 받은 뒤 예약한다. (원장님이 "확인 없이 해도 돼"라고 하기 전까지 매번)
- 예약 말고는 아무것도 누르지 않는다: 바로 게시, DM, 댓글, 광고, 설정 변경 금지.
- 업로드 실패·화면이 다르게 생김·로그인 풀림 → 그 자리에서 멈추고 화면을 보여 준다. 추측해서 다른 버튼을 누르지 않는다.
- 끝나면 비즈니스 스위트 **예약 목록 화면**을 보여 주고, 예약된 개수를 날짜별로 알려 준다.
