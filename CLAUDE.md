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
date: 2025-11-20                  # 게시 연도 기준 yyyy-mm-dd
source_url: https://...          # 원문 상세 페이지 (고유 키, 필수)
pdf_url: https://...             # 원본 PDF 직링크 (선택)
keywords: [생성형AI, 초중등, 교수학습]
abstract_source: pdf_analyzed    # 아래 4값 중 하나
---

## 요약
(본문)
```
- `source_url`은 중복 판별의 고유 키다. 항상 채운다.
- `pdf_url`은 선택. .do 계열 정부 사이트는 직링크가 없을 수 있으므로, 안정적 링크가
  없으면 비우고 `source_url`만 연결한다.
- `link_only` 기관(카드뉴스)에는 보고서 .md를 만들지 않는다.

## 요약(초록) 생성 우선순위
아래 순서로 판단하고, 사용한 경로를 `abstract_source`에 기록한다.
1. 사이트에 초록이 있으면 그대로 가져온다 → `site_abstract`
2. 사이트엔 없고 원문(PDF)에 요약/초록이 있으면 그것을 사용 → `pdf_abstract`
3. 사이트·원문 모두 초록이 없으면 원문을 직접 분석해 요약 → `pdf_analyzed`
4. 원문 자체가 없으면 사이트 게시 내용을 요약 → `page_summary`
- 원문 초록을 대량으로 그대로 복사하지 말고, 직접 요약하거나 짧게 출처를 밝혀 인용한다.

## 키워드 생성 우선순위
아래 순서로 판단한다.
1. 사이트에 키워드가 있으면 그것을 사용
2. 사이트엔 없고 원문에 키워드가 있으면 그것을 사용
3. 사이트·원문 모두 없으면 요약에서 5~10개 추출
4. 원문이 없으면 사이트 요약에서 5~10개 추출
- 키워드는 반드시 `src/_data/keywords.json` 레지스트리와 대조한다.
  의미가 같은 기존 키워드가 있으면 **그 표기를 재사용**하고(예: "생성형 AI"→"생성형AI"),
  없을 때만 새 키워드를 레지스트리에 추가한다. 표기 흔들림(공백/대소문자/영문)을 만들지 않는다.

## 증분 업데이트 절차
사용자가 기관과 기간을 지정하면(예: "kice-research, 2025-06 ~ 2025-12") 다음을 수행한다.
1. 해당 기관 목록에서 그 기간의 자료를 추린다. (기간 미지정 시: 저장소에 없는 최신 자료)
2. `src/reports/`의 기존 .md에서 `source_url`을 확인한다.
   ```
   grep -rh "source_url:" src/reports/ | sort -u
   ```
3. 이미 존재하는 `source_url`은 건너뛰고, 없는 것만 새 .md로 생성한다.
4. 새로 만든 건수와 제목 목록을 사용자에게 보고한다. 임의로 push하지 않는다.

## 작업 규칙
- 요약·키워드는 반드시 실제 원문/사이트 근거에 기반한다. 추측으로 채우지 않는다.
- 근거를 찾지 못하면 그 필드를 비우고 사용자에게 알린다.
- 저장소에 원문 PDF 파일을 올리지 않는다. 링크(`pdf_url`, `source_url`)로만 연결한다.
- 커밋·배포는 사용자 확인 후 진행한다.
