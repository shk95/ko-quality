# 03. 엔진 개념: 에이전트가 호출하는 기능 단위

> 단계 문서. 스택을 "에이전트에게 제공되는 기능"으로 다시 짠 결과.

## 형태: MCP 서버 하나

MCP의 세 primitive가 스택의 세 종류 계층과 대응한다. 이 대응이 엔진의 형태를 결정했다.

| 스택 계층 | MCP primitive | 에이전트가 받는 것 |
|---|---|---|
| L3 gate, feature, 변경률, 보존 검사 | **tools** | 실행 결과(JSON + pass/fail) |
| taxonomy, policy 블록, 프로파일 | **resources** | 필요할 때 읽는 참조 문서 |
| L0 policy, L1 rewrite, L2 diagnose 지시문 | **prompts** | 자기 컨텍스트에 넣을 지시 텍스트 |

MCP를 고른 이유는 Claude Code, Codex, Cursor, 직접 만든 하네스가 전부 MCP를 말하기 때문이다. "기능으로 제공"의 최소공통분모다. MCP가 없는 환경에는 같은 것을 CLI + SKILL.md 쌍으로 노출하고, 엔진 코드는 동일하다.

## 실행 주체의 분리

가장 중요한 설계 결정.

- **LLM이 필요한 단계(L0·L1·L2)는 엔진이 직접 실행하지 않고 지시문을 반환한다.** 호출한 에이전트가 자기 모델로 실행한다.
- **결정론적 단계(L3)만 엔진이 직접 실행한다.**

이렇게 갈라야 엔진이 모델·하네스에 독립적이면서, "모델이 괜찮다고 주장하는 것"과 "도구가 확인한 것"이 응답 안에서 구조적으로 분리된다.

## 인터페이스

단계마다 입출력 계약을 하나로 통일한다. 단계를 빼고 넣고 순서를 바꿔도 조합이 되게 하기 위해서다.

```text
Request  { text, profile, stages[], options{register, intensity, voice?} }
Response { text', report{stage→result}, pass, next }
```

노출하는 단계:

```text
policy    (prompt)       → 프로파일에 맞는 정책 텍스트. 생성 방향 진입점
selfcheck (prompt+tool)  → "출력 직전 gate를 호출하고 실패하면 고쳐라" 지시 + gate 도구
rewrite   (prompt)       → im-not-ai 절차 지시문 + taxonomy resource 링크
grammar   (prompt)       → 맞춤법·띄어쓰기 지시문
diagnose  (prompt)       → 수정 없이 신호 보고. yoonmoon detect
gate      (tool)         → lint / preserve / change_rate / features → pass/fail
```

프리셋:

```text
quick    = [gate]
standard = [policy, gate]
review   = [diagnose, gate]
edit     = [rewrite, grammar, gate]
full     = [policy, rewrite, grammar, diagnose, gate]
```

## 두 방향의 적용

### 생성 방향 — 프롬프트·사고에 적용

오케스트레이터가 서브에이전트를 띄울 때 `policy(profile)`를 호출해 반환된 텍스트를 서브에이전트의 system prompt에 넣는다. fluent-korean의 서브에이전트 조항이 하던 일을 엔진이 프로파일별로 대신한다.

`selfcheck`를 붙이면 서브에이전트가 산출물을 내기 직전에 `gate` 도구를 스스로 호출하고 실패 항목을 고친 뒤 내보낸다. fluent-korean README의 "출력 직전 점검" 블록은 모델의 자기 점검이라 검증이 안 되지만, `selfcheck`는 도구 호출 결과가 남으므로 검증이 된다.

사고에 대한 적용의 한계: extended thinking 내용을 직접 통제하는 수단은 없다. "한국어로 사고하라"는 지시를 system prompt에 넣는 것까지가 전부다. 다만 "저품질 한국어가 추론에 영향을 준다"는 fluent-korean의 가설은 같은 policy를 넣고 뺀 조건에서 gate 수치와 작업 성공률을 함께 재면 검증할 수 있고, 엔진은 이 실험을 바로 지원한다.

### 검토 방향 — 서브에이전트에게 위임

리뷰어 서브에이전트 정의를 엔진이 템플릿으로 제공한다.

```yaml
name: korean-reviewer
tools: [ko.gate, ko.features]
system: |
  {{ ko.prompt("policy", profile) }}
  {{ ko.prompt("diagnose") }}
  절차: diagnose → ko.gate 호출 → report 형식으로만 반환.
  산문 평가는 report의 notes 필드에만 쓴다.
```

오케스트레이터는 리뷰어의 산문이 아니라 **report의 pass 필드**를 보고 산출물을 받을지 결정한다. 리뷰어가 "자연스럽습니다"라고 써도 gate가 fail이면 거부된다. 같은 방식으로 `korean-editor`(rewrite+grammar+gate)를 두면 "검토만" / "수정까지"가 역할로 분리된다.

## 오케스트레이션 흐름

```text
orchestrator
  ├─ spawn writer      ← system += ko.policy(profile)
  │     └─ draft.md
  ├─ spawn reviewer    ← preset=review
  │     └─ report{pass:false, findings:[…]}
  ├─ spawn editor      ← preset=edit, input=draft+findings   (최대 N회)
  │     └─ draft'.md + report{change_rate:0.21, pass:true}
  └─ accept if report.pass
```

각 단계가 같은 report를 append하므로 최종 산출물에는 "어떤 정책 해시로 생성 → 어떤 신호가 잡혔고 → 몇 % 바뀌어 → 어떤 gate를 통과했는가"가 남는다. 서브에이전트 결과를 믿지 않고 artifact + provenance로 판단한다는 원칙이 엔진 계약 자체에 들어가 있다.

## 보증하는 것과 못 하는 것

- **보증하는 것**: report의 정확성. gate 수치, 변경률, 보존 검사, 어느 정책이 주입됐는지의 기록.
- **보증 못 하는 것**: 산문의 품질 자체. rewrite와 diagnose는 호출자 모델이 실행하므로 모델이 바뀌면 결과가 바뀐다. 엔진은 이 변화를 **감지**(같은 eval을 새 모델로 돌려 report 델타를 봄)할 수 있을 뿐 막지는 못한다.

## 컨텍스트 비용이라는 제약

서브에이전트마다 taxonomy 전체를 넣으면 priming 희석이 그대로 재현된다. prompt는 절차와 원칙만 짧게 주고, 패턴 목록은 resource로 두어 필요할 때만 읽게 한다. im-not-ai가 진단·윤문·finalizer를 별도 에이전트로 나눈 것도 같은 이유이고, 엔진의 역할 분리(reviewer/editor)가 그것을 흡수한다.

## 한 줄 정의

엔진은 "한국어 품질을 만들어주는 것"이 아니라 **한국어 품질에 관한 정책 주입·검증·기록을 에이전트가 호출 가능한 기능으로 표준화한 것**이다. 그 범위 안에서는 모듈처럼 단계별로 붙였다 뗐다 할 수 있고, 하네스를 바꿔도 계약이 유지된다.

## 이 단계에서 남긴 선택

에이전트 정의를 Claude Code 형식으로 만들 것인가, 하네스 중립 템플릿으로 만들 것인가. → 하네스 중립으로 결정(`03a_findings_decisions.md`).
