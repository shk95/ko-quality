# ko-quality 설계 기록

`ko-quality` 프로젝트의 설계 문서와, 그 설계를 지으면서 내린 판단과 실제로 지어보니 달라진 것을 함께 두는 디렉터리입니다. 구현 코드는 저장소 루트에 있고, 이 디렉터리는 **왜 그렇게 지었는가**와 **지금 어디까지 왔는가**만 담습니다. 에이전트의 판단 규칙은 여기 없고 루트 `AGENTS.md`에 있습니다.

## 지금 할 일

> 새 세션은 여기서 시작합니다.

**현재 위치:** 시대 `02-validation` **닫힘** (2026-09-18). 시대 `03`은 아직 열지 않았고, 다음 할 일은 시대 03의 `1-concept`입니다. 시대 03의 범위와 입력은 [`02-validation/7-review/review.md`](02-validation/7-review/review.md) §G에 있습니다. 범위는 선행 조건이 먼저입니다(§F, F2): 적용된 스타일을 실사용 레코드에서 관찰할 수 있게 하는 문제, 영어 프롬프트를 번역하는 정책 결함, 측정 규칙, 생성기의 턴 프로토콜을 먼저 다루고, 실사용 레코드 재측정과 `watch:`→`gate:` 승격은 그다음 시대로 넘깁니다. 시대 02의 release-blocked(P9 검정력 부족)는 리뷰에서 보충 배치로 해소했습니다(§A). 시대 02와 시대 98은 이 리뷰를 거쳐 `master`에 들어갑니다. 이전 상태 기록: `7-review` 재개 대기 (2026-09-18).

**같이 도는 것:** 없음. 임시 시대 `99-codex-retest`는 재시험을 마쳤고 (2026-09-16), 결과는 시대 02의 3-spec이 받았습니다.

**읽는 순서 (최소):**

1. [`02-validation/6-build/README.md`](02-validation/6-build/README.md) — **여기서 시작합니다.** 빌드 규칙, 기록 형식, 진행 현황, 새 세션 handoff
1. [`02-validation/5-preflight/flow.md`](02-validation/5-preflight/flow.md) — 수락된 preflight. 미리 정한 결정과 단계별 흐름
1. [`02-validation/4-plan/10_plan.md`](02-validation/4-plan/10_plan.md) — 수락된 계획. 단계 P1~P9와 완료 조건
1. [`02-validation/3-spec/09_toolkit_spec.md`](02-validation/3-spec/09_toolkit_spec.md) — 구현 대상 스펙. §22가 결정 현황. 마무리 기록은 같은 디렉터리의 `09a`
1. [`02-validation/2-exploration/README.md`](02-validation/2-exploration/README.md) — 스펙의 근거. 읽는 순서, 실측 기록 색인
2. [`02-validation/2-exploration/02_scope.md`](02-validation/2-exploration/02_scope.md) — 이 시대의 범위와 시대 03과의 경계, 조사 의제
3. [`02-validation/1-concept/01_idea.md`](02-validation/1-concept/01_idea.md) — 이 시대가 무엇을 하려는가
4. [`01-toolkit/7-review/review.md`](01-toolkit/7-review/review.md) §B·§D·§G — 물려받은 스펙 입력과 preflight 입력
5. 필요할 때만 — [`01-toolkit/3-spec/06_toolkit_spec.md`](01-toolkit/3-spec/06_toolkit_spec.md) §15(검증 단계로 가는 길)·§16(결정 현황), [`01-toolkit/3-spec/05a_findings_measurement.md`](01-toolkit/3-spec/05a_findings_measurement.md)(판정/측정의 선)

## 구조: 시대와 일곱 단계

설계 계획 하나가 **시대(era)** 하나입니다. 시대 안은 일곱 단계 디렉터리로 나뉘고, 문서는 앞에서 뒤로만 흐릅니다.

```text
design/
├── 01-toolkit/            ← 시대. 번호 + 주제
├── 02-validation/
├── 98-host-isolation/     ← 끼어드는 시대
├── 99-codex-retest/       ← 임시 시대
└── <시대>/
    ├── README.md          그 시대의 문서 지도와 현재 위치
    ├── 1-concept/         아이디어와 문제 의식. 요구는 아직 느슨함
    ├── 2-exploration/     조사와 구체화. 요구의 뜻이 바로잡히는 곳
    ├── 3-spec/            스펙. 여러 판본이 나란히 있을 수 있고 구현 대상은 하나
    ├── 4-plan/            무엇을 어떤 순서로 짓는가
    ├── 5-preflight/       구현 흐름 정의. 사전 검증, 미리 정한 결정, release를 막는 조건. 마지막 상호작용 단계
    ├── 6-build/           자율 구현의 기록. 스펙을 고치지 않는다
    └── 7-review/          구현 후 리뷰. 다음 시대의 입력
```

| 단계 | 하는 일 | 사용자와 |
|---|---|---|
| 1 concept | 문제와 바라는 것 | 상호작용 |
| 2 exploration | 조사, 재정의, 대안 비교 | 상호작용 |
| 3 spec | 설계 결과물. 사이 문서(`a`)가 판단 근거를 남김 | 상호작용 |
| 4 plan | 구현 순서와 단계 | 상호작용 |
| 5 preflight | 흐름을 실행 가능한 수준으로 구체화하고, 가정을 검증하고, 결정을 미리 내림 | 상호작용. 깊이를 함께 조절 |
| 6 build | 구현. 멈추지 않고 끝까지. 판단은 `AGENTS.md` 기준 | **자율** |
| 7 review | 스펙과 달랐던 것을 읽고 다음 시대를 정함 | 상호작용 |

**일방향.** 앞 단계 문서는 그 시점의 기록이라 고치지 않습니다. 나중에 틀린 것이 드러나면 전방 포인터나 상태 표시만 답니다. 구현 중 발견은 6-build에 쌓이고, 스펙을 바꿀 만한 것은 7-review를 거쳐 다음 시대를 엽니다. 시대 안에서 되돌아가지 않습니다.

**예외 하나.** 3-spec의 구현 대상 스펙(지금은 시대 02의 09)은 5-preflight까지는 개정할 수 있습니다. 개정 근거는 사이 문서나 실측 기록에 있고 스펙 머리말이 그것을 가리킵니다. 6-build에 들어가면 그것도 멈춥니다.

## 문서의 종류

| 종류 | 파일 이름 | 담는 것 |
|---|---|---|
| 단계 문서 | `NN_<이름>.md` | 그 시점의 설계 결과물 |
| 사이 문서 | `NNa_findings_<주제>.md` | 다음 단계로 넘어가며 알게 된 것, 바꾼 것, 되돌아볼 지점 |
| 실측 문서 | `NNb_built_<주제>.md`, 6-build의 `P<n>_*.md` | 지어 보니 스펙과 달랐던 것, 스펙이 몰랐던 것 |

단계 문서만 읽으면 결과가 보이고, 사이 문서를 같이 읽으면 왜 그 결과가 됐는지가 보이며, 실측 문서까지 읽으면 그 판단이 실제로 맞았는지가 보입니다.

## 시대 목록

| 시대 | 주제 | 상태 | 문서 |
|---|---|---|---|
| `01-toolkit` | 툴킷 — 공급 층, Skill, 하네스별 렌더, 최소 로거 | 닫힘 (2026-09-15). `master`에 있음 | [README](01-toolkit/README.md) |
| `02-validation` | 검증 단계 — 측정, 판정기 검증, `watch:` 후보값, eval. 임시 코퍼스로 | 닫힘 (2026-09-18). `master`에 있음 | [README](02-validation/README.md) |
| `03` (미개설) | 실사용 레코드로 재측정, `watch:`→`gate:` 승격, 대조군 교대 | 범위 정해짐 (02 리뷰 §F·§G). `1-concept` 대기 | — |
| `98-host-isolation` | 저장소를 호스트 상태에서 떼어 내기 — 공개 기록 규칙, 로컬 데이터 규약, 기계적 차단 (끼어드는 시대) | 닫힘 (2026-09-18). 02의 리뷰 뒤 `master`에 있음 | [README](98-host-isolation/README.md) |
| `99-codex-retest` | Codex 채널 재시험 (임시) | 재시험 끝 (2026-09-16). 결과는 02의 3-spec으로 | [README](99-codex-retest/README.md) |

`99`는 임시 시대입니다. 새 설계를 열지 않고 미뤄 둔 실측만 담으며, 결과는 다른 시대의 입력으로 들어갑니다.

`98`은 끼어드는 시대입니다. 제품 설계가 아니라 저장소 운영을 다루므로 정식 번호 순서에 넣지 않습니다. 일곱 단계를 모두 밟고, 진행 중인 시대는 단계의 경계에서 멈췄다가 시대 98이 `dev`에 머지된 뒤 재개합니다. `master` 머지는 정식 시대와 같이 리뷰에서 정합니다.

## 참고

- 각 시대의 문서 지도와 읽는 순서는 그 시대 디렉터리의 `README.md`에 있습니다.
- **언어.** 시대 02부터 `1-concept/`는 한국어, 2~7단계 문서는 영어로 씁니다. 시대 01은 이 규칙 이전의 기록이라 한국어 그대로 둡니다. 영어 문서 안에서 한국어 고유의 용어(조사, 어미, 윤문 등)와 고유명사는 한국어를 섞어 써도 됩니다 (`AGENTS.md`).
