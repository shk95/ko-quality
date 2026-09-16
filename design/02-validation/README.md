# 시대 02 — 검증 단계

넣은 것이 효과가 있는지 아는 장치를 짓는 시대입니다. 시대 01이 "설치하면 쓰이는 도구"를 짓고 미뤄 둔 질문을 받습니다.

**현재 위치:** `3-spec` 초안 완료, 검증됨 (2026-09-17). 구현 대상 스펙은 [`09_toolkit_spec.md`](3-spec/09_toolkit_spec.md)입니다. 다음은 `4-plan`입니다.

## 문서 지도

2-exploration은 문서가 일곱이라 그 단계의 [README](2-exploration/README.md)가 읽는 순서, 실측 기록 색인, 서브에이전트 누계를 갖고 있습니다.

| 단계 | 파일 | 내용 | 상태 |
|---|---|---|---|
| 1-concept | [`1-concept/01_idea.md`](1-concept/01_idea.md) | 문제 의식, 리뷰가 바꾼 전제(판정기를 먼저 검증), 물려받은 입력(06 §13.1 근사치 재검토 목록 포함), 초기 가설, 열린 질문 | 작성됨 |
| 2-exploration | [`2-exploration/02_scope.md`](2-exploration/02_scope.md) | 전제 교정(레코드 0건), E1 결정(오프라인 대조 코퍼스), 강제 없는 스타일 선택 실측(B9), 시대 02/03 경계, 의제 E2~E7, `register`가 기제와 어긋나는 건(E4) | 작성됨 |
| 2-exploration | [`2-exploration/03_features.md`](2-exploration/03_features.md) | **E2** — 네 원천의 규칙 209개를 mechanical/llm/human으로 분류하고, 중복을 걷어 측정 단위 28개로 정리. 3단 구성(표준 라이브러리 / 형태소 분석기 / 입력+출력), 제외 패스, `kiwipiepy` 의존성. 태그셋은 실측으로 통과, 레시피 둘은 깨져 있었고 수정안까지 실측 | 작성됨 |
| 2-exploration | `04_*.md`~`08_*.md` | E3~E7 조사 결과. 목록은 [단계 README](2-exploration/README.md) | 작성됨 |
| 3-spec | [`3-spec/09_toolkit_spec.md`](3-spec/09_toolkit_spec.md) | **구현 대상.** 06을 대체하는 자기완결 스펙(영어). B1~B9, E2~E7, 시대 99 결과, 결정 S1~S3 | 초안, 검증됨 |
| 4-plan | — | 무엇을 어떤 순서로 짓는가. 이 시대부터 계획은 독립 문서입니다 | 비어 있음 |
| 5-preflight | — | 구현 흐름 정의. 시대 01의 §D가 입력입니다 | 비어 있음 |
| 6-build | — | 자율 구현 기록 | 비어 있음 |
| 7-review | — | 구현 후 리뷰. 시대 03을 여는 곳 | 비어 있음 |

## 이 시대가 받은 것

시대 01의 [`7-review/review.md`](../01-toolkit/7-review/review.md) §G가 인계 문서입니다.

- **개념:** 06 §15의 검증 단계 — `ruleset`, `features`, `watch:`, `gate:`, `outcome`, MCP tool, 대조군, preset 끝의 `gate` 단계, eval
- **스펙 입력:** B1~B8 (06을 고치지 않고 넘긴 개정 후보)
- **preflight 입력:** §D 다섯 항목과 §C3의 판정기 발견
- **열린 발견:** `task_type` 규칙의 한계, `preset`의 출처 없음, 등급 규칙이 고칠 것 없는 글을 B로 묶음, upstream 생성기가 J-1을 빠뜨림
- **미결 결정:** stop-slop-ko를 `policy` 조각 공급자로 넣을지와 `exempt` 복구 (06 §16.2. 리뷰 §G가 빠뜨렸고 1-concept이 다시 담았습니다)
- **근사치 재검토:** 06 §13.1의 아홉 항목. threshold를 걸기 전에 다시 보라는 스펙 조항이고, threshold를 거는 시대가 여기입니다 (리뷰 §B·§G가 열거하지 않아 1-concept이 직접 받았습니다)

## 범위와 경계

`2-exploration/02_scope.md`가 확정한 것:

- **측정 코퍼스.** `~/.ko-quality/`가 없습니다 — 레코드 0건이고 툴킷은 일상 사용된 적이 없습니다. 그래서 이 시대는 headless 대조 실행으로 코퍼스를 직접 만들되, **출하되는 로거를 통과시켜** 만듭니다. 스키마가 같으므로 시대 03은 분포만 갈아끼웁니다.
- **이 시대가 정하는 것.** features와 기계적 채점기, 판정기 일치도, 축별 on/off 차이, `watch:` 후보 threshold, eval, gate 의미론(설계만), `ruleset` 역할, stop-slop-ko와 `exempt`.
- **실측 하나.** 강제를 빼면 플러그인 하나에 스타일 여럿을 넣고, 골라 쓰고, `/output-style`로 세션 중 바꿀 수 있습니다(`tests/runs/02-E1/`). 선택은 `<프로젝트>/.claude/settings.local.json`에 남아 **프로파일이 프로젝트 단위**가 됩니다. P3의 "formal-report 도달 불가"는 다른 스타일이 강제된 동안에만 참이었습니다. 대가는 설치만으로는 아무것도 안 걸린다는 것입니다. 06 §9·§12의 개정 후보 **B9**로 두고 `3-spec`에서 정합니다.
- **시대 03으로 넘기는 것.** `watch:`→`gate:` 승격, off 교대 스케줄러와 대조군 윤리, `outcome`, §13.1 중 실사용 분포가 필요한 항목. 시대 03은 이 시대의 `7-review`에서 엽니다.

## 범위 밖

Codex 채널 재시험은 [`../99-codex-retest/`](../99-codex-retest/)에 있습니다. 미뤄 둔 실측이라 이 시대와 분리했습니다.

## 언어

`1-concept/`는 한국어, 2~7단계 문서는 영어입니다 (`AGENTS.md`). `README.md`는 한국어입니다.
