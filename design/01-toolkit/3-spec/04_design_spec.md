# 04. 설계 스펙: ko-quality (검증 엔진 안)

> 단계 문서. 앞 단계의 결정을 전부 반영한 상태.
>
> **상태: 보류.** 이 스펙은 "LLM 층을 신뢰하지 않고 report만 보증한다"는 전제 위에 있다. 이후 전제가 "upstream을 신뢰하고 사용성을 우선한다"로 바뀌면서(→ `04a_findings_premise.md`) 구현 대상은 `05_composition_spec.md`가 됐다. 이 문서는 나중에 검증을 추가할 때의 목표 형태로 남긴다.
>
> **두 항목은 05로 내려갔다.** §6의 `ko.features`와 §12의 버전 고정은 판정 장치가 아니라 측정 장치라서 05에서 먼저 구현한다(→ `05a_findings_measurement.md`). 나머지(gate, report.pass, eval runner, baseline)는 이 문서에 그대로 있다.
>
> **§8의 threshold는 05에서 `watch:`로 먼저 산다.** 05의 profile은 같은 형식의 `watch:` 절을 두어 threshold를 적되 판정하지 않고 레코드에 표시만 한다. 그래서 이 문서의 `gate:`로 승격할 때는 절을 새로 쓰는 게 아니라 **검증된 값의 키 이름을 바꾼다.** §8.1이 "threshold는 비워두고 stage 0 측정 뒤 채운다"고 한 그 측정을 05의 로거가 미리 해둔다.

## 1. 목적과 범위

**목적.** 한국어 품질에 관한 정책 주입·검증·기록을 에이전트가 호출 가능한 기능으로 표준화한다.

**범위.**
- 정책 텍스트의 프로파일별 합성과 반환
- 결정론적 검증(gate)의 직접 실행
- rewrite / grammar / diagnose 지시문의 반환
- 모든 단계가 공유하는 report 계약
- 하네스 중립 에이전트 템플릿과 하네스별 adapter
- with/without eval

**비범위.**
- 산문 품질 자체의 보증 (LLM 단계는 호출자 모델이 실행)
- 사고(extended thinking) 내용의 직접 통제
- 업스트림 taxonomy의 편집 (vendor는 수정 금지)
- voice profile (stage 5로 보류)

## 2. 중립성 규약

1. `core/`, `stages/`, `agents/`, `policy-blocks/`, `profiles/`에는 하네스 이름이 등장하지 않는다.
2. 프롬프트는 도구 호출 문법 대신 capability 이름(`ko.gate` 등)만 언급한다.
3. 템플릿 변수는 `{profile}`, `{intensity}`, `{findings}`로 제한한다.
4. adapter는 렌더링만 한다. 허용: 형식 변환, capability→도구명 매핑, 정책 주입 지점 배치, hook 배선. 금지: 프롬프트 수정, threshold 변경, 단계 추가.
5. 규약 4는 테스트로 강제한다: 같은 profile에 대해 모든 adapter 출력의 `policy_hash`가 동일해야 한다.

## 3. 디렉터리

```text
ko-quality/
├── core/
│   ├── request.schema.json
│   ├── report.schema.json
│   ├── finding.schema.json
│   ├── profile.schema.json
│   ├── agent.schema.json
│   └── category_map.yaml
├── stages/
│   ├── policy/
│   ├── selfcheck/
│   ├── rewrite/
│   ├── grammar/
│   ├── diagnose/
│   └── gate/
│       ├── stage.yaml
│       ├── prompt.md          # kind: prompt 만
│       ├── run.py             # kind: tool 만
│       ├── resources/
│       └── evals/
├── capabilities/              # gate가 조합하는 원자 도구
│   ├── features.py            # 쉼표율, POS 다양성, 문장 완결성, 조사 부재율, 영어 비율
│   ├── change_rate.py
│   ├── preserve.py
│   ├── lint.py                # korean-report-skills 규칙 wrapper
│   └── spell.py               # hanspell / hunspell wrapper
├── policy-blocks/
│   ├── fluent-korean.core.md
│   ├── slop.three-rules.md
│   ├── honorific.md
│   ├── subagent-propagation.md
│   ├── think-in-korean.md
│   └── _meta.yaml
├── profiles/
│   ├── agent-reply.yaml
│   ├── formal-report.yaml
│   ├── tech-doc.yaml
│   └── chat-casual.yaml
├── presets/presets.yaml
├── agents/
│   ├── writer.yaml
│   ├── reviewer.yaml
│   └── editor.yaml
├── baselines/
│   ├── _schema.yaml
│   ├── personal.jsonl         # 사용자 제공
│   └── public.jsonl           # 공개 말뭉치 (선택)
├── transports/
│   ├── mcp/
│   ├── cli/
│   └── python/
├── adapters/
│   ├── generic/
│   ├── claude-code/
│   ├── codex/
│   └── cursor/
├── vendor/
│   ├── im-not-ai/
│   ├── korean-skills/
│   ├── yoonmoon/
│   ├── korean-report-skills/
│   ├── katfishnet/
│   └── vendor.lock
└── evals/
    ├── cases/
    ├── runner.py
    └── judge.yaml
```

## 4. core 스키마

### 4.1 request

```yaml
text: string                        # 필수
profile: string                     # profiles/ 의 id
stages: [string]                    # preset과 배타
preset: quick|standard|review|edit|full
options:
  register: string?                 # profile 기본값 덮어쓰기
  intensity: conservative|default|aggressive   # 기본 default
  voice: path?                      # stage 5 전까지 무시
  findings: [finding]?              # editor 입력
```

### 4.2 report

모든 경계를 넘는 유일한 데이터. 단계가 append한다.

```yaml
artifact: string                    # 파일명 또는 "inline"
profile: string
policy_hash_claimed: string?        # writer가 echo한 값. 검증된 값이 아님
stages:
  - stage: string
    kind: prompt | tool
    executed_by: model | engine     # 항상 기록
    result: object                  # 단계별 자유 형식 (아래 §5 참조)
    pass: bool | null               # tool만 값. prompt는 항상 null
    notes: string?                  # 모델의 산문 평가는 여기에만
pass: bool                          # tool 단계 pass의 AND. warning은 영향 없음
warnings: [string]
```

규칙: prompt 단계는 `pass`를 주장할 수 없다. 최종 `pass`는 tool 단계만 결정한다. 오케스트레이터는 `notes`를 판단 근거로 쓰지 않는다.

### 4.3 finding

diagnose가 내고 rewrite가 받는 중립 형식.

```yaml
span: {start: int, end: int}        # 형태소 오프셋
category: string                    # diagnose taxonomy의 범주 id
severity: S1 | S2 | S3
evidence: string                    # 짧게. 원문 재인용 아님
mapped_category: string?            # category_map 적용 후 rewrite taxonomy 범주
```

### 4.4 profile

```yaml
id: string
register: string
blocks: [string]                    # policy-blocks/ 의 id 순서대로
default_preset: string
on_final_fail: block | emit_with_flag   # 필수. 상속 불가
gate:
  change_rate: {warn: float, fail: float}
  lint_ruleset: string
  spelling: warn | fail
  spelling_backend: hanspell | hunspell
  preserve: [numbers, proper_nouns, code, paths, urls, quotes]
  length_growth: {warn: float}      # policy-off 대비 증가율
  features:                         # baseline 대비 threshold. §8 참조
    noun_ending_ratio: {fail: float}
    particle_absence_ratio: {fail: float}
    english_ratio: {warn: float}
baseline: personal | public         # baselines/ 파일 선택
exempt: [string]                    # 면제 규칙 id
```

### 4.5 agent

```yaml
name: string
role: string
preset: string?
capabilities: [string]              # ko.* 이름
prompt:
  compose: [string]                 # policy-blocks 또는 stages/*/prompt.md 경로
  append: string?
output_contract: core/report.schema.json
echo: [policy_hash_claimed]?        # writer만
```

### 4.6 category_map.yaml

```yaml
# diagnose 범주 → rewrite 범주. 다대일 허용
translationese:        [im.particle_calque, im.inanimate_subject, im.pronoun_literal]
passive_overuse:       [im.double_passive, im.by_agent]
hedging_cliche:        [im.hedge_ending, im.closing_cliche]
mechanical_structure:  [im.enumeration, im.uniform_sentence]
...
```

## 5. 스테이지 규약과 정의

### 5.1 공통 규약

```yaml
# stages/<id>/stage.yaml
id: string
kind: prompt | tool | prompt+tool
requires_capabilities: [string]
inputs:  [string]
outputs: [string]
resources: [path]                   # 프롬프트에 인라인하지 않음
upstream: vendor/<name>@<commit>?
```

prompt.md 작성 규칙: 절차와 원칙만. 패턴 목록은 resources로. 100줄 이내. capability 이름 외 도구 문법 금지.

### 5.2 policy (prompt)

- inputs: profile
- outputs: text(정책 텍스트), result{policy_hash, blocks}
- 동작: profile.blocks 순서로 policy-blocks를 이어 붙이고 sha256을 policy_hash로. 렌더는 결정론적.
- 블록 `subagent-propagation`은 "한국어로 서브에이전트에 프롬프트를 줄 때 이 정책을 함께 넘긴다"는 조항.

### 5.3 selfcheck (prompt+tool)

- requires: ko.gate
- 지시: 산출물을 내기 직전 ko.gate를 호출한다. fail이면 실패 항목만 고쳐 재호출한다. 최대 `N=2`. 그래도 fail이면 profile.on_final_fail을 따른다.
- result{attempts, final_pass}

### 5.4 rewrite (prompt)

- upstream: vendor/im-not-ai
- inputs: text, profile, findings?
- outputs: text', result{change_rate_claimed, spans_touched}
- 절차: route 판정(light/standard/heavy) → 진단 → span 단위 수정 → finalize.
- invariant(프롬프트에 명시): 의미 보존, 탐지 span만 수정, 장르 보존, 숫자·고유명사·인용 불변, **신호가 둘 이상 겹칠 때만 수정**(hjongc 원칙), 변경률 30% 초과 시 중단하고 보고.
- resources: `resources/taxonomy.md`(im-not-ai 패턴 표). diagnose taxonomy는 로드하지 않는다.

### 5.5 grammar (prompt)

- upstream: vendor/korean-skills grammar-checker
- requires: ko.spell
- 절차: ko.spell로 후보를 받는다 → 고유명사·식별자·경로·외래어 후보는 기각 → 나머지 적용 → result{applied[], rejected[]}.

### 5.6 diagnose (prompt)

- upstream: vendor/yoonmoon detect
- outputs: result{findings[], ai_likelihood, confidence}
- 규칙: 텍스트를 수정하지 않는다. finding.schema 형식으로만 낸다. 산문 평가는 notes.
- resources: `resources/taxonomy.md`(yoonmoon 10대 분류). rewrite taxonomy는 로드하지 않는다.

### 5.7 gate (tool)

- executed_by: engine
- 조합: features + change_rate + preserve + lint + spell
- outputs: result{checks{…}, spelling{count, items, unavailable}}, pass
- pass = preserve ∧ change_rate<fail ∧ lint(fail 등급) ∧ features(fail 등급). spelling과 length_growth는 warning.
- exit code: 0 pass / 1 fail / 2 엔진 오류.

## 6. capabilities

| 이름 | 입력 | 출력 | 비고 |
|---|---|---|---|
| ko.features | text, baseline | {comma_rate, pos_ngram_diversity, noun_ending_ratio, particle_absence_ratio, english_ratio, sentence_len_var} + baseline 대비 z | kiwipiepy. 코드 블록·경로는 제외 후 계산 |
| ko.change_rate | before, after, preserve_spans | ratio | 형태소 단위. 보존 span은 분모 제외 |
| ko.preserve | before, after, kinds | {violations[]} | 숫자·고유명사·코드·경로·URL·인용 추출 후 집합 비교 |
| ko.lint | text, ruleset | {violations[{line, col, rule, level}]} | korean-report-skills 규칙 wrapper. `--fix`는 노출하지 않음 |
| ko.spell | text, backend | {items[], unavailable} | 해시 캐시. 타임아웃 시 unavailable |
| ko.gate | text, profile, before? | report 단계 1개 | 위 다섯의 조합 |

## 7. presets

```yaml
quick:    [gate]
standard: [policy, gate]
review:   [diagnose, gate]
edit:     [rewrite, grammar, gate]
full:     [policy, rewrite, grammar, diagnose, gate]
```

승격 규칙(stage 활성화): 새 단계나 블록을 preset에 넣으려면 evals에서 with/without 델타가 0 이상이어야 한다.

## 8. profiles

### 8.1 agent-reply (첫 profile)

```yaml
id: agent-reply
register: 에이전트가 사용자에게 하는 보고·설명
blocks: [fluent-korean.core, slop.three-rules, subagent-propagation]
default_preset: standard          # policy + gate. selfcheck는 writer 템플릿이 붙임
on_final_fail: emit_with_flag
gate:
  change_rate: {warn: 0.30, fail: 0.50}
  lint_ruleset: korean-report-skills/light
  spelling: warn
  spelling_backend: hanspell
  preserve: [numbers, code, paths, urls]
  length_growth: {warn: 0.40}
  features:
    noun_ending_ratio:       {fail: <stage0 측정 후>}   # 종결어미 없이 명사구로 끝나는 문장 비율
    particle_absence_ratio:  {fail: <stage0 측정 후>}   # 명사 뒤 조사 부재 비율
    english_ratio:           {warn: <stage0 측정 후>}   # 코드·경로 제외
baseline: personal
exempt: [slop.cta_in_sns, slop.polite_email_ending]
```

threshold는 비워두고 stage 0(policy 없이 gate만) 측정 뒤 채운다.

### 8.2 formal-report (두 번째)

- blocks에 `honorific` 추가, `subagent-propagation` 제외
- default_preset: full
- on_final_fail: block
- lint_ruleset: korean-report-skills/full (어미 일관성, 제목 명사구 등)
- spelling: fail + allowlist
- preserve에 quotes, proper_nouns 추가
- rewrite 경로가 중심. gate 구성이 agent-reply와 거의 겹치지 않음을 확인하는 용도.

## 9. agents

### writer.yaml

```yaml
name: korean-writer
role: 정책을 받아 산출물을 생성한다
capabilities: [ko.gate]
prompt:
  compose: [stages/policy, stages/selfcheck]
echo: [policy_hash_claimed]
output_contract: core/report.schema.json
```

### reviewer.yaml

```yaml
name: korean-reviewer
role: 산출물을 수정하지 않고 진단·검증한다
preset: review
capabilities: [ko.gate, ko.features]
prompt:
  compose: [policy-blocks/fluent-korean.core, stages/diagnose/prompt.md]
  append: 반환은 report 형식으로만 한다. 산문 평가는 notes에만 쓴다. 텍스트를 고치지 않는다.
output_contract: core/report.schema.json
```

### editor.yaml

```yaml
name: korean-editor
role: finding을 받아 span 단위로 수정하고 검증한다
preset: edit
capabilities: [ko.gate, ko.spell, ko.change_rate]
prompt:
  compose: [policy-blocks/fluent-korean.core, stages/rewrite/prompt.md, stages/grammar/prompt.md]
  append: 입력된 findings의 span 밖은 건드리지 않는다.
output_contract: core/report.schema.json
```

오케스트레이터 계약: 산출물 수락 여부는 `report.pass`로만 결정한다. `notes`와 `policy_hash_claimed`는 참고 정보다.

## 10. transports

| transport | 노출 |
|---|---|
| mcp | tools: ko.* / resources: policy-blocks, taxonomies, profiles / prompts: policy, selfcheck, rewrite, grammar, diagnose |
| cli | `ko-quality run --profile P --preset X file`, `ko-quality prompt <stage> --profile P`, `ko-quality gate file` |
| python | `ko_quality.run(request) -> response`, `ko_quality.prompt(stage, profile) -> str` |

세 transport는 같은 `core` 함수를 부른다. 로직은 transport에 없다.

## 11. adapters

| adapter | agent.yaml → | policy → | hook |
|---|---|---|---|
| generic | system prompt 문자열 + capability 표 | 문자열 | 없음 |
| claude-code | `agents/<name>.md` (frontmatter tools = MCP 도구명) | `output-styles/<profile>.md` 또는 CLAUDE.md 절 | Stop, PreToolUse(Write) → ko.gate |
| codex | AGENTS.md 절 | AGENTS.md 상단 | wrapper 스크립트 |
| cursor | rules 파일 | rules 상단 | 없음 |

adapter 테스트: 같은 profile에 대해 네 adapter 출력의 policy_hash 동일.

## 12. vendor

- 각 업스트림을 커밋 고정으로 복사. `vendor.lock`에 name, url, commit, license, 사용 파일 목록.
- 수정 금지. 필요한 변경은 `stages/*/prompt.md`나 `capabilities/`에서 한다.
- 커밋을 올릴 때는 evals를 돌려 델타를 확인한 뒤에만.
- 라이선스: 전부 MIT. `_meta.yaml`과 `vendor.lock`에 attribution.

## 13. evals

### 13.1 케이스 형식 (stop-slop-ko 포맷 확장)

```yaml
id: string
profile: string
register: string
input: string                       # 또는 task(생성 과제)
expect:
  gate_pass: bool
  preserve: [string]                # 반드시 살아 있어야 하는 토큰
  max_change_rate: float?
  must_not_contain: [string]?       # slop 패턴
  trigger: bool?                    # 단계가 발동해야 하는가 (면제 케이스)
```

### 13.2 runner

- 매트릭스: profile × preset × 모델 × {with, without}
- 측정: gate 통과율, 항목별 위반 수, change_rate, 출력 토큰 증가율
- 판정이 필요한 항목은 `judge.yaml`의 모델로 블라인드 채점. 생성 모델과 다른 모델.
- 결과는 `evals/results/<date>.json`. 승격 규칙의 입력.

### 13.3 자기참조 완화

- judge 모델 ≠ 생성 모델
- 케이스 일부에 사람 라벨을 두고 judge 일치율을 함께 기록

## 14. 구현 순서

```text
S0  core 스키마 4개 + category_map 빈 파일
S1  capabilities: features, change_rate, preserve  (kiwipiepy)
S2  gate 스테이지 + cli transport                   ← 여기서 stage 0 측정 가능
S3  policy 스테이지 + policy-blocks + agent-reply profile
S4  reviewer 에이전트 + generic adapter
S5  mcp transport
S6  evals runner + 빈 케이스 → 사용자 로그로 채움 → threshold 확정
S7  rewrite / grammar / diagnose 스테이지 + editor + writer
S8  claude-code adapter
S9  formal-report profile
```

S2까지가 stage 0(policy 없이 gate만) 측정의 최소 조건이다. 사용자 재료(글 샘플, 세션 로그)는 S6에서 필요하다.

## 15. 열린 문제

- **features의 heuristic 정확도.** 조사 부재율과 명사 종결 비율은 형태소 분석 기반 근사치다. 코드·경로 제거가 불완전하면 오탐이 난다. stage 0에서 분포를 보고 정의를 다듬는다.
- **length_growth의 기준.** policy-off 산출물이 없는 실전 상황에서는 증가율을 계산할 수 없다. 이때는 profile의 절대 상한으로 대체할지 결정 필요.
- **policy_hash_claimed의 신뢰도.** 주장 기록일 뿐이다. gate 수치 A/B가 진짜 검증이라는 점을 report 소비자에게 문서화한다.
- **hanspell 서비스 약관.** 자동화 대량 호출이 허용되는지 확인 필요. 불확실하면 hunspell 기본.
- **MCP sampling 활용 여부.** LLM 단계를 엔진 안에서 실행하는 선택지가 있으나 지원이 고르지 않아 현재는 배제. 하네스 지원이 넓어지면 재검토.
