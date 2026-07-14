# SW·AI 교육 동향 아카이브 — 개발 스펙 (Claude Code 핸드오프용)

## 1. 목적
12개 국내 교육 관련 기관/사이트에서 SW·AI 교육 관련 보고서·리포트를 수합해 제목 기준으로 아카이빙하고,
요약·키워드로 검색할 수 있게 하는 정적 사이트. GitHub Pages로 배포.

## 2. 수집 대상 12곳 (기관 코드 기준)

| code | 기관/코너명 | 원본 목록 URL |
|---|---|---|
| kice-research | 교육과정평가원 연구보고서 | https://www.kice.re.kr/resrchBoard/list.do?cate=0&m=030109&s=kice |
| kice-trend | 교육과정평가원 국제교육동향 | https://www.kice.re.kr/boardCnts/list.do?boardID=5000064&m=030207&s=kice |
| kice-cardnews | 교육과정평가원 카드뉴스 | https://www.kice.re.kr/cardNewsBoard/list.do?boardId=1&s=kice&m=030216 |
| kedi-research | 교육개발원 연구보고서 | https://www.kedi.re.kr/khome/main/research/listPubForm.do |
| kedi-brief | 교육개발원 브리프 | https://www.kedi.re.kr/khome/main/research/kediBrief.do |
| edpolicy-domestic | 교육정책네트워크 국가별 교육동향 | https://edpolicy.kedi.re.kr/edpolicy/board/30 |
| edpolicy-intl | 교육정책네트워크 국제기구 교육동향 | https://edpolicy.kedi.re.kr/edpolicy/board/31 |
| spri | 소프트웨어정책연구소 | https://www.spri.kr/posts?data_page=1&code=data_all&study_type=&board_type=research |
| kosac-research | 한국과학창의재단 연구보고서 | https://www.kosac.re.kr/menus/244/boards/457/posts |
| kosac-trend | 한국과학창의재단 동향리포트 | https://www.kosac.re.kr/menus/248/boards/459/posts |
| keris-research | 한국교육학술정보원 연구보고서 | https://keris.or.kr/main/ad/pblcte/selectPblcteRRList.do?mi=1138 |
| keris-issue | 한국교육학술정보원 이슈리포트 | https://keris.or.kr/main/ad/pblcte/selectPblcteRMList.do?mi=1139 |

이 표는 `data/institutions.json`으로 코드화한다:
```json
{
  "code": "keris-research",
  "name": "한국교육학술정보원 연구보고서",
  "list_url": "https://keris.or.kr/main/ad/pblcte/selectPblcteRRList.do?mi=1138"
}
```

## 3. 데이터 파이프라인
- 수집/요약은 **Claude Code가 사용자 요청 시 수행**한다 (자동 크롤러 없음). 사용자가 "N번 기관 수합해줘"라고 요청하면, Claude Code가 원본 사이트를 읽고 보고서별 마크다운 파일을 생성/갱신한다.
- 보고서 원본 파일: `src/reports/<institution-code>/<slug>.md`
- 빌드 스크립트가 모든 마크다운의 frontmatter를 모아 `public/data/reports-index.json` 하나로 합친다. 사이트(메인/검색/상세)는 이 인덱스 JSON + 개별 md 렌더 결과만 읽는다. 즉 **런타임에 외부 사이트를 호출하지 않는다** (정적 사이트 원칙 준수).

### 3.1 보고서 스키마 (`src/reports/<code>/<slug>.md`)
```markdown
---
institution: keris-research      # institutions.json의 code와 정확히 일치
title: "생성형 AI 활용 교육 지원 방안 연구"
lead_researcher: 홍길동
date: 2025-11-20                  # 게시 연도 기준 yyyy-mm-dd
source_url: https://...           # 원문 상세 페이지 (고유 키, 필수)
pdf_url: https://...              # 원본 PDF 직링크 (선택)
keywords: [생성형AI, 초중등, 교수학습]
abstract_source: pdf_analyzed     # pdf_analyzed | excerpt | manual | unavailable (아래 참고)
table_of_contents: |              # 선택. 보고서 목차 (마크다운 리스트)
  - 1. 서론
  - 2. 선행 연구 검토
  - 3. 연구 방법
---

(본문: 요약문 3~5문단 + 필요 시 분석 코멘트)
```

`abstract_source` 값 정의 (제안값 — 확정 필요 시 조정):
- `pdf_analyzed`: PDF 원문을 분석해 Claude가 요약 작성
- `excerpt`: 원문 페이지의 요약/초록을 그대로 발췌
- `manual`: 담당자가 직접 작성
- `unavailable`: 요약 없음 (제목·메타데이터만)

### 3.2 인덱스 산출물 (`public/data/reports-index.json`)
빌드 시 모든 md의 frontmatter + 본문 요약 텍스트를 배열로 직렬화. 각 항목:
```json
{
  "institution": "keris-research",
  "slug": "generative-ai-2025",
  "title": "생성형 AI 활용 교육 지원 방안 연구",
  "date": "2025-11-20",
  "keywords": ["생성형AI", "초중등", "교수학습"],
  "abstract_excerpt": "이 연구는 ...",   // 검색용 요약 발췌 (앞 150자 등)
  "detail_path": "reports/keris-research/generative-ai-2025.html"
}
```
메인 페이지, 검색 모두 이 파일 하나만 fetch해서 클라이언트에서 필터링한다 (건수가 많지 않으므로 서버 검색 불필요).

## 4. 사이트 구조
```
/index.html                       메인 아카이브 (2열 6행)
/reports/<code>/<slug>.html       보고서 상세 페이지 (빌드 스크립트가 md → html 생성)
/data/institutions.json
/public/data/reports-index.json
/scripts/build.js                 md → 상세 html + reports-index.json 생성
```
GitHub Pages 배포: `main` 브랜치의 `/docs` 폴더 또는 GitHub Actions로 `gh-pages` 브랜치에 퍼블리시.

## 5. 메인 페이지 (`index.html`)
- **레이아웃**: 2열 × 6행 그리드, 셀 1개 = 기관 1곳 (12개 기관 = 12개 셀, 1:1 매칭).
- **셀 구성**: 상단에 기관명(작게), 그 아래 최신 보고서 제목 최대 5개 (제목 + 날짜). 제목 클릭 → 해당 보고서 상세 페이지로 이동.
- **더보기**: 6개 이상 보고서가 있을 경우 셀 하단에 "더보기" 노출. 클릭 시 **해당 기관의 원본 목록 페이지(외부 URL, institutions.json의 list_url)로 새 탭 이동** — 사이트 내 전체 목록 페이지는 만들지 않음.
- **검색**: 우측 상단 검색창(상시 노출). 입력 시 제목+요약+키워드를 대상으로 클라이언트 사이드 필터링.
  - 검색 결과는 그리드를 대체해 리스트로 표시.
  - 각 결과 행 형식: **기관명 · 제목(링크)**. 제목 클릭 시 상세 페이지 이동.
  - 검색어 비우면 원래 그리드로 복귀.

## 6. 보고서 상세 페이지 (`reports/<code>/<slug>.html`)
표시 항목 (스키마 필드와 1:1 매핑):
- 기관명, 제목, 연구책임자, 게시일
- 키워드 태그
- 목차 (있으면)
- 요약/분석 본문
- 원문 링크(source_url), PDF 링크(있으면 pdf_url)

## 7. 디자인 방향
- 톤: 테크/AI 스타트업 스타일 — 모던, 대비감 있는 레이아웃.
- 컬러: 그레이스케일(거의 흑백에 가까운 뉴트럴) + 포인트 컬러 1개(인디고/블루 계열).
- 타이포: 한글 산세리프 1종 (예: Pretendard / Noto Sans KR), 코드/메타데이터용 모노스페이스 보조.
- 언어: 한국어 단일.

## 8. 첨부물
- `SWAI 아카이브 예시.dc.html` — 메인 페이지(2×6 그리드 + 검색) 및 상세 페이지 예시가 담긴 단일 HTML 목업. 실제 개발 시 레이아웃/톤 참고용이며, 데이터는 더미.

## 9. 미확정/확인 필요 항목
- `abstract_source`의 4개 값 정식 명칭 (위는 제안값)
- 보고서 갱신 주기 및 "최신 5개"의 정렬 기준(게시일 desc 가정)
- 상세 페이지를 빌드 시 정적 HTML로 생성할지, 클라이언트 라우팅(SPA)으로 처리할지
