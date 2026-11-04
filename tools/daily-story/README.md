# 매일 스토리 "TODAY'S CLASS INFO" 영상 만들기

    node tools/daily-story/render.js 2026-11-05        # 15초, 1080x1920
    → content/2026-11-05_daily-story/story.mp4

- 요일 시간표: `schedule-2026-11.json` (월이 바뀌면 `schedule-YYYY-MM.json` 새로 추가)
- 그날만 바뀌는 것(대강·팝업·휴강·추가): `extra.json`에 날짜별로 적는다
  - `replace`: 시작 시간·수업명이 같은 수업의 강사·표시 바꾸기 (`"mark": "popup"` → POP-UP 표시)
  - `remove`: 휴강
  - `add`: 그날만 추가 ({start, end, name, teacher, hall, mark, key})
- 음악: `music/` 폴더에 파일을 넣고 `music.json`에 지정 → 자동으로 입힘 (앞 0.4초 페이드인, 끝 1.2초 페이드아웃)
  - `{"default": {"file": "music/track.mp3", "start": 32, "volume": 0.9}}` / 날짜별로 다르게: `{"2026-11-05": {...}}`
  - 지정이 없으면 무음 (인스타 스토리에서 음악 스티커로 붙인다)
  - 상업 음원을 영상에 직접 넣으면 인스타에서 음소거·차단될 수 있다. 저작권 없는 음원이나 사용 허락받은 음원만 넣는다.
- 토요일 영상은 만들지 않는다 (원장님 지시 2026-11-04). 자동 생성: 매주 일요일 19:52 다음 주 월~금
