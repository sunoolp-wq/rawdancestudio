# 매일 스토리 "TODAY'S CLASS INFO" 영상 만들기

    node tools/daily-story/render.js 2026-11-05        # 15초, 1080x1920
    → content/2026-11-05_daily-story/story.mp4

- 요일 시간표: `schedule-2026-11.json` (월이 바뀌면 `schedule-YYYY-MM.json` 새로 추가)
- 그날만 바뀌는 것(대강·팝업·휴강·추가): `extra.json`에 날짜별로 적는다
  - `replace`: 시작 시간·수업명이 같은 수업의 강사·표시 바꾸기 (`"mark": "popup"` → POP-UP 표시)
  - `remove`: 휴강
  - `add`: 그날만 추가 ({start, end, name, teacher, hall, mark, key})
- 소리 없음(무음 트랙). 음악은 인스타 스토리에서 붙인다.
