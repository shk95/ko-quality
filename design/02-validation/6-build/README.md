# 6-build — 구현

자율 구현 단계입니다. `dev` 브랜치에서 진행하고, `master` 머지는 7-review에서 정합니다.

**진행:** 열림 (2026-09-17). **빌드 끝 (2026-09-18). 7-review 대기.** P1~P9 모두 완료 조건 met, release-blocked 1건(아래 표). 이 기기에서 `measure/.venv`(kiwipiepy 0.23.2)는 설치돼 있고 커밋되지 않습니다.

## 이 단계가 따르는 것

| 문서 | 역할 |
|---|---|
| [`../3-spec/09_toolkit_spec.md`](../3-spec/09_toolkit_spec.md) | 구현 대상. **P1의 첫 커밋부터 고치지 않습니다** |
| [`../4-plan/10_plan.md`](../4-plan/10_plan.md) | 단계 P1~P9, 완료 조건, release-blocked 조건. 고치지 않습니다 |
| [`../5-preflight/flow.md`](../5-preflight/flow.md) | 미리 정한 결정 F1~F16, 단계별 흐름, 검증 run 형식, release-blocked 모음 |
| [`../../../AGENTS.md`](../../../AGENTS.md) | 판단, 서브에이전트, git, 셸 규칙 |

## 규칙

- **멈추지 않는다.** 멈출 이유였을 것은 되돌리기 싼 경로로 가면서 **release-blocked**로 기록합니다. 사용자에게 묻지 않습니다.
- **스펙과 계획을 고치지 않는다.** 달랐던 것, 몰랐던 것, 스펙이 정하지 않아 고른 것은 P 기록에 남기고 7-review로 넘깁니다.
- **P마다 커밋하고 P마다 기록한다.** 한 걸음에 커밋 하나, P의 마지막 커밋이 기록을 닫습니다.
- **완료 조건은 독립 검증 run이 확인한다** (`flow.md` §2 형식, `mid`, 상한 밖). 판정 원문을 기록에 그대로 붙입니다.
- **탐색 run은 P당 4회**(`large`는 2회로 셈). Codex `large`(`gpt-5.6-sol`)는 시대 02에서 측정하지 않았으므로(원인은 조사하지 않음) Claude Code `claude-opus-5`로 대신합니다 (F16).
- **비용 상한:** P8 $21, P9 $200 (F10). 실행마다 비용을 기록에 누적합니다.
- **실제 원문은 저장소에 넣지 않습니다.** 코퍼스와 레코드는 트리 밖 `KO_QUALITY_HOME`에, `tests/runs/P<n>/`에는 개수·해시·토큰·비용·합성 텍스트만 둡니다 (F14, 09 §20).

## 기록 형식

P마다 파일 하나: `P<n>_<이름>.md` (영어). 절은 이 순서로 둡니다.

```markdown
# P<n> — <name>
## Summary            3–5 lines: what was built, done-condition verdict, release-blocked count
## Built              | Item | Path | State |
## Decisions          | # | Grade (minor/major/structural) | Options (best / cheapest to reverse) | Chosen | Confidence | Basis (run #) |
## Subagent runs      | # | Tier | Purpose | Tokens | Verdict |
## Cost               | Run | Model | USD |   (running total against the step's ceiling)
## Differs from spec
## Spec did not know
## Verification       the verification run's answer, verbatim
## Release-blocked    | Condition | Evidence | Cheapest reverse taken | Resolve in review by |
```

## 진행 현황

P가 끝날 때마다 한 행을 채웁니다. 리뷰는 이 표에서 시작합니다.

| P | 이름 | 기록 | 완료 조건 판정 | release-blocked | 비용 | 마지막 커밋 |
|---|---|---|---|---|---|---|
| P1 | Distribution under B9 | [P1](P1_distribution.md) | met (4/4) | 0 | $1.14 | `639831a` |
| P2 | Logger | [P2](P2_logger.md) | met (5/5) | 0 | $0.92 | `5d15f70` |
| P3 | Self-application | [P3](P3_self-application.md) | met (3/3) | 0 | $0.36 | `3edac84` |
| P4 | Exclusion pass and `measure/` | [P4](P4_exclusion-and-measure.md) | met (3/3); 4 findings fixed in P5 | 0 | $0 | `edf5bfd` |
| P5 | Tier 0 | [P5](P5_tier0.md) | met (2/2); 3 notes carried to P6 | 0 | $0 | `cf3c2f7` |
| P6 | Tier 1 and Tier 2 | [P6](P6_tier1-tier2.md) | met (3/3) | 0 | $0 | `b1d7ded` |
| P7 | Eval split and judge Tier A | [P7](P7_eval-split-and-judge.md) | met (2/2) | 0 | $3.22 | `e49349e` |
| P8 | Corpus generator and pilot | [P8](P8_corpus-and-pilot.md) | met (4/4) | 0 | $12.87 | `9592171` |
| P9 | Sized batch and `watch:` candidates | [P9](P9_batch-and-watch.md) | met (3/3) | 1 (budget cap, underpowered) | $191.11 | P9 record |

### release-blocked 모음

| P | 조건 | 근거 | 택한 되돌리기 싼 경로 | 리뷰에서 정할 것 |
|---|---|---|---|---|
| P9 | 크기를 정한 배치가 예산 상한에 막힘 (10_plan.md P9) | 파일럿 기준 칸당 63세션 ≈ $229.5 > $200. 칸당 54세션으로 돌렸고 달성 검정력 0.738 (`tests/runs/02-P9/batch-01-summary.json`) | 상한이 허용한 크기로 실행하고 결과와 후보를 검정력 부족으로 표시. `watch:`는 아무것도 읽지 않음 | 검정력이 부족한 배치를 시대 02의 결과로 받을지, 상한을 올려 새 배치 id로 보충 배치를 돌릴지 |

리뷰가 먼저 볼 발견(각 P 기록의 "Spec did not know"): 정책이 영어 프롬프트에도 한국어로 답하게 함(P9), `phrase_battery`가 길이에 영향받는 원시 개수라는 점(P9), 형태소 분석기가 외래어 일반명사를 NNP로 태깅함(P6), 판정 도구가 이유를 내지 않음(P7), 헤드리스 stream-json 입력을 한꺼번에 넣으면 턴이 합쳐짐(P8), `ruleset` 규칙 수 115 → 136(P9).

## 빌드가 끝나면

1. 이 README의 진행 현황을 모두 채우고, release-blocked를 한 표로 모읍니다.
2. `design/README.md`와 시대 README의 현재 위치를 "6-build 끝, 7-review 대기"로 바꿉니다.
3. `master`에 머지하지 않습니다.

## 새 세션 시작 (handoff)

빌드는 **새 세션**에서 시작합니다. 저장소 루트에서 Claude Code를 띄우고 아래를 그대로 붙여 넣습니다.

```text
era 02 6-build를 시작한다. 사용자 수락: flow.md (2026-09-17).

먼저 읽기: AGENTS.md → design/README.md → design/02-validation/6-build/README.md
→ design/02-validation/4-plan/10_plan.md → design/02-validation/5-preflight/flow.md
→ design/02-validation/3-spec/09_toolkit_spec.md (필요한 절).

dev 브랜치에서 P1부터 P9까지 자율로 진행한다. 사용자에게 묻지 않고 멈추지 않는다.
판단은 AGENTS.md, 미리 정한 결정은 flow.md §1, 기록 형식은 6-build/README.md를 따른다.
P마다: flow.md §3 흐름 → 커밋 → 독립 mid 검증 run(flow.md §2) → P 기록 → README 진행 현황 한 행 → 커밋.
스펙(09)과 계획(10)은 고치지 않는다. 막히면 되돌리기 싼 경로 + release-blocked.
재개할 때는 6-build/README.md 진행 현황과 git log로 위치를 찾는다.
끝나면 6-build/README.md "빌드가 끝나면"을 따른다. master에 머지하지 않는다.
```

**시작 전에 확인할 것 (사용자)**
- 이 기기의 `.claude/settings.local.json`에 Codex hook trust 권한 규칙이 있다 (U4).
- **같은 파일에서 `outputStyle`을 직접 지운다** (F12). 빌드가 이 파일을 고치면 auto 모드 분류기에 막힐 수 있어서, 빌드는 이 파일에 손대지 않는다.
- 빌드 세션의 권한 모드. auto 모드 분류기가 막는 명령이 나오면 빌드는 release-blocked로 기록하고 계속 간다.
- P3 이후 새로 띄우는 세션은 `agent-reply` 스타일로 돌고 `~/.ko-quality-dev`에 기록을 남긴다 (F12). 이미 떠 있는 빌드 세션은 영향이 없다.
