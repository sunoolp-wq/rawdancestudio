# 로우댄스학원 수원점 마케팅 에이전트 팀

RAW DANCE STUDIO SUWON의 마케팅을 **6개 부서, 14명의 AI 에이전트**로 나눠 기획부터 실행까지 운영하는 작업 공간입니다.
Claude Code에서 이 폴더를 열면 에이전트(`.claude/agents/`)와 워크플로(`.claude/skills/`)가 자동으로 불러와집니다.

## 조직도
```
                         총괄 PD (메인 Claude 세션)
                                  │
 ┌──────────────┬───────────────┼──────────────────┬───────────────┬──────────────┐
 전략기획실      콘텐츠제작팀      채널캡션팀            고객경험팀        품질관리실       성과분석실
 ├ trend-        ├ shortform-     ├ caption-naver-clip  ├ review-manager  └ compliance-   └ performance-
 │ researcher    │ planner        ├ caption-smartplace  └ inquiry-          checker         analyst
 └ campaign-     └ shoot-         ├ caption-instagram     concierge
   strategist      director       ├ caption-tiktok
                                  ├ caption-daangn
                                  └ caption-youtube
```

| 부서 | 왜 필요한가 |
|---|---|
| 전략기획실 | 입시·오디션 일정과 방학 시즌이 매출을 좌우하는 업종이라, 시즌 캘린더와 트렌드를 먼저 잡아야 함 |
| 콘텐츠제작팀 | 원장님·강사님이 스마트폰으로 15분 안에 찍을 수 있게 훅·대본·샷리스트를 미리 준비 |
| 채널캡션팀 | 같은 영상이라도 10대 채널(틱톡·인스타·쇼츠)과 학부모 채널(네이버·당근)은 말투와 정보가 달라야 함 |
| 고객경험팀 | 리뷰와 DM 응답 속도가 곧 등록 전환. 스마트플레이스 리뷰 답글도 노출 관리의 일부 |
| 품질관리실 | 학원 광고는 교습비 표시 의무, 과장 광고 제재, 미성년 초상권 이슈가 있음 |
| 성과분석실 | "조회수"가 아니라 **문의 → 체험 → 등록** 숫자로 다음 주 전략을 수정 |

## 매일·매주 쓰는 법
| 상황 | 이렇게 말하세요 | 실행되는 것 |
|---|---|---|
| 오늘 찍은 영상 올릴 때 | `/one-source 입시반 화요일 수업, ○○ 안무 4인 단체, 얼굴 동의 받음` | 6개 채널 캡션 동시 작성 → 검수 |
| 주말에 다음 주 준비 | `/weekly-content 다음 주 목표: 토요일 K-POP반 신규 문의 10건` | 리서치 → 캘린더 → 숏폼 기획 → 촬영 가이드 → 캡션 → 검수 |
| 주간 성과 정리 | `/weekly-report` + 지표 붙여넣기 | 퍼널 리포트 + 다음 주 실험 |
| 리뷰·DM 왔을 때 | `/review-reply` + 내용 붙여넣기 | 답글/답변 A·B안 |
| 특정 부서만 | "trend-researcher로 이번 주 챌린지 찾아줘" | 해당 에이전트만 호출 |

## 처음 시작할 때 (중요)
1. `brand/brand-guide.md`에 학원 정보·교습비·시간표·강사가 정리되어 있습니다 (2026-10-08 반영). 남은 `[확인필요]` 칸(토요일 시간, 체험수업, 강사 경력, 합격 실적 등)을 채울수록 결과물이 정확해집니다. 비어 있으면 지어내지 않고 `[확인필요]`로 남깁니다.
2. 수강생(특히 미성년) 사진·영상 사용 **보호자 동의서**를 받아 두세요 (용도·채널·기간 명시).
3. 스마트플레이스 정보 점검부터: "caption-smartplace로 플레이스 점검 체크리스트 줘".

## 폴더 구조
```
CLAUDE.md                  공통 규칙 + 조직도 (모든 에이전트가 따름)
brand/brand-guide.md       학원 정보·타깃·톤·금지 표현·시즌 캘린더
docs/platform-playbook.md  채널별 역할·포맷·노출 요령
docs/research.md           리서치 요약과 출처
.claude/agents/            14개 에이전트 정의
.claude/skills/            4개 워크플로 (one-source, weekly-content, weekly-report, review-reply)
content/                   산출물 (research/, plans/, reports/, 날짜_주제/)
```
