# 로우댄스학원 수원점 (RAW DANCE STUDIO SUWON) 마케팅 본부

이 저장소는 로우댄스학원 수원점의 마케팅 업무를 **부서별 AI 에이전트 팀**으로 나눠 운영하기 위한 작업 공간이다.
모든 에이전트와 메인 세션은 아래 공통 규칙을 따른다.

## 먼저 읽을 문서
- `brand/brand-guide.md`: 학원 정보, 타깃, 톤앤매너, 금지 표현. **모든 콘텐츠의 기준.**
- `docs/platform-playbook.md`: 채널별 역할, 포맷, 노출 요령.
- `docs/research.md`: 리서치 요약과 출처.
- `brand/blog-template.md`: 네이버 블로그 고정 양식.
- `brand/timetable-a-hall-2026-10.png`: A홀 주간 시간표 원본.

## 조직도 (에이전트 = `.claude/agents/*.md`)
| 부서 | 에이전트 | 하는 일 |
|---|---|---|
| 전략기획실 | `trend-researcher` | 트렌드 음원·챌린지, 경쟁 학원, 입시/오디션 일정, 검색 키워드 조사 |
| 전략기획실 | `campaign-strategist` | 월간·주간 콘텐츠 캘린더, 모집 캠페인(K-POP반·전문반·오디션반·토요일반) 기획 |
| 콘텐츠제작팀 | `shortform-planner` | 숏폼 훅·대본·콘티, 1소스 멀티유즈 설계 |
| 콘텐츠제작팀 | `shoot-director` | 촬영 샷리스트, 편집 포인트, 화면 자막 설계 (강사·원장용 현장 가이드) |
| 채널캡션팀 | `caption-naver-clip` | 네이버 클립 제목·본문·해시태그 |
| 채널캡션팀 | `caption-naver-blog` | 네이버 블로그 글 (고정 양식 `brand/blog-template.md`) |
| 채널캡션팀 | `caption-smartplace` | 스마트플레이스 소식·쿠폰·이벤트 문구 |
| 채널캡션팀 | `caption-instagram` | 인스타 릴스·피드·스토리 캡션 |
| 채널캡션팀 | `caption-tiktok` | 틱톡 캡션·검색형 자막 |
| 채널캡션팀 | `caption-daangn` | 당근 비즈프로필 소식·스토리 문구 |
| 채널캡션팀 | `caption-youtube` | 유튜브 쇼츠/롱폼 제목·설명·고정댓글 |
| 고객경험팀 | `review-manager` | 리뷰·댓글 답글, 리뷰 요청 문구 |
| 고객경험팀 | `inquiry-concierge` | DM·카톡·당근 채팅 상담 스크립트, 체험→등록 전환 |
| 품질관리실 | `compliance-checker` | 학원법·표시광고·초상권·음원 저작권·브랜드 톤 최종 검수 |
| 성과분석실 | `performance-analyst` | 채널별 지표 리포트, 다음 주 개선안 |

서브에이전트는 다른 서브에이전트를 부를 수 없다. **여러 부서를 거치는 업무는 메인 세션(총괄 PD 역할)이** `.claude/skills/`의 워크플로를 따라 순서대로 호출한다.

## 공통 규칙
1. **사실만 쓴다.** 수강료, 시간표, 합격 실적, 강사 경력 등은 `brand/brand-guide.md`에 있는 내용만 사용한다. 비어 있으면 `[확인필요: ...]`로 남기고 지어내지 않는다.
2. **과장 금지.** "100% 합격", "무조건 데뷔", "수원 1등" 같은 보장·최상급 표현은 쓰지 않는다 (상세 목록은 브랜드 가이드).
3. **미성년자 보호.** 수강생 실명, 학교명, 얼굴이 나오는 콘텐츠는 보호자 동의 여부를 확인하라고 표시한다.
4. **음원.** 상업 음원은 각 플랫폼 내 제공 음원 사용을 기본으로 안내한다.
5. **결과물 저장.** 산출물은 `content/YYYY-MM-DD_<주제>/` 폴더에 채널별 파일(`naver-blog.md`, `naver-clip.md`, `smartplace.md`, `instagram.md`, `tiktok.md`, `daangn.md`, `youtube.md`)로 저장한다. 리포트는 `content/reports/`에 저장한다.
6. **발행 전 검수.** 외부에 게시될 문구는 반드시 `compliance-checker`를 거친다.
7. 모든 결과물은 한국어로, 바로 복사해 붙여넣을 수 있는 형태로 쓴다.
