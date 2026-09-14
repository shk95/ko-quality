# 02. 스택 구상: 다섯 층

> 단계 문서. 조사 결과를 조합해 "무엇을 어느 순서로 쌓는가"를 정한 시점.

## 원칙

1. **rewrite taxonomy는 하나만.** 나머지 프로젝트는 평가용·참고용으로만 쓴다.
2. **LLM 판정과 결정론적 판정을 분리한다.** 프롬프트 층의 한계 효용은 작다(stop-slop-ko 5:5). 스크립트로 잡히는 것은 스크립트로 내린다.

## 구조

```text
L0  생성 시점 policy      fluent-korean (output-style)
                         + stop-slop-ko 생성 모드에서 차이가 난 3규칙만 append
        ↓
L1  산출물 rewrite        im-not-ai (route_hint → diagnosis → rewrite → finalize)
                         + korean-skills grammar-checker (맞춤법·띄어쓰기)
        ↓
L2  LLM 진단 (수정 없음)  yoonmoon detect  또는  korean-writing-reviewer evaluate
        ↓
L3  결정론적 gate         korean-report-skills lint.py
                         + katfishnet feature (쉼표율·POS 다양성 baseline)
                         + 변경률 diff (30% 경고 / 50% 중단) 스크립트화
                         + 숫자·고유명사·인용 보존 검사
                         → exit code로 PASS/FAIL (son-writer-skill 방식)
        ↓
L4  eval harness          stop-slop-ko evals.json / trigger_eval.json 포맷
                         with/without A/B + 블라인드 채점
```

## 각 층

### L0 — 생성 시점 policy

fluent-korean은 문법적 완결성(조사·어미 복원, 전보체 방지)을, stop-slop-ko 생성 모드는 공허한 표현(단정 회피, 양비론)을 막는다. 겨냥하는 결함이 달라 겹치지 않는다.

배치: output-style. 단, output-style은 매 세션 토큰이 들고 priming 희석의 원인이 되므로 stop-slop-ko는 전체가 아니라 벤치마크에서 차이가 난 세 패턴만 넣는다. 서브에이전트가 한국어 프롬프트를 주고받는 하네스라면 서브에이전트 정의에도 같은 텍스트를 넣어야 fluent-korean이 지적한 단계별 누적을 막는다.

### L1 — 산출물 rewrite

엔진은 im-not-ai로 고정한다. k-skill과 yoonmoon이 이 방법론에서 파생됐다는 점에서 가장 검증됐고, route_hint 사전 채점과 변경률 gate가 이미 있어 L3와 인터페이스가 맞는다.

호출 시점: 매 응답이 아니라 **산출물 경계**(문서 파일 생성, 최종 보고)에서만. 맞춤법은 문체와 별개 문제라 korean-skills grammar-checker를 뒤에 붙인다.

### L2 — 수정하지 않는 진단

rewrite 결과를 rewrite 모델이 "괜찮다"고 하는 순환을 끊기 위한 층. yoonmoon detect는 signal 표를, korean-writing-reviewer는 점수와 재평가를 낸다. 둘 중 하나면 충분하고, 진단 결과는 L3 threshold의 입력이 된다.

### L3 — 결정론적 gate

"artifact + provenance + verification"의 실체. son-writer-skill의 fail-closed 아이디어를 가져오되 gate 항목은 위 도구들로 채운다.

- katfishnet feature는 탐지기가 아니라 **before/after 수치 baseline**으로 쓴다.
- 변경률 검사는 im-not-ai 프롬프트 안의 invariant를 스크립트로 옮긴다. 모델이 "30% 이내"라고 주장하는 게 아니라 diff가 계산한다.
- Claude Code라면 Stop hook이나 Write 직전 hook에 걸어 exit code 0이 아니면 산출물을 내보내지 않는다.

### L4 — eval harness

새 규칙을 L0/L1에 추가하기 전 반드시 통과하는 관문. stop-slop-ko의 evals.json은 레지스터별 면제/발동 쌍, 정보 보존·줄표 임계 회귀 검증까지 포함해 템플릿으로 바로 쓸 수 있다. 채점자를 생성 모델과 다른 모델로 두면 자기참조 문제를 일부 완화한다.

## 선택 계층

- **voice profile**: personal-humanizer-maker로 개인 스타일 skill을 컴파일해 L1의 voice 입력으로 쓴다. L0·L1과 충돌할 수 있어 L4로 측정한 뒤에 넣는다.
- **토큰 측정**: scrooge-mode의 측정 방식을 빌려 L0 적용 전후 출력 토큰과 claim 보존율을 잰다.

## 최소 구성

L0(fluent-korean만) + L3(lint.py + 변경률 diff + 숫자 보존) + L4. L1·L2는 L4에서 "L0만으로 안 잡히는 결함"이 실제로 측정된 뒤에 추가한다. 프롬프트를 쌓아 올리는 것보다 검증 우선 원칙에 맞다.

## 배치 요약

| 층 | 놓이는 곳 | 실행 주체 | 호출 시점 |
|---|---|---|---|
| L0 | output-style / CLAUDE.md / 서브에이전트 정의 | 모델 (priming) | 세션 내내 |
| L1 | skill | 모델 | 산출물 경계 |
| L2 | skill | 모델 | 산출물 경계 |
| L3 | hook / 스크립트 | 스크립트 | 산출물 경계 |
| L4 | CI / 로컬 runner | 스크립트 + 다른 모델 | 규칙 변경 시 |

## 이 시점의 한계

이 구상은 "무엇을 쌓는가"에는 답하지만 "어떻게 재사용하는가"에는 답하지 않는다. 다음 단계에서 재사용성을 정의하려다 이 구상의 형태 자체가 바뀐다.
