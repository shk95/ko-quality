# 2-exploration — 현재 상태

> 이 단계의 문서 지도와 읽는 순서. **새 세션은 여기서 시작합니다.**
> 문서 본문은 영어, 이 README는 한국어입니다 (`AGENTS.md`).

**진행:** E1~E7 끝. 조사 의제는 전부 닫혔고 **다음은 `3-spec`** 입니다.

## 읽는 순서

| # | 문서 | 무엇을 정했나 |
|---|---|---|
| 1 | [`02_scope.md`](02_scope.md) | 이 시대의 범위. 레코드가 0건이라 **오프라인 코퍼스**로 가고 실사용 재측정은 시대 03이 받습니다. 의제 E2~E7, 그리고 B9(강제 없는 스타일)·E4의 `register`·E7의 자기 적용이 여기 붙어 있습니다 |
| 2 | [`03_features.md`](03_features.md) | **E2.** 규칙 209개 → 측정 28개, 3단(표준 라이브러리 / 형태소 / 입력+출력). 제외 패스가 모든 단의 전제 |
| 3 | [`04_judge.md`](04_judge.md) | **E3.** 판정기 기준선을 감쇠에서 유도. 이 시대는 `llm` 채점기 값을 **기록하지 않습니다** |
| 4 | [`05_approximations.md`](05_approximations.md) | **E4.** 06 §13.1 아홉 항목 + 셋. 삭제 0건 |
| 5 | [`06_ruleset_and_eval.md`](06_ruleset_and_eval.md) | **E5.** `ruleset` 보류, 케이스 형식, **러너 둘로 분리** |
| 6 | [`07_gate.md`](07_gate.md) | **E6.** gate는 가능. 팔을 `정책 × gate` 2×2로 나누면 둘 다 측정 가능 |
| 7 | [`08_scope_decisions.md`](08_scope_decisions.md) | **E7.** stop-slop-ko는 이 시대에 넣지 않고 `exempt`는 삭제. 원문 90일 보관. 이 저장소는 `agent-reply`를 **기본값으로** 자기 적용 |

급하면 1번과 각 문서의 "Handed to the spec" 절만 읽어도 3-spec에 필요한 것은 다 있습니다.

## 이 단계가 3-spec에 넘기는 것

**측정**

- feature 목록 28개와 3단 구성. **제외 패스를 가장 먼저 짓고 가장 먼저 검증**합니다 (E2)
- Tier 1 레시피 둘은 쓴 그대로면 깨집니다 — 후행 구두점 제거, 동사화된 체언을 분모에서 제외 (E2)
- `ko.preserve`는 지을 수 있고 **`ko.change_rate`는 절차가 없습니다** (E4 항목 8)
- 토큰은 추정하지 않고 생성기의 실제 usage를 씁니다 (E4 항목 6)

**판정**

- 기준 측정 **넷**(`사용자님`, `spelling_denylist`, `quote_balance`, `allomorph_errors`). 방향당 상한 10%, n ≈ 60~70, 구성된 집합 (E3)
- Tier A(루브릭 자기모순 1건이면 기각)를 가장 먼저 (E3)
- 판정된 텍스트·이유·판정기 모델을 반드시 남깁니다 (E3)

**구조**

- 로거에 `session_id` 추가 — 없으면 팔 라벨도 `sub_to_sub_present`도 붙일 곳이 없습니다 (E4)
- `policy_on`은 이름을 지키고 뜻을 되찾습니다. `plugin_present`를 추가 (E4)
- gate는 로거와 **별개 실행 파일** (E6)
- 러너 둘 — `claude plugin eval`은 발동·회귀, 측정은 우리 것 오프라인 (E5)

**실험 설계**

- 이 시대의 팔은 **A / B / C**(정책 끔·미선택·켬), gate는 전부 꺼져 있습니다
- gate 차원은 시대 03 이후. 그때 `정책 × gate` 2×2가 됩니다 (E6)
- **팔 B는 B9가 채택돼야 존재합니다.** 그리고 `policy_on`이 고쳐져야 B와 C가 구분됩니다

**범위 (E7)**

- stop-slop-ko는 lock에도 팔에도 넣지 않습니다. `exempt`는 되살릴 참조 대상이 원래 없었으므로 06 §6에서 **삭제**합니다
- 실제 원문은 커밋하지 않고, 판정기 사본도 `KO_QUALITY_HOME` 아래에 두며, `task`/`output`은 **90일**(월 파일 단위) 뒤 삭제합니다. 파생값은 만료되는 파일 밖에 저장합니다. 마스킹에 전화번호·주민등록번호·카드번호·홈 경로를 추가합니다
- 서브에이전트 레코드의 `injection_point`는 스탬프가 아니라 `agent_type`의 네임스페이스로 정합니다. 개발용 에이전트 이름은 배포 이름과 겹치지 않게 빌드 검사로 막습니다(가독성 규칙)
- 자기 적용을 **저장소 기본값**으로 켭니다. 그 전에 격리가 먼저입니다 — 로거 `expanduser`, 커밋되는 `.claude/settings.json`, 레코드의 프로젝트 표지(`cwd`의 git 루트 기준), 빌드 스탬프의 빌드 식별자. 마켓플레이스 등록과 로컬 스타일 제거는 커밋되지 않아 **기기마다 한 번** 해야 합니다

## 실측 기록

| 항목 | 파일 | 무엇을 확인했나 |
|---|---|---|
| E1 / B9 | [`02-E1/unforced-style-selection.json`](../../../tests/runs/02-E1/unforced-style-selection.json) | 강제 없는 스타일은 선택 가능하고 세션 중 전환되며 선택은 프로젝트에 남습니다 |
| E2 | [`02-E2/kiwipiepy-recipes.json`](../../../tests/runs/02-E2/kiwipiepy-recipes.json) | 태그셋 20개 전부 통과. 레시피 둘은 깨져 있었고 수정안까지 실측 |
| E4 | [`02-E4/approximations.json`](../../../tests/runs/02-E4/approximations.json) | `subagent_stats`로 중첩 관측 가능. 토큰 비율은 내용에 따라 4배 범위 |
| E5 | [`02-E5/eval-grader-types.json`](../../../tests/runs/02-E5/eval-grader-types.json) | 채점기 타입 여섯, `regex`는 존재 매칭만, 코드 채점기 없음 |
| E6 | [`02-E6/stop-hook-gate.json`](../../../tests/runs/02-E6/stop-hook-gate.json) | Stop hook이 답변을 되돌립니다. 하네스가 8회에서 끊고 **빈 결과**를 돌려줍니다 |
| E7 | [`02-E7/agent-scope-and-visibility.json`](../../../tests/runs/02-E7/agent-scope-and-visibility.json) | `--scope local`은 가시성을 제한합니다. "프로젝트 에이전트가 우선"은 뒤의 리뷰에서 **공존**으로 바로잡혔습니다. **E7 문서보다 먼저 나온 기록입니다** |
| E7 | [`02-E7/settings-env-isolation.json`](../../../tests/runs/02-E7/settings-env-isolation.json) | 프로젝트 설정의 `env`가 플러그인 hook까지 닿아 로거 홈을 격리합니다. 단 `settings.local.json`은 커밋되지 않습니다 |
| E7 | [`02-E7/committed-settings-and-agent-names.json`](../../../tests/runs/02-E7/committed-settings-and-agent-names.json) | 커밋 설정의 `env`는 닿지만 `~`는 풀리지 않습니다. 마켓플레이스는 커밋되지 않고, 로컬 스타일이 커밋 스타일을 이깁니다. 설정은 실행 디렉터리에서만 읽힙니다. 에이전트는 이름이 달라 공존합니다 |

`02-E7`의 첫 기록이 `08_*.md`보다 앞서 있는 것은 그 실측이 E2 단계에서 제기된 질문을 따라가다 나왔기 때문입니다. E7 문서를 쓸 때 입력으로 씁니다.

## 서브에이전트 실행

이 단계 누계 **11회** (`mid` 10, `docs` 1). `docs`는 `mid`와 같게 셉니다 (시대 01 리뷰 §E).

| # | 목적 | 티어 | 토큰 |
|---|---|---|---|
| E2-a | ko-diagnose 참조 분류 | mid | 81.7k |
| E2-b | ko-grammar 참조 분류 | mid | 83.4k |
| E2-c | 에이전트 정의 위치와 `--scope` | docs | 39.7k |
| E2-v | kiwipiepy 태그셋과 레시피 실행 | mid | 85.4k |
| E3-v | E3 초고 통계 검증 | mid | 82.5k |
| E3-v2 | 기준 측정 후보 검증 + `ko.change_rate` 대응 | mid | 101.2k |
| E4-v | E4 처분 검증 | mid | 88.2k |
| E5-v | E5 러너·`ruleset` 검증 | mid | 121.2k |
| E6-v | E6 gate 검증 | mid | 112.6k |
| E7-v | E7 결정 문서 검증 | mid | 92.8k |
| E7-v2 | E7 확신 낮은 하네스 주장 실측 | mid | 105.2k |

각 문서의 `## Subagent runs` 절이 그 문서가 쓴 실행만 적고, 누계는 여기입니다.

## 이 단계가 배운 것 (3-spec이 아니라 절차에 대한 것)

**일곱 의제 전부에서, 문서가 옳다고 적어둔 것이 실제로는 달랐습니다.**

| 의제 | 읽어서는 알 수 없었던 것 |
|---|---|
| E2 | 태그셋은 맞았는데 **레시피가 깨져** 있었습니다. `noun_ending_ratio`는 모든 글에 100% 발동했습니다 |
| E3 | 판정기는 노이즈가 아니라 **일관되게** 틀렸고, `--runs`는 판정 횟수가 아니었습니다 |
| E4 | 토큰 추정치가 내용에 따라 4배로 흔들렸고, `session_id`가 **아예 없었습니다** |
| E5 | `regex` 채점기가 **있었습니다** — 없다고 가정하고 설계할 뻔했습니다 |
| E6 | 하네스가 **상한을 겁니다**. 제 프로브가 상한 아래에서 멈춰 "없다"고 썼습니다 |
| E7 | 되살릴 `exempt`의 규칙 id가 upstream에 **처음부터 없었습니다**. 격리 설정은 동작했지만 커밋되지 않는 파일에서만 동작했습니다 |

아홉 번의 검증 실행 중 **결론을 뒤집은 것은 없고, 근거를 바꾼 것은 전부**입니다. 그리고 근거가 바뀔 때마다 스펙에 들어갈 문장이 달라졌습니다.

**`AGENTS.md` 후보 한 줄.** 시대 01의 리뷰 §D가 heredoc 규칙을 그렇게 더했듯이, 이 단계도 규칙 하나를 벌었습니다 — **하네스의 동작을 설계 문서에 쓰기 전에 한 번 돌려 본다.** 문서가 말하는 것과 도구가 하는 것은 달랐고, 여섯 번 다 그랬습니다. 규칙은 리뷰에서 더하는 것이라 여기서는 후보로만 적어 둡니다.
