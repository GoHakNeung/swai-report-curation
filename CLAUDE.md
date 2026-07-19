# 프로젝트: SW·AI 연구보고서 큐레이션 사이트

국내 교육·SW 연구기관의 SW·AI 관련 보고서를 수집·요약해 정적 웹사이트로 제공한다.
자동 크롤링은 하지 않는다. 사용자가 필요할 때 Claude Code로 자료를 추가·검토·배포한다.

## 기술 스택
- Eleventy(11ty) 정적 사이트 생성기
- GitHub Pages 배포 (Settings → Pages → Source = GitHub Actions)
- 데이터: 마크다운(front matter) + JSON

## 폴더 구조
```
src/
  _data/
    institutions.json   # 기관 12곳, 그리드 순서
    keywords.json       # 키워드 레지스트리(표기 통일용)
  _includes/            # base / card / report 템플릿
  reports/<code>/       # 보고서 1건 = .md 1개 (<code>는 기관 코드)
  institutions/         # 기관별 '더보기' 전체 목록 페이지
  index.njk             # 첫 페이지(그리드)
_site/                  # 빌드 결과물 (git 제외)
```

## 모델 사용 정책
- 연구보고서 요약(초록) 작성, 키워드 생성/정제: **Opus 4.8**
- 코드 생성(Eleventy 템플릿, 설정, 스크립트 등): **Sonnet 5** (기본)
- 코드 작업 중 오류 발생 시 디버깅: **Opus 4.8**로 전환해 수정
- Claude Code는 세션 중 모델을 자동 전환하지 않으므로, 위 기준에 따라 `/model`로 직접 전환한다.

## 명령어
- `npm run dev` : 로컬 미리보기
- `npm run build` : `_site/`로 빌드
- 배포 : `git add -A && git commit && git push` (Actions가 빌드·배포)

## 기관 분류 및 처리 방식
기관 12곳은 콘텐츠 유형에 따라 다르게 처리된다:

| 유형 | 기관 (order) | 처리 방식 | 요약 구조 | 목차 | 데이터 출처 |
|------|-------------|---------|---------|------|-----------|
| **연구보고서** | 1,2,3,4,5 | .md 파일 생성 | 배경·목적 / 연구방법 / 주요결과 | O | 기관 사이트/PDF |
| **이슈리포트** | 6 | .md 파일 생성 | 배경·목적 / 연구방법 / 주요결과 | O | 기관 사이트/PDF |
| **카드뉴스** | 7 | .md 파일 생성 | 제목만 | - | 기관 링크 |
| **브리프** | 8 | .md 파일 생성 | 제목만 | - | 기관 링크 |
| **동향리포트** | 9 | .md 파일 생성 | 사이트 기반 요약 | - | 해당 기관 사이트 |
| **국제기구동향** | 10 | .md 파일 생성 | 원본 자료 기반 요약 | - | 외부 링크 따라가 원본 분석 |
| **국제교육동향** | 11 | .md 파일 생성 | PDF 기반 요약 | - | PDF 파일 텍스트 추출 |
| **국가별동향** | 12 | .md 파일 생성 | 사이트 기반 요약 | - | 해당 사이트 콘텐츠 |

## 첫 페이지 레이아웃
- 기관 12칸 그리드(2열 × 6행, 모바일 1열). 순서는 institutions.json의 `order`.
- 각 칸: 그 기관의 최신 6건(제목 + 연구책임자, 각각 상세 페이지로 링크), `date` 내림차순.
- 칸 하단: '더보기' → 기관별 전체 목록 페이지.
- `link_only: true`인 기관은 목록 없이 '사이트 바로가기' 버튼만 렌더한다. (예: 카드뉴스)

## 보고서 스키마 (src/reports/<code>/<slug>.md)
```markdown
---
institution: keris-research      # institutions.json의 code와 정확히 일치
title: "생성형 AI 활용 교육 지원 방안 연구"
lead_researcher: 홍길동
lead_affiliation: 진주교육대학교    # 선택. 원문에 명시된 경우만. 없으면 비운다
date: 2025-11-20                  # 게시 연도 기준 yyyy-mm-dd
source_url: https://...          # 원문 상세 페이지 (고유 키, 필수)
pdf_url: https://...             # 원본 PDF 직링크 (선택)
keywords: [생성형AI, 초중등, 교수학습]
abstract_source: pdf_analyzed    # 아래 4값 중 하나
table_of_contents: |             # 선택. 보고서 목차 (마크다운 리스트)
  - 1. 서론
  - 2. 선행 연구 검토
  - 3. 연구 방법
---

## 요약
(본문)
```
- `source_url`은 중복 판별의 고유 키다. 항상 채운다.
- `pdf_url`은 선택. .do 계열 정부 사이트는 직링크가 없을 수 있으므로, 안정적 링크가
  없으면 비우고 `source_url`만 연결한다.
- `table_of_contents`는 선택. 원문에 명확한 목차가 있으면 마크다운 리스트로 옮긴다.
- `link_only` 기관(카드뉴스)에는 보고서 .md를 만들지 않는다.

## 상세페이지 템플릿 가이드

보고서 상세페이지는 기관 유형에 따라 **두 가지 스타일**로 자동 렌더링된다:

### 1. 연구보고서형 (order 1~6)
- **파일 참고**: `보고서 상세_연구보고서형.dc.html`
- **구성 요소**:
  - 기관 정보 헤더: 마크, 기관명, 날짜
  - 제목 (26px, 굵음)
  - 요약 출처 레이블 + 원문/PDF 링크
  - 연구책임자, 공동연구자
  - 키워드 (해시태그 형식)
  - 전체 요약
  - 목차 (토글 가능, 선택)
  - 섹션별 내용:
    * 연구 배경 및 목적
    * 연구 방법
    * 주요 결과

### 2. 동향형 (order 9~12 국제소식)
- **파일 참고**: `보고서 상세_동향형.dc.html`
- **구성 요소**:
  - 기관 정보 헤더: 마크, 기관명, 날짜
  - 제목 (26px, 굵음)
  - 요약 출처 레이블 + 원문 링크
  - 지역/국가/국제기구 태그
  - 요약 본문

**Front Matter 필드 매핑**:
- `co_researchers`: 공동연구자 (연구보고서형만)
- `lead_affiliation`: 연구책임자 소속 (연구보고서형만, 선택)
  - 값이 있으면 `홍길동 (소속)`, 없으면 `홍길동` 으로 렌더된다.
  - **원문/사이트에 소속이 명시된 경우에만 채운다.** 명시되어 있지 않으면 비운다.
    소속이 따로 적히지 않은 연구책임자는 발행 기관 소속일 확률이 높고, 독자도 그렇게
    읽는다. 추측해서 부정확하게 명시하는 것보다 비워 두는 편이 낫다.
  - 외부 소속(예: `임윤진(진주교육대학교)`)처럼 원문이 명시한 경우가 이 필드의 용도다.
- `region`: 지역/국가/국제기구명 (동향형만)

## 마크다운 작성 구조 (보고서 본문)

### 연구보고서 (order 1~5) 및 이슈리포트 (order 6) - 구조화된 본문

**요약 작성의 근거 범위 (매우 중요)**
- 요약·배경·방법·결과는 **사이트에 게시된 내용과 PDF 앞부분을 모두 참고**해 정리한다.
  둘 중 하나만 보고 쓰면 내용이 불안정해진다. 사이트 요약이 짧으면 PDF 앞부분으로
  보완하고, 사이트에 없는 초록은 PDF 앞부분에서 가져온다.
- **PDF는 앞부분만 본다.** 여기서 '앞부분'이란 표지 뒤의 **보고서 초록 / 국문 요약문 /
  연구 개요**와 **목차**가 실린 구간을 말한다(대개 앞 10~20쪽 안). 본문 전체를
  추출·통독하지 않는다. 이 사이트는 '요약 큐레이션'이 목적이고, 전체 추출은 토큰 비용이
  크기 때문이다.
  - 텍스트 PDF: `pdftotext -f 1 -l 16 in.pdf -` 정도로 앞부분만 뽑는다.
  - 스캔 PDF: 앞 14쪽만 OCR한다(위 'OCR 절차' 참고).
- **목차는 초록과 같은 앞부분에 있으므로 함께 가져온다.** 초록만 보고 목차를 빠뜨리지 말 것.
  사이트가 목차 필드를 제공하면 그것을, 아니면 PDF 앞부분의 목차(차례)를 옮긴다.
- 이렇게 하면 근거가 초록+목차로 좁혀져 안정적이고, 토큰도 절약된다.

마크다운 파일의 본문은 **반드시 다음 순서**로 작성하며, 각 섹션은 별도 제목으로 구분한다:

```markdown
## 요약
(1~2문장의 핵심 개요)

## 목차
(마크다운 리스트 형식 - 상세함)

## 연구 배경 및 목적
(이 연구를 하게 된 계기, 해결하려는 문제, 연구의 필요성)

## 연구 방법
(연구 대상, 연구 설계, 데이터 수집 방식, 분석 방법 등)

## 주요 결과
(연구에서 도출된 주요 발견, 결론, 제언 등)
```

**각 섹션 작성 시 유의사항**:
- **요약**: 1~2문장으로 전체 연구의 핵심을 간결하게 표현
- **목차**:
  - 사이트가 목차 필드를 제공하면 그것을, 없으면 PDF 앞부분의 목차(차례)를 옮긴다.
  - `table_of_contents` front matter 에 넣으며, 장은 들여쓰기 없이, 절·소절은 2칸씩
    들여쓴다. **페이지 번호와 점선(···)은 제거한다.**
  - 아코디언(토글)으로 표시되므로 장·절·소절 구조를 상세히 반영한다.
- **배경/목적, 방법, 결과**: 각각 1~2문단으로 충분한 맥락 유지

**요약(초록) 출처 선택** (`abstract_source` front matter):
1. 사이트에 초록/요약이 있으면 → `site_abstract`
2. 사이트엔 없고 PDF에 초록이 있으면 → `pdf_abstract`
3. 사이트·PDF 모두 없으면 직접 분석 → `pdf_analyzed` / `page_analyzed`
4. 원문이 없으면 사이트 게시 내용 요약 → `page_summary`

### 국제소식 및 동향형 콘텐츠 (order 9~12) - 간단한 본문

마크다운 파일의 본문은 **다음 구조**로 작성:

```markdown
## 요약
(해당 자료/원본을 기반으로 한 핵심 내용 요약)
```

- 배경-방법-결과 구조화 불필요
- 1~2문단으로 간결하게 작성
- `abstract_source: page_summary`

#### 한국과학창의재단 동향리포트 (9)
- 해당 기관의 동향리포트 사이트를 직접 읽고 요약
- 원문 내용에 충실한 요약 작성

#### 교육정책네트워크 국제기구 동향 (10) - **중요**

**게시판 구조 (2026-07 확인)**: 이 게시판에는 **개별 글 상세 페이지가 없다.**
각 항목은 국문 제목 + 영문 원제 + 출처(OECD/UNESCO/WorldBank) + 날짜뿐이고,
제목 링크가 곧바로 원문 사이트로 직행한다. 즉 이 사이트에는 요약할 본문이 없으므로
**링크를 따라가 원문을 읽는 것이 유일한 방법이다.**

1. 목록에서 제목·출처·날짜·원문 URL 수집 (`<td class="bbs_tit">` 의 `a.tit-a` href)
2. 각 기사의 **외부 링크를 반드시 따라가기**
3. 원본 사이트에서 **실제 자료를 읽고 분석하기**
4. 원본 자료를 기반으로 **정확한 요약 작성** (구체적 통계·발견사항·정책 권고 포함)

**주의**: 제목만으로는 대략적인 요약을 만들어서는 안 됨. 반드시 원본 자료 확인 필수.

**source_url**: 게시판 목록 주소가 아니라 **원문 URL**을 쓴다. 게시판에 상세 페이지가
없으므로 원문 URL이 유일한 고유 키다. 목록 href 끝에 붙는 `?utm_source=...` 추적
파라미터는 제거한 정규 URL을 쓴다.

**알려진 접근 제약**:
- `www.oecd.org` / `www.oecd-ilibrary.org` / `unesdoc.unesco.org` 는 봇 차단(403)이라
  WebFetch·curl 모두 실패한다. 이때는 웹 검색으로 **OECD 공식 페이지의 초록·설명**을
  확보해 근거로 삼는다. 근거를 얻지 못하면 요약을 비우고 사용자에게 알린다.
- `oecdedutoday.com`(OECD 교육 블로그), `blogs.worldbank.org`, `www.worldbank.org`,
  `www.iesalc.unesco.org`, `www.unesco.org` 는 정상 접근된다.
- OECD 보고서는 `www.oecd.org/content/dam/...` 직링크 PDF가 있는 경우가 있어
  `pdf_url` 로 연결할 수 있다.

**중복 게시**: 게시판이 같은 원문을 다른 국문 제목·날짜로 두 번 올리는 경우가 있다.
`source_url` 이 같으면 1건만 생성한다.

#### 교육과정평가원 국제교육동향 (11)
- 교육과정평가원에서 제공하는 PDF 파일(국제교육동향 보고서) 수집
- PDF에서 텍스트 추출 및 원문 내용 분석
- 추출한 원문을 기반으로 정확한 요약 작성
- 사이트 활용법 (2026-07 확인)
  - 목록: `.../boardCnts/list.do?boardID=5000064&m=030207&s=kice&page=<n>`
    (페이지 파라미터는 `page`). 각 `<tr>` 에 `goView('5000064','<seq>')` 의 seq,
    제목(`[국가] 제목` 형태), `fn_fileDown('<fileKey>')` 의 PDF 다운로드 키가 있다.
  - 상세(= `source_url`): `.../boardCnts/view.do?boardID=5000064&boardSeq=<seq>&m=030207&s=kice`
    (목록에 fileKey 가 안 보이면 상세 HTML 에서 `fn_fileDown` 을 뽑는다.)
  - **PDF 다운로드는 POST**: `.../boardCnts/fileDown.do` 에 `fileSeq=<fileKey>` 로 POST.
    PDF 첫 줄에 `국제교육동향 / 20XX년 N호 / 발행일`, 이후 '배경'·'주요내용'에 본문이 있다.
    → `abstract_source: pdf_analyzed`. PDF 는 안정적 GET 직링크가 없어 `pdf_url` 은 비운다.
  - **호(號)마다 국가 특집 주제가 다르다.** 최신호가 SW·AI 와 무관한 주제(예: 민주시민
    교육)일 수 있으니, 관심 키워드로 게시판을 거슬러 올라가 AI·디지털 주제 호를 고른다.
    2024년 2호가 'AI 기술 도입' 국가별 특집이라 좋은 소스다. 동향형이라 `region` 에
    국가명을 넣는다.

#### 교육정책네트워크 국가별 교육동향 (12)
- 교육정책네트워크 정보센터의 국가별 교육동향 사이트 콘텐츠 직접 읽기
- 해당 사이트에 게재된 내용을 기반으로 요약 작성
- 사이트 활용법 (2026-07 확인) — 국제기구동향(10)과 같은 사이트, 다른 게시판
  - 목록: `https://edpolicy.kedi.re.kr/edpolicy/board/30?pageIndex=<n>`
    각 `<tr>` 의 `view(<seq>, event)` 가 식별자, 제목은 `[국가] 제목` 형태.
  - 상세(= `source_url`, GET 가능): `.../edpolicy/board/30/<seq>`
    상세에 원문제목·자료출처·보도일과 함께 **번역·요약된 본문**이 그대로 있다.
    (국제기구동향(10)과 달리 외부 링크를 따라갈 필요 없이 사이트 본문을 요약하면 된다.)
    → `abstract_source: page_summary`, 동향형이라 `region` 에 국가명.
  - **나라별 일반 교육 소식이라 SW·AI 무관한 항목이 대부분.** 관심 키워드로
    게시판을 훑어 AI·디지털 주제를 골라 담는다(11번과 동일한 접근).

**작성 규칙** (모든 유형):
- 원문 초록을 대량으로 그대로 복사하지 말고, 직접 요약하거나 짧게 출처를 밝혀 인용
- 각 항목은 1~2문장으로 간결하되, 충분한 맥락 유지
- **원본 자료를 반드시 확인한 후 작성** (제목만으로 작성 금지)

## 키워드 생성 우선순위
아래 순서로 판단한다.
1. 사이트에 키워드가 있으면 그것을 사용
2. 사이트엔 없고 원문에 키워드가 있으면 그것을 사용
3. 사이트·원문 모두 없으면 요약에서 5~10개 추출
4. 원문이 없으면 사이트 요약에서 5~10개 추출
- 키워드는 반드시 `src/_data/keywords.json` 레지스트리와 대조한다.
  의미가 같은 기존 키워드가 있으면 **그 표기를 재사용**하고(예: "생성형 AI"→"생성형AI"),
  없을 때만 새 키워드를 레지스트리에 추가한다. 표기 흔들림(공백/대소문자/영문)을 만들지 않는다.

## 자료 선택 기준

### 관심 키워드
다음 키워드 중 하나 이상을 포함한 자료만 수집·분석 대상으로 삼는다:
- 정보, SW, AI, 인공지능, 생성형AI, 자동평가, 자동채점
- 디지털 리터러시, 컴퓨팅 사고력, 프로그래밍, 코딩
- 정보교과, 정보교육, 정보보호, 정보윤리
- 디지털 기술, 디지털 교육, 디지털 전환

### 기관별 수집 정책

**연구보고서 (KICE 교육과정평가원, KIED 교육개발원 등 전 교과 대상 기관)**
- 전 교과를 연구 대상으로 하므로, 위 관심 키워드 관련 자료만 선택
- 토큰 효율성을 위해 무분별한 수집 회피
- 사용자가 분석 대상을 명시하면, Claude Code가 해당 사이트에서 관심 키워드 자료를 필터링해 수집
- **"N건"은 게시판 최신 N건이 아니라, 관심 키워드로 검색·필터링한 결과 중 N건이다.**

**KICE 연구보고서 사이트 활용법 (2026-07 확인)**
- 목록은 `srchWord` 로 키워드 검색된다. 관심 키워드를 각각 질의해 후보를 모은 뒤
  `goView(seq)` 의 seq 로 중복을 제거한다.
  ```
  https://www.kice.re.kr/resrchBoard/list.do?cate=0&s=kice&m=030109&srchType=0&srchWord=인공지능
  ```
  ("정보" 처럼 너무 흔한 말은 무관한 자료가 대량으로 걸리므로 쓰지 않는다.)
- 상세: `https://www.kice.re.kr/resrchBoard/view.do?seq=<seq>&s=kice&m=030109` (= `source_url`)
- **초록은 '연구내용' 필드에 있다.** '한글개요'·'연구필요성 및 목적'·'연구방법'·
  '성과물 주제어' 칸은 거의 항상 비어 있으니 개요란만 보고 판단하지 말 것.
  → `abstract_source: site_abstract`
- **게시일**: 화면에는 발간년도만 있으나, PDF 경로의 13자리 숫자가 업로드 시각(ms)이다.
  이 값에서 `date` 를 산출한다. 발간년도와 게시일이 해를 넘겨 다를 수 있다.
- **목차**는 항목 끝에 페이지 번호가 붙어 있다. 제거하고 들여쓰기로 계층을 표현한다.
- ORM(연구자료·가이드북·이슈페이퍼)은 '연구내용'이 "본문을 참고하세요" 수준인 경우가
  있다. 이때는 PDF 원문을 분석해 작성하고 `abstract_source: pdf_analyzed` 를 쓴다.
  PDF 텍스트 추출은 `pip3 install --user pypdf` 후 `PdfReader(...).extract_text()`.
  (내려받은 PDF는 스크래치패드에만 두고 저장소에 커밋하지 않는다.)

**KEDI 연구보고서 사이트 활용법 (2026-07 확인)**
- 목록 검색은 **`plTitl`** (제목 검색). `q` 는 필터링되지 않으니 쓰지 말 것.
  ```
  https://www.kedi.re.kr/khome/main/research/listPubForm.do?plTitl=인공지능&maxResults=100
  ```
- 행에서 `selectPubFormFn('<plNum0>')` 로 식별자를, `downloadAction(...)` 인자로 PDF
  정보를 얻는다. `<td class="tfile">` 이 비어 있으면 **PDF 미첨부**다.
- 상세: `https://www.kedi.re.kr/khome/main/research/selectPubForm.do?plNum0=<plNum0>` (= `source_url`)
- **상세 페이지의 '연구 요약' 필드에는 초록이 아니라 목차가 들어 있다.** 즉 사이트에는
  초록이 없다. → 요약은 **PDF 원문**을 읽어 작성하고 `abstract_source: pdf_analyzed`.
- **연구책임자·연구진은 인라인 JS에 있다.** 화면의 "정보를 불러오지 못했습니다"는
  `<noscript>` 폴백이다. `researchSplt('이름|아이디|소속:^:...')` 를 파싱한다.
- **PDF는 POST로만 받을 수 있다**(GET·정적 경로 모두 실패). 안정적 직링크가 없으므로
  `pdf_url` 은 비우고 `source_url` 만 연결한다. 분석용 내려받기는 아래처럼 한다.
  ```
  curl -X POST https://www.kedi.re.kr/khome/main/research/downloadPubFileAction.do \
    --data-urlencode "plNum0=.." --data-urlencode "pcPart=.." --data-urlencode "pcCode=.." \
    --data-urlencode "plTitl=.." --data-urlencode "origName=.." --data-urlencode "saveName=.." \
    --data-urlencode "savePath=.." --data-urlencode "pfType=P" -o out.pdf
  ```
- PDF 앞부분의 **'연구 요약'** 섹션이 배경·방법·결과를 그대로 담고 있어 요약의 근거로 쓴다.
- 구분(kind)에 `기본연구`(RR), `수탁연구`(CRR/CRM), `이슈페이`(IP/CIP), `연구자료`(RM),
  `현안보고` 등이 섞여 있다. **연구보고서로 볼 것은 RR·CRR·IP/CIP** 이고, 포럼 자료집·
  기획기사·사업 결과보고서·국제회의 자료(RM/CRM 다수)는 연구가 아니므로 제외한다.
- 일부 오래된 PDF는 텍스트를 못 얻는다. 스캔 이미지(예: CRR2022-13)이거나 폰트에
  유니코드 매핑이 없어 글리프 ID만 나오는 경우(예: RR2022-01)다. OCR 수단이 없으면
  근거를 얻을 수 없으므로 건너뛰고 사용자에게 알린다.

**SPRi 소프트웨어정책연구소 (5)**
- **SW·AI 전문 기관이라 발간물 전부가 관심 키워드에 해당한다.** KICE·KEDI 같은
  전 교과 대상 기관과 달리 키워드 필터링이 불필요하므로 **최신순으로 선정**한다.
- 사이트 활용법 (2026-07 확인)
  - 목록: `https://www.spri.kr/posts?data_page=<n>&code=data_all&study_type=&board_type=research`
    행에서 `/posts/view/<vid>`, `bg_c2`(보고서번호 RE-xxx), `s_authors=`(저자), 날짜를 얻는다.
  - 상세(= `source_url`): `https://www.spri.kr/posts/view/<vid>?code=research&board_type=research`
  - **상세에 구조화된 요약문이 그대로 있다.** `tab_1` = 요약문, `tab_2` = 목차.
    요약문은 `1. 제목 / 2. 연구 목적 및 필요성 / 3. 연구의 구성 및 범위 /
    4. 연구 내용 및 결과 / 5. 정책적 활용 내용 / 6. 기대효과` 구성이라
    본문 4개 절에 그대로 대응된다. → `abstract_source: site_abstract`
    (PDF를 열 필요가 없다. 파싱 시 `tab_1`~`tab_2` 구간, `tab_2`~`footer` 구간으로
     경계를 끊어야 푸터·뉴스레터 문구가 섞이지 않는다.)
  - **PDF는 안정적인 GET 직링크가 있다**: `https://www.spri.kr/download/<file_no>`.
    `file_no` 는 상세의 `file_down('<file_no>')` 에서 얻는다(vid 와 다른 번호다).
    → `pdf_url` 을 채운다.
  - 저자 소속은 `산업정책연구실 책임연구원` 처럼 SPRi 내부 직위다. 발행 기관 소속이므로
    `lead_affiliation` 은 비운다.

**KOSAC 한국과학창의재단 사이트 활용법 (2026-07 확인)**
- 과학·수학·융합교육 전반을 다루므로 **관심 키워드 필터링 필요**.
- 목록: `https://www.kosac.re.kr/menus/244/boards/457/posts?page=<n>` (제목·등록일)
- 상세(= `source_url`): `https://www.kosac.re.kr/menus/244/boards/457/posts/<pid>`
- Next.js 사이트라 데이터가 **두 곳**에 있다. 둘 다 보고 긴 쪽을 쓴다.
  - `<div hidden id="S:0">` 의 SSR 폴백 HTML → `view_con` 에 HTML 서식 요약
  - flight 페이로드의 `{\"children\":\"연구요약\"}...{\"children\":\"...\"}` → 평문 요약
- **PDF 직링크가 flight 페이로드의 `fileUrl` 에 있다**(`https://cdn.kosac.re.kr/files/cms/attach/...`).
  화면의 다운로드 `href` 는 비어 있으니 페이로드에서 뽑는다. → `pdf_url` 채움.
- 사이트 키워드는 `keyword_list` 의 `#` 항목에 있다(있는 건도, 없는 건도 있음).
- 연구요약이 비어 있는 건이 적지 않다. 그때는 PDF를 분석한다(`pdf_analyzed`).
  KOSAC PDF 앞부분에는 대개 **'보고서 초록'**(연구 목적/연구방법/연구 성과/기대효과/색인어)이 있다.
- 연구책임자 필드에 `변정호(강원대학교 과학교육학부)` 처럼 외부 소속이 함께 오면
  `lead_affiliation` 으로 분리한다. 괄호가 중첩된 `방준성((주)와이매틱스)` 형태를
  깨뜨리지 않도록 마지막 닫는 괄호까지 잡아야 한다.

**KERIS 한국교육학술정보원 사이트 활용법 (2026-07 확인)**
- 교육 ICT 외에 **RISS·대학도서관·학술지 사업 보고서도 섞여 있어** 필터링 필요.
- 목록: `https://keris.or.kr/main/ad/pblcte/selectPblcteRRList.do?mi=1138&currPage=<n>`
  행에 `pblcteView('<seq>')`, 연구책임자, 연구진, 발행년도, `listFileDown data-id` 가 있다.
- 상세(= `source_url`): `.../selectPblcteRRInfo.do?mi=1138&pblcteSeq=<seq>` (GET 가능)
  - **키워드**(`키워드` 필드), **목차**(`<h3>목차</h3>` 다음 `div.txt_wrap`, `<br>` 구분),
    **저자소개**(외부 소속 포함)가 있으나 **초록은 없다.**
- **PDF는 GET 직링크**: `https://keris.or.kr/common/fileDownload.do?fileKey=<fileKey>&dwlTy=pblcte`
  (`fileKey` 는 상세 HTML 에 있음). → `pdf_url` 채움. 초록은 PDF 앞부분의
  **'요 약'** 절에서 얻는다(`abstract_source: pdf_abstract`).
  ※ 목차의 '요 약'과 헷갈리지 않게, 점선(`···`)이 적고 한글이 많은 지점을 골라야 한다.
- **스캔 이미지 PDF가 많다.** `pdftotext` 가 빈 결과를 내거나 `pdffonts` 에 폰트가
  없으면 텍스트 레이어가 없다는 뜻이다. 이때는 아래 OCR 절차를 쓴다.
- 발행년도만 제공하고 게시일이 없다. `date` 는 `<발행년도>-01-01` 로 둔다.

**스캔 PDF OCR 절차 (poppler + tesseract, 2026-07 도입)**
```
brew install poppler tesseract tesseract-lang   # 이미 설치됨
pdftoppm -r 300 -gray -f 1 -l 14 -png in.pdf out/p    # 앞 14쪽만 300dpi 변환
for img in out/p-*.png; do tesseract "$img" - -l kor --psm 6 >> out.txt; done
```
- 요약/초록은 대개 앞 14쪽 안에 있으므로 전체를 OCR할 필요가 없다(200쪽 OCR은 매우 느리다).
- 요약이 앞에 없으면 목차를 보고 위치를 잡는다. 국문초록이 **보고서 끝**에 있는 경우
  (참고문헌 뒤)도 있고, 실태조사류처럼 **요약 자체가 없어** 서론을 써야 하는 경우도 있다.
- **OCR은 한글은 잘 읽지만 영문·숫자를 자주 깨뜨린다.** `AI`→`ㅅ1`/`41`, `RAG`→`1143`
  같은 오인식이 흔하다. 한글 서술로 의미를 확인하고 영문 약어·수치는 그대로 옮기지 말고
  문맥으로 복원하거나 확실하지 않으면 쓰지 않는다.
- `abstract_source`: PDF의 '요 약' 절을 OCR한 경우 `pdf_abstract`,
  요약이 없어 서론 등을 분석한 경우 `pdf_analyzed`.

**이슈리포트 (6)**
- 위 관심 키워드 관련 자료만 선택

**카드뉴스 (7) — 교육과정평가원 카드뉴스**
- 제목만 수집 (.md 파일 생성, 요약/키워드 불필요). front matter 는
  institution/title/date/source_url 만. 저자 정보 없음.
- **브리프(8)와 동일하게** institutions.json 의 kice-cardnews 에
  `"title_external": true` 가 있어 제목 클릭 시 상세 페이지가 아니라
  기관 사이트(source_url, 새 탭)로 바로 이동한다. (동일 메커니즘: [[브리프 규칙]])
- 사이트 활용법 (2026-07 확인)
  - 목록(갤러리형, 정적 HTML): `.../cardNewsBoard/list.do?boardId=1&s=kice&m=030216&page=<n>`
    (페이지 파라미터는 `page`, `pageIndex` 아님). `<li>` 의 `<img alt="...">` 가 제목,
    `detail/view.do?seq=<seq>` 가 seq, 이미지 경로 `/upload/cardNewsBoard/1/YYYY/MM/<seq>/`
    에서 발행 연·월을 얻는다(목록에 별도 날짜 표기 없음).
  - **개별 카드뉴스 URL(= source_url, GET)**: `.../cardNewsBoard/view.do?seq=<seq>&m=030216&s=kice`
  - 전 교과 대상이라 관심 키워드 필터링 필요. SW/AI/디지털 카드뉴스는 많지 않으니
    지능정보사회·컴퓨터 기반 평가 등 인접 주제까지 포함해 채운다.

**브리프 (8) — 교육개발원 KEDI Brief**
- 제목만 수집 (.md 파일 생성, 요약/키워드 불필요)
- 각 브리프당 1개의 .md 파일 생성. front matter 는 institution/title/
  lead_researcher(저자)/date/source_url 만. 본문·keywords·abstract_source 없음.
- **제목 클릭 시 상세 페이지가 아니라 해당 기관 사이트(source_url)로 바로 이동한다.**
  institutions.json 의 kedi-brief 에 `"title_external": true` 플래그가 있고,
  card.njk·institution.njk·index.njk(검색)가 이 플래그를 보고 제목을 source_url 로
  (새 탭) 연결한다. 브리프 저자는 KEDI 소속이므로 lead_affiliation 은 비운다.
- 사이트 활용법 (2026-07 확인)
  - 목록은 JS(XHR)로 로드된다. `kediBriefData.do` 에 POST 한다.
    ```
    curl -X POST https://www.kedi.re.kr/khome/main/research/kediBriefData.do \
      -H "X-Requested-With: XMLHttpRequest" \
      --data "maxResults=15&currentPage=<n>&board_sq_no=41&selectTp=0&isReply=0&stored_file_type=1&doc_use_yn=N&editor_use_yn=Y&prvw_use_yn=N&srchType=1"
    ```
    행에서 `goReadSelect('<sq>')` 의 sq, 제목(`[YYYY년 N호 | 저자] 본제목`), 날짜,
    `downloadAction(...)` 의 PDF 정보를 얻는다. 관심 키워드 필터링 필요(전 교육 주제).
  - **개별 브리프 URL(= source_url, GET 가능)**:
    `.../selectKediBriefForm.do?article_sq_no=<sq>&board_sq_no=41&maxResults=15&currentPage=1&selectTp=0&isReply=0`
  - 목록 제목은 길면 잘린다(`...`). 정확한 전체 제목은 PDF 표지에서 확인한다.
    PDF 도 POST(`downFileAction.do`)로만 받는다. 표지가 이미지라 OCR이 필요한 건도 있다.

**한국과학창의재단 동향리포트 (9)**
- 해당 기관의 동향리포트 목록에서 자료 수집
- 기관 사이트에 게재된 글을 직접 읽고 요약 생성
- abstract_source: page_summary

**교육정책네트워크 국제기구 동향 (10)**
- 교육정책네트워크 국제기구 동향 페이지에서 기사/뉴스 수집
- **중요**: 제목만으로 요약을 작성하지 않음
- 각 기사의 외부 링크를 반드시 따라가 원본 자료(OECD, UNESCO, World Bank 등) 확인
- 원본 자료의 실제 내용을 읽고 분석한 후 요약 작성
- 구체적인 통계, 발견사항, 정책 권고사항 등 포함
- abstract_source: 원문 페이지를 직접 읽고 분석했으므로 `page_analyzed`.
  원문에 접근하지 못해 게시 정보 수준으로만 요약했다면 `page_summary`.

**교육과정평가원 국제교육동향 (11)**
- 교육과정평가원에서 제공하는 PDF 파일(국제교육동향 보고서) 수집
- PDF에서 텍스트 추출 및 원문 내용 분석
- 추출한 내용을 기반으로 요약 및 키워드 생성
- abstract_source: pdf_analyzed

**교육정책네트워크 국가별 교육동향 (12)**
- 교육정책네트워크 정보센터의 국가별 교육동향 페이지에서 자료 수집
- 해당 사이트에 게재된 콘텐츠를 직접 읽고 요약 생성
- abstract_source: page_summary

## 보고서 인덱스 CSV (`data/report_index.csv`) — 토큰 절약용 색인

매 세션마다 기관 사이트의 보고서를 PDF까지 분석하면 토큰이 많이 든다. 이를 줄이기 위해
**제목만 크롤링한 색인 CSV**를 두고, 이 CSV를 근거로 요약 대상을 고른다.

- **대상 게시판(11)**:
  - **키워드 필터형(8)** — 전 교과/전 교육주제라 관심 키워드로 관련여부 판정:
    kice-research, kedi-research, kosac-research, keris-research, spri, keris-issue,
    kice-trend, **kedi-brief**.
  - **전부 관련형(3)** — 세계 교육 트렌드 확인용이라 SW·AI 무관하게 **관련여부=o 고정**
    (크롤러가 `force_rel=True`): **kosac-trend(9), edpolicy-intl(10), edpolicy-domestic(12)**.
    (`매칭키워드`는 참고용으로 계속 채워, 트렌드 항목 중 SW·AI 건을 구분할 수 있다.)
- **컬럼**: 기관코드, 기관명, 식별자, 제목, 발행, source_url, 관련여부(o/X),
  매칭키워드, 요약여부(o/X), 갱신일.
  - `관련여부`: 키워드 필터형은 **제목의 관심 키워드 매칭**으로 자동 판정(제목만 보므로
    저렴, PDF 안 엶). 전부 관련형은 항상 o.
  - `요약여부`: `src/reports/<code>/` 의 기존 식별자와 대조해 자동 표시.
    edpolicy-intl(10)만은 상세페이지가 없어 **외부 원문 URL(utm 제거)** 로 대조한다.
    (게시판이 과거엔 '월별 주요동향' 내부 상세글, 최근엔 개별 기사 외부 직링크형이라
    크롤러는 외부 직링크 항목만 담는다.)
- **생성/갱신**: `python3 scripts/build_index.py` 실행 → `data/report_index.csv` 재작성.
  전체 게시판을 다시 크롤링해 신규 글을 추가하고 요약여부를 최신화한다(KEDI는 7천여 건이라
  72페이지, 수 분 소요). git 으로 커밋해 세션 간 유지한다. 사이트 빌드 대상(`src/`)이
  아니라서 배포에는 포함되지 않는다.
  - **동향/국제/국가별(9·10·12)도 색인에 포함**한다. 최신순 수집 대상이지만, 이미 요약한
    글을 요약여부=o 로 추적해 중복을 막고 남은 후보를 보여주기 위함이다.
- **요약 대상 선정**: CSV에서 `관련여부=o AND 요약여부=X` 행을 뽑아, 그 글만 원문을 열어
  요약한다. 요약 후 다음 갱신 때 `요약여부`가 자동으로 o 가 된다.
- **주의**: 관련여부는 제목 기반 1차 필터라 오탐/누락이 있을 수 있다. 실제 요약 전
  제목이 애매하면 확인한다. 최신호가 관심 주제와 무관한 특집(예: 민주시민 교육)이면
  이전 호로 거슬러 올라가 관련 글을 고른다.

## 세션 요약(핸드오프) 규칙 — 토큰 절약용

세션을 마치거나 요약할 때는 상태를 저장소에 남겨, 다음 세션이 사이트를 재크롤링해
상태를 재추론하지 않게 한다. 요약에는 다음을 포함한다.

1. **바뀐 규칙**: 이번 세션에 정한 규칙·방식을 CLAUDE.md에 반영했는지.
2. **CSV 갱신**: 새 요약 .md 를 커밋했으면 `python3 scripts/build_index.py` 로
   `report_index.csv` 를 재생성한다(요약여부가 `src/reports` 에서 자동 최신화). **새
   요약이 없으면 재크롤 불필요** — CSV 의 `갱신일` 칼럼이 마지막 크롤 시점이자 신뢰 기준.
   (재크롤은 KEDI 72페이지 때문에 수 분·토큰이 드니 새 요약을 커밋한 뒤에만 돌린다.)
3. **아직 요약 안 함 명시**: CSV 는 '후보 목록'일 뿐, `관련=o AND 요약=X` 건은
   **다음 세션의 할 일**이다. 요약본을 만든 게 아님을 분명히 한다.
4. **git 상태**: 무엇을 커밋·푸시했는지(미완이면 그것도).
5. **다음 착수점**: 기관별 `관련·미요약` 건수와 "재크롤 말고 CSV 에서 골라 원문만 열기".
6. **알려진 예외/부채**: 예) edpolicy-intl 은 정식 문서 URL 로 저장해 게시판 링크와
   다른 2건이 요약여부 대조 안 됨(무해), 스캔 PDF 라 OCR 필요/건너뛴 건 등.

## 증분 업데이트 절차
사용자가 기관과 기간을 지정하면(예: "kice-research, 2025-06 ~ 2025-12") 다음을 수행한다.
(또는 위 인덱스 CSV에서 `관련=o, 요약=X` 를 골라 진행한다.)

**단계 1: 자료 필터링**
- 해당 기관 목록에서 그 기간의 자료를 추린다. (기간 미지정 시: 저장소에 없는 최신 자료)
- 연구보고서/브리프인 경우: 위 "자료 선택 기준"의 관심 키워드로 필터링
- 국제소식인 경우: 모든 자료 포함

**단계 2: 중복 제거**
- `src/reports/`의 기존 .md에서 `source_url`을 확인한다.
   ```
   grep -rh "source_url:" src/reports/ | sort -u
   ```
- 이미 존재하는 `source_url`은 건너뛰고, 없는 것만 새 .md로 생성 대상으로 삼는다.

**단계 3: 자료 분석 및 생성**
- 각 자료(사이트 페이지 또는 PDF)를 분석해 .md 파일 생성
- 요약, 키워드, (필요 시) 목차를 작성

**단계 4: 보고**
- 새로 만든 건수와 제목 목록을 사용자에게 보고한다. 임의로 push하지 않는다.

## 작업 규칙
- 요약·키워드는 반드시 실제 원문/사이트 근거에 기반한다. 추측으로 채우지 않는다.
- 근거를 찾지 못하면 그 필드를 비우고 사용자에게 알린다.
- 저장소에 원문 PDF 파일을 올리지 않는다. 링크(`pdf_url`, `source_url`)로만 연결한다.
- 커밋·배포는 사용자 확인 후 진행한다.
