# 시대 01 — 툴킷

한국어 품질 upstream 넷을 하나의 설치 단위로 묶어, Claude Code와 Codex에서 에이전트가 실제로 쓸 수 있는 도구로 만든 시대입니다.

**상태: 닫힘 (2026-09-15).** 6-build P1~P7 완료, 7-review 끝, `dev`는 `master`에 머지됐습니다. release-blocked 3건(모두 Codex 쪽)은 리뷰에서 받아들이고 넘겼습니다 — 재시험은 [`../99-codex-retest/`](../99-codex-retest/)에 있습니다. 다음 시대의 입력은 [`7-review/review.md`](7-review/review.md) §G입니다.

**읽는 순서 (최소):**

1. [`3-spec/06_toolkit_spec.md`](3-spec/06_toolkit_spec.md) — §1 목적, §3 층, §5 공급 층, §14 프로토타입 계획, §16 결정 현황
2. [`5-preflight/06b_built_prototype.md`](5-preflight/06b_built_prototype.md) — P0 파일 지도, 06 반영 결정, 문서 검토
3. [`5-preflight/flow.md`](5-preflight/flow.md) — preflight 결정 D1~D7과 P1~P7 흐름
4. [`7-review/review.md`](7-review/review.md) — 무엇이 뒤집혔고 무엇이 다음으로 갔는가

이 시대의 문서는 기록입니다. 고치지 않고, 나중에 틀린 것이 드러나면 전방 포인터만 답니다.

## 문서 지도

| 단계 | 파일 | 내용 |
|---|---|---|
| 1-concept | `01_idea.md` | 초기 문제 의식과 원하는 것 |
| | `01a_findings_survey.md` | 유사 프로젝트 17종 조사와 판단 |
| 2-exploration | `02_stack.md` | 5층 스택 구상 |
| | `02a_findings_reusability.md` | "재사용성"의 뜻이 바로잡힘 — 에이전트에게 기능으로 제공 |
| | `03_engine.md` | 에이전트가 호출하는 기능 단위로서의 엔진 |
| | `03a_findings_decisions.md` | 하네스 중립 결정과 14개 세부 결정 |
| 3-spec | `04_design_spec.md` | 검증 엔진 안. **보류** — 나중에 검증을 더할 때의 목표 형태 |
| | `04a_findings_premise.md` | 전제 교체(upstream 신뢰, 사용성 우선), 로거 요구 |
| | `05_composition_spec.md` | 구성 계층 스펙. **보류** — 로거가 앞에 섰음 |
| | `05a_findings_measurement.md` | 판정/측정의 선, `watch:`. **검증 단계 준비 문서** |
| | `06_toolkit_spec.md` | **구현 대상.** 공급 / Skill / MCP / 하네스별 렌더, 프로토타입 계획, 결정 현황 |
| | `06a_findings_supply.md` | 공급 층(버전 고정 + 역할 단위 정규화 + 출처), 변환 3등급 |
| | `prompt-flow.html`, `diagrams/` | 06 기준 작동 구조. 루트 README가 같은 그림을 씀 |
| | `composition-structure.html` | 05 기준 작동 구조. 설계 세션에서 만든 페이지 |
| 4-plan | `README.md` | 계획은 06 §14·§16 안에 있음 |
| 5-preflight | `06b_built_prototype.md` | P0 사전 확인(lock, 파일 지도, 하네스 재확인, 06 반영 결정), 문서 검토 |
| | `explorations.md` | 열린 결정 탐색 보고 6건(절차 원천, 앵커 형식, 렌더 구분, 합성 규칙, 참조 역할, Codex 로컬 플러그인), E1 후속, Codex 헤드리스 실측, 환경 확인 |
| | `flow.md` | 구현 흐름 정의 — 결정 D1~D7, P1~P7, release를 막는 조건. 수락됨 |
| 6-build | `P1_ko-rewrite.md` | im-not-ai → ko-rewrite 손 추출, 헤드리스 실행 |
| | `P2_ko-diagnose.md` | yoonmoon → ko-diagnose, 참조 역할 |
| | `P3_policy.md` | fluent-korean 정책, 결정 ③, 채널 실측 |
| | `P4_abstraction.md` | 스키마, 추출기 코드, 네 번째 벤더, 업데이트 실측 |
| | `P5_claude-code-build.md` | 조립, 프로파일별 Claude Code 플러그인, 설치·eval |
| | `P6_codex-build.md` | Codex 빌드, 설치기, 채널 실측, 커스텀 에이전트 release-blocked |
| | `P7_server-logger.md` | 로거·hook·스탬프 싣기, Claude Code 실측, Codex 쪽 release-blocked |
| 7-review | `review.md` | release-blocked 수용과 머지, 스펙 개정 후보 B1~B8, 결정 재검토, preflight가 놓친 것, 등급 규칙, 다음 시대(검증 단계) |

## 단계 요약

```text
01 아이디어      "Claude Code의 한국어가 깨진다. 비슷한 것들을 모아 최적 조합을 찾고 싶다"
   ↓ 조사        생태계는 생성 시점 개입 / 생성 후 개입으로 갈림. 평가를 해본 프로젝트는 하나뿐
02 스택          L0 policy ~ L4 eval 5층. 원칙: taxonomy 하나, LLM 판정과 결정론 판정 분리
   ↓ 재정의      재사용성 = 에이전트에게 기능으로 제공. 프롬프트 층은 텍스트+계약+회귀테스트여야 장치가 됨
03 엔진          MCP tools/resources/prompts = gate/taxonomy/지시문. 두 방향(생성 주입, 검토 위임)
   ↓ 결정        하네스 중립. 14개 결정. 되돌아볼 지점 3개
04 검증 엔진 안  gate·report·eval 로 LLM 층을 검증. 보류
   ↓ 전제 교체   근거를 되짚음 → 검증 비중은 사용자 관심사에서 온 것. upstream 신뢰 + 사용성 우선으로
05 구성 계층     upstream 을 profile·preset·agent 로 묶는 얇은 층 + 판정하지 않는 로거. 보류
   ↓ 선 교정     자른 기준이 검증/비검증이었음 → 판정/측정으로. 이 판단은 검증 단계로 이월
   ↓ 목표 재확인  산출물은 계측 장치가 아니라 쓸 수 있는 도구. 검증은 다음 단계
   ↓ 사양 조사    Claude Code·Codex 공식 문서 확인. 세 가지 제약 발견
06 툴킷          Skill 이 지시문, MCP 가 계산, 하네스별 렌더가 정책 주입. 구현 대상
   ↓ 구현 점검   그릇은 있고 내용물이 없음 → upstream 을 우리 규격으로 받는 공급 층. 추상화는 프로토타입 뒤
   ↓ P0 사전 확인 upstream 4종 MIT 고정. 파일 지도에서 06과 어긋난 것 13건, 하네스 재확인에서 2건 (06b)
   ↓ P0 반영     06 개정: 정책 조각 단위, 앵커 규칙, rewrite invariant(hjongc 원칙 제외), Codex 플러그인 사실
   ↓ 문서 검토   문서 안 어긋남 13건 정정, 사양 재검증 26건(어긋남 없음, 몰랐던 것 9건). 열린 결정 8건 추가
   ↓ 프로세스    시대 / 7단계 일방향으로 재배치. 판단 규칙은 AGENTS.md로 분리
   ↓ 탐색        열린 결정 6건 독립 보고, B가 낡았는지 후속 탐색, Codex 헤드리스 실측(커스텀 에이전트 닿지 않음)
   ↓ preflight   flow.md — 결정 D1~D7, P1~P7 흐름. 수락
   ↓ build       P1~P5 완료(추출·스키마·Claude Code 빌드), P6 Codex 빌드(커스텀 에이전트 release-blocked), P7 로거(Codex 쪽 release-blocked)
   ↓ review      Codex 3건 수용 후 master 머지. 스펙 입력 B1~B8. LLM 판정기가 믿을 만하지 않음(C3). 다음 시대: 검증 단계
```

조사에서 나온 제약 셋이 06 의 형태를 결정했습니다.

- **출력 스타일은 서브에이전트에 닿지 않는다** → 정책을 에이전트 정의마다 직접 써넣는 것이 필수
- **Codex 의 MCP 는 tools 전용** → 지시문은 MCP prompt/resource 가 아니라 Skill 이 나른다
- **transcript 는 hook 의 안정적 입력이 아니다** → 로거는 hook 입력에서 점진적으로 조립한다

구현 점검에서 나온 원칙 둘이 06 의 진행 방식을 결정했습니다.

- **upstream 문장은 그들의 것, 형식은 우리의 것** → 문장은 고치지 않고 역할별 규격으로 정규화하며 출처를 단다
- **스키마는 실물에서 역산한다** → 세 벤더를 손으로 통과시킨 뒤 스키마를 만들고, 네 번째 벤더로 추상화를 시험한다

## 세 스펙의 관계

`04` → `05` → `06` 은 같은 대상의 세 판본이고, 셋 다 형식을 공유합니다. 구현 대상은 **06** 하나입니다.

| | 산출물 | 상태 |
|---|---|---|
| 04 | 검증 엔진. gate·report·eval 로 LLM 층을 검증 | 보류 — 목표 형태 |
| 05 | 구성 계층. 얇은 층 + 로거 | 보류 — 로거가 앞에 섰음 |
| **06** | **툴킷. 설치하면 쓰이는 도구** | **구현 대상** |

06 은 검증 단계의 부분집합입니다. profile·preset·agent·skill·레코드가 같은 형식을 쓰고, `ruleset`·`features`·`watch:`·`gate:`·eval 은 나중에 **더하는** 것입니다. 무엇을 어디에 더하는지는 06 §15에 있습니다. 검증 단계는 실제로 다음 시대가 됐습니다 — [`../02-validation/`](../02-validation/).

부분집합을 가르는 기준은 **판정하느냐 측정하느냐**입니다(05a). 판정은 값을 놓고 통과·중단을 정하는 것이고 04 에 있습니다. 측정은 값을 남기는 것이고 05 에 있습니다. 두 스펙을 잇는 장치는 profile 의 `watch:` 절입니다 — 04 의 `gate:` 와 형식이 같지만 넘어도 막지 않고 레코드에 표시만 남기며, 승격은 키 이름만 바꿉니다.

## 참고

- 06 기준 작동 구조 그림은 [`3-spec/prompt-flow.html`](3-spec/prompt-flow.html)과 루트 README에 있습니다. 05 기준 그림은 [`3-spec/composition-structure.html`](3-spec/composition-structure.html)입니다.
- 이 시대는 언어 규칙(시대 02부터 1-concept 한국어, 2~7단계 영어) 이전의 기록이라 전부 한국어입니다.
