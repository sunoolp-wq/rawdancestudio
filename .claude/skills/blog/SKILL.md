---
name: blog
description: 블로그팀 워크플로. 네이버 블로그 글 1편을 키워드 브리프 → 본문 → 사진 가이드 → 검색 최적화 편집 → 검수까지 만들거나, 한 달 블로그 발행 계획을 짠다. "블로그 써줘", "블로그 글 하나", "이번 달 블로그 계획", "/blog" 요청에 사용.
---

# 블로그팀 워크플로

메인 세션이 총괄 PD로서 블로그팀(`blog-strategist` → `caption-naver-blog` → `blog-photo-director` → `blog-seo-editor`)과 `compliance-checker`를 순서대로 호출한다.

## 모드 1. 글 1편
1. **입력 확인** (모자라면 한 번에 묻기): 주제 또는 소재(수업 영상/공지/정보 글), 사진·영상 보유 여부, 학생 이름(A형).
2. **브리프:** `blog-strategist` → 메인 키워드·제목 후보·글 종류·겹침 확인. 저장 경로 `content/YYYY-MM-DD_<주제>/`를 정해 함께 넘긴다.
3. **본문 + 사진 (동시 호출):**
   - `caption-naver-blog` → `naver-blog.md` (브리프 전달)
   - `blog-photo-director` → `blog-photos.md` (브리프 전달, 본문 완성 전이라도 장면 기준으로 작성)
4. **편집:** `blog-seo-editor` → `naver-blog.md` 직접 수정 (사진 위치를 `blog-photos.md`와 맞춤).
5. **검수:** `compliance-checker` → 폴더 전체.
6. **전달:** 제목 1개 추천 + 바로 붙여넣을 본문 + 사진 순서표 + `[확인필요]` 모음. 발행하면 URL을 알려 달라고 요청 → `blog-strategist`가 `docs/blog-log.md`에 기록.

## 모드 2. 월간 계획
1. `blog-strategist` → `content/blog-plan/YYYY-MM.md` (주 2편: C형 1 + A/B형 1, 글마다 키워드·제목·필요 사진).
2. 필요한 촬영 컷만 모아 `blog-photo-director`에게 "이번 달 몰아 찍기 목록" 요청 → 같은 파일 아래에 추가.
3. 원장님께 표로 요약 전달. 확정되면 모드 1로 한 편씩 진행.

## 다른 워크플로와의 관계
- `/one-source`에서 블로그가 포함되면 `caption-naver-blog`만 단독으로 쓴다(빠른 버전). 검색 노출을 노리는 글은 이 `/blog` 워크플로를 쓴다.
