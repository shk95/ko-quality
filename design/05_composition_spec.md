# 05. 설계 스펙: ko-quality 구성 계층

> 단계 문서. 전제: upstream은 신뢰할 만하고, 사용성을 우선한다. 검증 엔진(04)은 나중에 더할 수 있도록 형식을 공유한다.
>
> **상태: 보류.** 이 스펙은 로거를 중심에 두고 도구를 뒤로 미룬다. 이후 목표가 "우선 쓸 수 있는 스택을 만들고 검증은 다음 단계로"로 재확인되면서 구현 대상은 `06_toolkit_spec.md`가 됐다. 04와 나란히 목표 형태로 남긴다.
>
> **한 번 개정된 상태다.** 부분집합을 자른 선이 "검증이냐 아니냐"에서 **"판정하느냐 측정하느냐"**로 교정되면서 `ko.features`와 버전 스냅샷이 04에서 내려왔고, 대조군 교대와 구현 순서가 바뀌었다. 근거는 `05a_findings_measurement.md`.
>
> **로거 설계 두 곳이 사실과 어긋난다.** §9.2가 transcript를 읽도록 되어 있는데 Claude Code와 Codex 모두 transcript를 hook의 안정적 입력으로 쓰지 말라고 명시한다. §9.4의 `harness_position` 판별도 실제보다 어렵게 잡혀 있다 — 어느 hook이 발화했는지가 곧 답이다. 06 §11이 hook 입력에서 조립하는 방식으로 다시 썼다.

## 1. 목적과 전제

**목적.** 이미 있는 한국어 품질 upstream들을 프로파일·프리셋·에이전트 템플릿으로 묶어, 에이전트가 생성 방향(정책 주입)과 검토 방향(위임)으로 단계별로 쓸 수 있게 한다.

**전제.**
- upstream은 설치되고 하라는 대로 동작한다.
- upstream이 스스로 내는 수치(변경률, 등급)는 그대로 받아들인다.
- 효과의 유무는 지금 판정하지 않는다. 대신 나중에 판정할 수 있도록 재료를 쌓는다.
- **판정하지 않는 것과 재지 않는 것은 다르다.** 판정 없이 남길 수 있는 수치는 지금 남긴다.

**범위.**
- upstream 설치 구성과 버전 스냅샷 자동 기록
- 프로파일, 프리셋, 에이전트 템플릿 (04와 형식 공유)
- 라우터 skill: 요청을 받아 어떤 upstream을 어떤 순서로 부를지 정함
- 로거: 하네스 밖에서 산출물·축·측정치를 eval 케이스 형식으로 기록

**비범위.**
- 결정론적 gate, report 보증, eval 관문 (04로 이월)
- **측정치에 의한 판정** — threshold는 `watch:`로 둘 수 있으나 표시만 하고 통과·중단에 쓰지 않는다
- upstream taxonomy 편집
- voice profile

**이것은 장치가 아니다.** 02a는 프롬프트 층의 장치화가 텍스트 + 계약 + 회귀 테스트 세 개가 한 묶음일 때만 성립한다고 했다. 05는 뒤의 둘을 04로 보냈으므로 **설치 구성 + 관측**이고, 장치가 되는 시점은 eval이 들어올 때다.

## 2. 검증 엔진과의 관계

부분집합 원칙. 아래 표의 "공유"는 두 버전이 같은 파일·같은 형식을 쓰는 것이고, "추가"는 04로 갈 때 더해지는 것이다.

| 구성 요소 | 05 | 04로 갈 때 |
|---|---|---|
| profiles/*.yaml | 공유. `gate:` 절 없음 | `gate:`, `baseline:`, `on_final_fail` 절 추가 |
| presets.yaml | 공유 | `gate` 단계가 각 preset 끝에 추가 |
| agents/*.yaml | 공유. `capabilities` 비어 있음 | `capabilities: [ko.gate, …]` 추가 |
| 로거 레코드 | 공유. eval 케이스 형식. `features`·`outcome` 측정치 포함 | `expect:` 절만 채우면 케이스가 됨 |
| `features.py` | **05에 있음.** 측정만 | `capabilities/features.py`로 이동. 코드는 그대로 |
| threshold | `watch:` 절. 넘으면 레코드에 표시만 | 같은 값이 `gate:` 절이 되어 판정한다. **이름만 바뀐다** |
| 라우터 SKILL.md | 공유 | MCP transport로 대체 가능 |
| upstream | 마켓플레이스 설치 + 세션 시작 시 버전 스냅샷 | vendor 복사 + lock으로 전환 |

## 3. 디렉터리

```text
ko-quality-lite/
├── install.md            # upstream 설치 명령과 버전 기록 방법
├── upstreams.yaml        # 사용하는 upstream, 역할, 설치 시 기록된 버전
├── profiles/
│   ├── _schema.yaml      # 04와 동일 스키마. gate 절은 optional
│   ├── agent-reply.yaml
│   └── formal-report.yaml
├── presets.yaml
├── policy-blocks/        # fluent-korean README의 선택 블록만
│   ├── subagent-propagation.md
│   ├── honorific.md
│   └── think-in-korean.md
├── agents/
│   ├── writer.yaml
│   ├── reviewer.yaml
│   └── editor.yaml
├── router/
│   └── SKILL.md          # 프로파일·프리셋을 읽어 upstream skill 호출 순서를 정함
├── adapters/
│   ├── generic/          # agent.yaml → system prompt 문자열
│   └── claude-code/      # agent.yaml → agents/*.md, output-style 선택, logger hook
└── logger/
    ├── schema.yaml       # 레코드 형식 (= eval 케이스 형식)
    ├── capture/          # 하네스별 캡처 스크립트. 버전 스냅샷 포함
    ├── axes.py           # 축 계산
    ├── features.py       # 측정치 → 04 의 capabilities/features.py
    ├── outcome.py        # 작업 결과. 하네스 메타데이터에서만
    ├── watch.py          # profile.watch 와 비교해 표시만. 반환값 없음
    ├── filter.py         # 포함/제외 조건. features 를 읽지 않는다
    ├── schedule.py       # off 교대 (층화용 축 2개)
    └── README.md         # 저장 위치, 금지 사항
```

## 4. upstream 구성

| 역할 | upstream | 설치 방식 | 프로파일에서의 호출 이름 |
|---|---|---|---|
| policy | snflkd/fluent-korean | 플러그인 (output-style 2종) | `policy.fluent-korean`, `policy.fluent-korean-not-coding` |
| rewrite | epoko77-ai/im-not-ai | 플러그인 | `rewrite.im-not-ai` |
| grammar | DaleSeo/korean-skills grammar-checker | skill 복사 | `grammar.korean-skills` |
| diagnose (선택) | amondnet/yoonmoon detect | 플러그인 | `diagnose.yoonmoon` |
| slop 규칙 (선택) | limleesol/stop-slop-ko | SKILL.md 복사 | `policy.stop-slop-ko` |

원칙:
- upstream을 수정하지 않는다. 필요한 조정은 profile의 강도·면제나 에이전트 템플릿의 `append`에서 한다.
- 버전은 손으로 적지 않는다. 캡처 스크립트가 **세션 시작 시** 각 upstream 설치 디렉터리의 커밋 해시(또는 플러그인 버전)를 찍어 레코드의 `upstream_versions`에 넣는다. `upstreams.yaml`에는 역할과 설치 경로만 둔다.
- 수동 기입은 값이 조용히 거짓이 된다. 플러그인이 업데이트되면 그 시점 이후의 로그가 이전 로그와 비교 불가능해지는데, 수동 기입으로는 그 경계가 기록되지 않는다.
- rewrite는 im-not-ai 하나만. 다른 humanizer를 같은 preset에 넣지 않는다.

## 5. profiles

스키마는 04 §4.4와 동일하되 `gate`, `baseline`, `on_final_fail`은 optional이다. 대신 **`watch:`** 가 있다.

### `watch:` — 판정하지 않는 threshold

`gate:`와 같은 형식인데 **표시만 하고 막지 않는다.** 넘긴 축 이름이 레코드의 `watch_hits` 에 들어가고, 산출물은 그대로 나간다. 에이전트는 이 값을 보지 못한다.

목적은 **gate를 만들기 전에 그 gate가 어떻게 행동했을지 아는 것**이다. 발동 빈도, 오탐률, 층별 편차가 로그에 쌓이므로 04로 갈 때 threshold를 추측하지 않아도 된다. 선례는 03a #2 — 맞춤법을 fail이 아니라 warning으로 둔 것과 같은 논리다. 재현성과 오탐이 확인되기 전에는 hard fail 예산을 쓰지 않는다.

`watch:`가 하지 않는 것: 산출물 차단, `usable` 판정, off 배정, 에이전트 피드백. 전부 §9.7에서 금지한다.

초기값은 비워두거나 대충 잡아도 된다. 틀린 threshold의 비용이 표시 하나뿐이고, 그 틀림 자체가 로그에 남기 때문이다.

### agent-reply

```yaml
id: agent-reply
register: 에이전트가 사용자에게 하는 보고·설명
policy: policy.fluent-korean            # 코딩 세션. 비코딩이면 -not-coding
blocks: [subagent-propagation]          # fluent-korean 본문 뒤에 붙는 선택 블록
default_preset: standard
intensity: default
exempt: []
watch:                                  # 판정하지 않음. 레코드에 표시만
  noun_ending_ratio: 0.40               # 초기 추정치. 분포를 보고 조정
  particle_absence_ratio: 0.25
  english_ratio: 0.30
```

### formal-report

```yaml
id: formal-report
register: 사용자에게 전달되는 문서
policy: policy.fluent-korean-not-coding
blocks: [honorific]
default_preset: full
intensity: conservative                 # im-not-ai 강도
exempt: [slop.cta_in_sns, slop.polite_email_ending]
watch:
  noun_ending_ratio: 0.30               # 문서 레지스터라 더 엄격
  particle_absence_ratio: 0.15
  english_ratio: 0.15
```

두 profile의 `watch:` 값이 다르다는 것 자체가 관측 대상이다. 실제로 레지스터에 따라 분포가 갈리는지, 아니면 같은 값으로 수렴하는지가 두 번째 profile을 둔 이유(03a #4의 마지막 항목)에 답한다.

## 6. presets

```yaml
quick:    []                            # 아무 단계도 없음. 로거만 동작
standard: [policy]
review:   [diagnose]
edit:     [rewrite, grammar]
full:     [policy, rewrite, grammar, diagnose]
```

04와의 차이: 각 preset 끝의 `gate`가 없다. `selfcheck`도 없다 — gate가 없으면 selfcheck는 모델의 자기 점검일 뿐이므로 fluent-korean README의 "출력 직전 점검" 블록으로 대체한다.

## 7. agents

프롬프트는 upstream skill을 이름으로 호출한다. 도구 문법은 쓰지 않는다.

### writer.yaml

```yaml
name: korean-writer
role: 정책을 받아 산출물을 생성한다
capabilities: []
prompt:
  compose: [profile.policy, profile.blocks]
  append: |
    출력 직전에 위 지침에 어긋난 부분을 점검하고 수정한 뒤 출력한다.
```

### reviewer.yaml

```yaml
name: korean-reviewer
role: 산출물을 수정하지 않고 진단한다
preset: review
capabilities: []
prompt:
  compose: [profile.policy]
  append: |
    diagnose.yoonmoon 을 호출해 AI 가능성·신뢰도·근거를 받는다.
    텍스트를 고치지 않는다. 결과는 upstream 출력 형식 그대로 반환한다.
```

### editor.yaml

```yaml
name: korean-editor
role: 산출물을 윤문하고 맞춤법을 교정한다
preset: edit
capabilities: []
prompt:
  compose: [profile.policy]
  append: |
    rewrite.im-not-ai 를 profile.intensity 로 호출한다.
    이어서 grammar.korean-skills 를 호출한다.
    im-not-ai 가 내는 변경률과 등급을 그대로 반환한다.
```

오케스트레이터 계약(lite): 산출물 수락 여부는 오케스트레이터가 정한다. editor가 반환한 변경률이 50%를 넘으면 im-not-ai 자체가 중단하므로, 오케스트레이터는 그 중단 보고를 존중하면 된다.

## 8. 라우터 SKILL.md

역할: "프로파일 P, 프리셋 X로 이 텍스트를 처리해라"를 받아 §6의 순서대로 upstream skill을 호출하고 결과를 이어 붙인다.

```text
입력: text, profile, preset | stages
절차:
  1. profiles/<profile>.yaml 을 읽는다
  2. preset 을 stages 로 푼다
  3. policy 가 있으면: 이미 output-style 로 켜져 있는지 확인. 아니면 정책 텍스트를 컨텍스트에 넣는다
  4. 나머지 stage 를 순서대로 upstream skill 이름으로 호출한다
  5. 각 upstream 의 출력(변경률, 등급, 탐지 표)을 그대로 이어 붙여 반환한다
금지: upstream 출력을 요약하거나 재해석하지 않는다
```

라우터 자체는 100줄 이내의 텍스트다. 04의 MCP transport가 이 역할을 대체할 수 있도록 입력 형식은 04 §4.1과 같게 둔다.

## 9. 로거

### 9.1 원칙

- 하네스 **밖**에서 돈다. 모델은 로거의 존재를 모른다.
- **판정하지 않고 차단하지 않는다. 그러나 잰다.** 결정론적으로 계산되는 수치는 threshold 없이 기록한다. 판정은 그 값으로 통과·중단을 정하는 것이고, 로거는 값을 남기는 데서 멈춘다.
- 레코드 형식 = eval 케이스 형식. 나중에 `expect:`만 채우면 케이스가 된다.
- 토큰을 쓰지 않는다. §9.7의 금지 사항으로 보장한다.

### 9.2 캡처 지점

| 하네스 | 방법 |
|---|---|
| Claude Code | Stop hook → transcript 경로 → 마지막 assistant 턴과 서브에이전트 결과 추출 |
| Codex | 세션 파일 후처리 |
| 직접 하네스 | API wrapper에서 요청·응답 쌍 |

### 9.3 레코드 스키마

```yaml
id: string                          # 날짜-일련번호
ts: datetime
# ── 실행 조건 ──
profile: string
preset: string
policy_on: bool
injection_point: output-style | claude-md | system-string | none
upstream_versions: {name: version}
model: string
# ── 축 ──
instruction_lang: ko | en | mixed
artifact_lang: ko | en | mixed
think_ko_instructed: bool
context_en_ratio: float
harness_position: main-to-user | sub-to-orchestrator | sub-to-sub
session: {turns: int, tokens_so_far: int}
task_type: coding | writing | analysis | null
# ── 내용 ──
task: string                        # 지시 요약. 원문이 짧으면 원문
output: string                      # 모델이 생성한 한국어 span만
before: string?                     # editor 경로일 때 윤문 전
after: string?
tokens: {output: int}
upstream_report: string?            # im-not-ai / yoonmoon 출력 그대로
# ── 측정 (판정 아님) ──
features:                           # features.py. threshold 없음
  comma_rate: float
  pos_ngram_diversity: float
  noun_ending_ratio: float          # 종결어미 없이 명사구로 끝나는 문장 비율
  particle_absence_ratio: float     # 명사 뒤 조사 부재 비율
  english_ratio: float              # 코드·경로 제외
  sentence_len_var: float
outcome:                            # 하네스 메타데이터에서. LLM 분류 금지
  retries: int                      # 같은 task 재시도 횟수
  user_followup: bool               # 사용자가 다시 요청했는가
  tool_errors: int
watch_hits: [string]                # profile.watch 를 넘긴 축 이름. 판정 아님
watch_version: string               # 어느 watch 설정으로 평가했는가 (해시)
# ── 나중에 채움 ──
expect: null
```

`features`와 `outcome`이 종속변수다. 이게 없으면 축 아홉 개를 기록해도 비교할 대상이 없고, 레코드는 04를 구현해야만 값이 생기는 원문 더미가 된다. 특히 `think_ko_instructed` 축은 04a가 "유일한 실험은 작업 성공률"이라고 못 박았으므로 `outcome` 없이는 영원히 분석되지 않는다.

### 9.4 축 계산 (`axes.py`)

| 축 | 계산 |
|---|---|
| instruction_lang, artifact_lang | 한글 문자 비율. 0.8 이상 ko, 0.2 이하 en, 사이 mixed. 코드 블록·경로·URL은 제외 후 계산 |
| think_ko_instructed | profile.blocks 에 think-in-korean 포함 여부 |
| context_en_ratio | transcript 의 시스템 프롬프트·도구 출력·코드 블록에서 영어 문자 비율 |
| harness_position | 하네스 메타데이터. Claude Code는 서브에이전트 transcript 여부로 판별 |
| session | transcript 턴 수, 누적 토큰 |
| task_type | 규칙: Edit/Write 도구 호출 있으면 coding, 산출물이 .md 이고 도구 호출 없으면 writing, 그 외 null. **LLM 분류 금지** |

### 9.4b 측정치 계산 (`features.py`)

04 §6의 `ko.features`를 threshold 없이 가져온 것. kiwipiepy로 형태소를 얻어 `output` 에서만 계산하고, 코드 블록·경로·URL·인용은 제외한다.

- 계산만 하고 판정하지 않는다. 반환에 pass/fail 이 없고 profile 은 이 값을 읽지 않는다.
- baseline 대비 z 점수는 내지 않는다. baseline 자체가 04 항목이고, 비교는 로그가 쌓인 뒤 사후에 한다.
- 계산이 실패하면(형태소 분석 오류 등) `features: null` 로 두고 레코드는 살린다. `usable` 판정에는 쓰지 않는다.

04 로 갈 때 이 파일이 `capabilities/features.py` 가 되고, profile 의 `gate:` 절이 같은 값에 threshold 를 건다. **threshold 를 걸고 싶어지는 시점이 04 전환의 신호다.**

### 9.4c 작업 결과 (`outcome`)

하네스 메타데이터와 transcript 구조에서만 계산한다. 에이전트에게 묻지 않는다.

| 필드 | 계산 |
|---|---|
| retries | 같은 task 로 묶인 재시도 수 (§9.5 의 `retry_of` 사슬 길이) |
| user_followup | 산출물 직후 사용자 턴이 재요청인가. 규칙: 새 파일·새 도구 호출 없이 이어지는 짧은 사용자 턴 |
| tool_errors | transcript 의 도구 오류 수 |

`user_followup` 은 근사치다. 정확도가 낮으면 규칙을 고치되 LLM 으로 분류하지 않는다 — 토큰이 새는 지점이 된다.

### 9.4d watch 평가

`features` 계산 뒤, profile 의 `watch:` 와 비교해 넘긴 축 이름만 `watch_hits` 에 넣는다. 여기서 끝난다.

- `watch:` 설정을 바꾸면 **그 시점 이후 레코드만** 새 설정으로 평가된다. 과거 레코드를 다시 계산하지 않는다
- 대신 `watch_version` 에 설정 해시를 남겨 어느 기준으로 평가된 것인지 구분한다. 이게 없으면 threshold 를 조정한 전후가 섞여 발동률 추이가 거짓이 된다
- `features: null` 이면 `watch_hits: null`. 빈 배열(`[]`, 넘긴 축이 없음)과 구분한다
- 산출물 처리에 영향을 주지 않는다. 반환값이 없고 호출자가 없다

**승격은 자동이 아니다.** `watch:` 가 `gate:` 가 되는 것은 §11 의 조건 셋을 사람이 확인한 뒤에만 일어난다. 발동률이 높다는 것만으로는 근거가 되지 않는다 — threshold 가 잘못 잡혔을 가능성이 먼저다.

### 9.5 포함/제외 (`filter.py`)

- `output` 은 모델 생성분만. 사용자 입력과 도구 출력을 transcript 에서 diff 로 제거
- 한국어 어절 20개 미만 제외 (초기값, 조정 가능)
- 같은 task 의 재시도는 `retry_of` 로 연결하고 마지막 것만 A/B 대상
- 축 중 `injection_point`, `harness_position`, `instruction_lang`, `artifact_lang` 이 비면 `usable: false`
- **`features` 와 `watch_hits` 는 `usable` 판정에 쓰지 않는다.** 재려는 변수로 표본을 거르면 최악의 한국어가 체계적으로 삭제된다 — 조사 부재율이 비정상이라 버린 레코드가 바로 fluent-korean 이 겨냥한 결함이다. 형태소 분석이 실제로 깨졌더라도 `features: null` 로 두고 레코드는 살린다

### 9.6 대조군 교대 (`schedule.py`)

**축을 두 종류로 나눈다.**

| 종류 | 축 | 쓰임 |
|---|---|---|
| 층화용 | `harness_position` × `policy_on` | `schedule.py` 가 배정에 쓴다 |
| 분석용 | 나머지 전부 | 기록만. 사후 필터로 쓴다 |

이유: off 배정은 **세션 시작**에 일어나는데(off 의 실현이 output-style 을 default 로 두거나 spawn 시 policy 블록을 빼는 것이므로), 층 키에 `task_type` 이나 실제 `harness_position` 을 넣으면 배정 시점에 존재하지 않는 값을 요구하게 된다. 사전 균형 배정이 불가능해지고 사후 층화만 남는다. 또 4축을 다 쓰면 층이 최대 72개(2×3×4×3)로 쪼개져 층당 대조 표본이 실질적으로 안 쌓인다.

규칙:

- 층 키 = **세션 시작에 확정되는 것만**. `profile` 과 `injection_point`, 그리고 서브에이전트라면 spawn 시점에 정해지는 `harness_position`
- 층마다 카운터. k번째마다 policy off. **초기 k=3~5** (stop-slop-ko 의 블라인드 5:5 는 검출할 효과가 작다는 뜻이고, 작은 효과는 큰 표본을 요구한다)
- 로거는 세션 시작 설정을 읽어 `policy_on` 을 기록
- 같은 작업을 on/off 두 번 돌리지 않는다. A/B 는 층 안에서의 비교이지 짝지은 반복이 아니다
- `main-to-user` 의 off 는 사용자가 그 세션의 품질 저하를 떠안는다. 이 비용이 크면 off 를 서브에이전트 경로에만 적용하고 `main-to-user` 는 수동으로 모은다

사후 분석은 층화용 축으로 자른 뒤 분석용 축으로 다시 좁힌다. "policy 가 효과 있었나"는 답이 없고 "지시 ko · 산출물 ko · sub→orchestrator · 긴 세션에서 효과 있었나"만 답이 있다.

### 9.7 금지 사항

- 에이전트에게 로그를 쓰게 하지 않는다 (자기 보고 없음)
- task_type 을 LLM 으로 분류하지 않는다
- 로그를 작업 디렉터리 안에 두지 않는다. `~/.ko-quality/logs/` 또는 그에 준하는 트리 밖 경로

**측정이 판정으로 새는 네 지점.** `features` 와 `watch_hits` 가 레코드에 있으면 쓰고 싶어진다. 네 가지를 막는다.

| 금지 | 하면 깨지는 것 |
|---|---|
| `filter.py` 가 `features` 를 읽어 `usable` 을 정하는 것 | 재려는 변수로 표본을 거르면 최악의 한국어가 삭제된다 (§9.5) |
| `schedule.py` 가 `features` 나 `watch_hits` 를 보고 off 를 배정하는 것 | 대조군이 종속변수로 선택되어 A/B 가 무의미해진다. off 로 인한 사용자 불편을 줄이려 할 때 가장 끌리는 선택이다 |
| 에이전트에게 `features` 나 `watch_hits` 를 보여주는 것 | 토큰이 새고, 모델이 지표를 최적화하기 시작하며, 그 전후 레코드가 서로 비교 불가능해진다. 몇 주치 로그가 두 동강 난다 |
| `watch_hits` 를 근거로 산출물을 막는 것 | 그건 gate 다. 만들려면 §11 절차를 따른다 |

세 번째가 가장 조용히 일어난다. 로거는 하네스 밖에 있으므로 모델에게 값을 넘기려면 누군가 의도적으로 배선해야 하는데, "출력 직전 자기 점검"을 강화하려는 시도가 정확히 그 모양을 한다.

### 9.8 저장

- `~/.ko-quality/logs/<profile>/<yyyy-mm>.jsonl`
- 월별 파일. 하네스별 캡처 스크립트가 append
- 개인정보·비밀은 캡처 단계에서 기존 secret 패턴으로 마스킹. 마스킹된 레코드는 `masked: true`

## 10. adapters

| adapter | 담당 |
|---|---|
| generic | agent.yaml → system prompt 문자열. policy 텍스트를 앞에 붙임 |
| claude-code | agent.yaml → `.claude/agents/<name>.md`; profile.policy → settings 의 outputStyle; Stop hook 에 logger capture 등록 |

adapter 는 프롬프트 내용을 바꾸지 않는다. 04 의 policy_hash 테스트는 lite 에서는 생략하되, 두 adapter 가 같은 profile 에서 같은 정책 텍스트를 내는지 문자열 비교로 확인한다.

## 11. 검증 엔진으로 가는 절차

신뢰가 깨진 지점이 생기면 그 지점만 04 에서 가져온다. 순서는 자유이나 전형적으로:

### 11.1 승격 조건 — `watch:` 하나가 `gate:` 가 되는 때

한 축씩 판단한다. 셋을 **전부** 확인한 뒤에만 연다.

| 조건 | 확인 방법 | 못 넘으면 |
|---|---|---|
| 1. 분포가 안정됐는가 | 층당 표본이 충분한가, `watch_version` 이 같은 구간에서 발동률이 수렴했는가 | 더 쌓는다 |
| 2. 오탐률을 쟀는가 | `watch_hits` 가 붙은 레코드를 **손으로 읽어** 실제로 나쁜지 본다. LLM 에게 묻지 않는다 | threshold 를 고치고 1번으로 |
| 3. 그 축에서 on/off 차이가 나는가 | 같은 층 안에서 `policy_on` 별 분포를 비교한다 | **gate 를 걸지 않는다.** 아래 참조 |

3번이 핵심이다. `policy_on` 이 그 축을 움직이지 않으면, 거기에 gate 를 거는 것은 이 설계가 검증하려던 것과 무관한 일을 하는 것이다. 그건 한국어 품질 엔진이 아니라 일반 문체 린터이고, 다른 프로젝트다. 발동률이 높다는 것만으로는 근거가 되지 않는다 — threshold 가 잘못 잡혔을 가능성이 먼저다.

### 11.2 절차

1. 로거 레코드 중 `usable: true` 인 것을 `evals/cases/` 로 복사, `expect:` 채움 — `features` 와 `watch_hits` 가 이미 들어 있으므로 기대값을 실측 분포에서 뽑을 수 있다
2. `logger/features.py` 를 `capabilities/features.py` 로 옮긴다. 코드는 그대로이고 호출자만 바뀐다
3. 04 §6 의 나머지 capability 중 필요한 것만 구현 (대개 preserve, change_rate 부터)
4. profile 의 `watch:` 에서 승격 조건을 통과한 축만 **`gate:` 로 이름을 바꾼다.** 값은 그대로 — 이미 실측으로 검증된 threshold 다. 나머지 축은 `watch:` 에 남는다
5. preset 끝에 `gate` 추가
6. 해당 에이전트 템플릿 `capabilities` 에 `ko.gate` 추가
7. `upstreams.yaml` 의 버전 스냅샷을 `vendor.lock` 으로 승격
8. 필요하면 라우터를 MCP transport 로 교체

각 단계는 기존 파일에 절을 더하는 것이지 형식을 바꾸는 것이 아니다. 4번은 절을 더하지도 않고 키 이름만 바꾼다.

**전환의 신호.** 측정치에 threshold 를 걸고 싶어지는 순간 — 이 신호는 `watch:` 가 흡수한다. 걸고 싶으면 걸되 판정하지 않는 자리가 이미 있으므로, 진짜 신호는 그다음이다. **`watch_hits` 가 붙은 산출물을 실제로 막았어야 했다고 판단하는 사례가 쌓이는 것.**

**재료의 전제.** 1번의 `usable: true` 는 `harness_position` 을 요구하고(§9.5), `sub-*` 값은 S3 이후에야 생긴다. 서브에이전트 경로에 gate 를 걸려면 S3 이후로도 충분한 축적 기간이 필요하다.

**부분적 전환이 정상이다.** 축 하나만 `gate:` 로 가고 나머지는 `watch:` 에 남는 상태가 오래 유지될 수 있다. 04 로 "넘어가는" 시점 같은 것은 없고, 축 단위로 하나씩 승격될 뿐이다.

## 12. 구현 순서

```text
S0   upstreams.yaml, install.md, 버전 스냅샷 스크립트
S1a  agent-reply.yaml (watch: 초기 추정치 포함), presets.yaml
S2   logger: schema, axes, features, outcome, watch 평가, filter,
     claude-code capture, 단순 off 교대,
     Stop hook 수동 등록                                  ← 여기서부터 재료가 쌓임
     ── 1주 뒤: watch 초기값 1회 조정, watch_version 올림 ──
     ─────────── 6~8주 재료 축적 ───────────
S3   agents 3개 + generic adapter + claude-code adapter
     + S1 나머지 (subagent-propagation, formal-report, honorific)
     ← 여기서부터 sub→* 경로가 기록됨
S4   router SKILL.md                                     ← review/edit 가 실제로 필요해질 때
S5   codex capture
보류 think-in-korean 블록 — outcome 필드가 실측된 뒤
```

**S1 을 쪼갠 이유.** profile 이 실제로 하는 일(policy 선택, blocks 조합, intensity, exempt)은 전부 에이전트에 주입되거나 라우터가 읽는 것이라 S3 전에는 소비자가 없다. 다만 `agent-reply` 하나는 레코드의 `profile` 필드가 매직 스트링이 아니라 실제 파일을 가리키게 하므로 앞에 둔다.

**S2 를 앞에 두는 이유.** 나머지가 완성되기 전이라도 policy on/off 산출물이 쌓이기 시작해야 한다. 다만 그 대가가 셋이다.

| 대가 | 처리 |
|---|---|
| capture 에 필요한 Stop hook 자동 등록이 claude-code adapter(S3)에 있다 | S3 까지 손으로 건다 |
| off 교대가 없으면 전부 on 샘플이다 | 단순형(`policy_on` 만 교대)을 S2 에 흡수 |
| S3 전에는 `harness_position` 이 전부 `main-to-user` 다 | **처방 없음.** 초기 로그로는 01 이 지목한 다단계 누적을 못 잰다 |

**S3 에서 adapter 둘을 합치는 이유.** hook 자동 등록과 서브에이전트 경로가 같은 시점에 필요해진다. **S4 를 뒤로 미루는 이유.** S2~S3 시점에 실재하는 경로(일상 보고, 대조군 세션) 중 라우터를 쓰는 것이 하나도 없다.

## 13. 열린 문제

- **artifact_lang 의 mixed 처리.** 코드 + 한국어 주석 산출물에서 한국어 span 추출이 불완전하면 output 이 오염된다. 초기에는 주석·문자열 리터럴·마크다운 문단만 추출하고 코드 토큰은 버린다.
- **harness_position 의 판별.** Claude Code 외 하네스에서 서브에이전트 여부를 메타데이터로 못 얻으면 null 로 두고 usable 에서 제외한다.
- **off 교대와 사용자 경험.** k번째 세션마다 policy 가 꺼지면 그 세션의 한국어가 나빠진다. k 를 3~5 로 내렸으므로 이 비용이 커진다. off 를 서브에이전트에만 적용하고 main→user 는 수동으로 모으는 절충을 S3 에서 재검토한다.
- **`user_followup` 의 정확도.** "사용자가 다시 요청했다"를 규칙으로 판별하는 것은 근사치다. 재요청과 후속 질문을 못 가르면 종속변수가 오염된다. 초기 표본을 손으로 라벨링해 규칙의 일치율을 한 번 잰다. LLM 분류로 도망가지 않는다.
- **`features` 의 heuristic 정확도.** 조사 부재율과 명사 종결 비율은 형태소 분석 기반 근사치이고, 코드·경로 제거가 불완전하면 값이 흔들린다. 판정에 쓰지 않으므로 당장 위험하지는 않지만, `watch:` 의 오탐률(§11.1 조건 2)이 이 정확도에 직접 달려 있다.
- **`watch:` 초기값을 어디서 가져오나.** 지금은 추정치다. 첫 레코드가 쌓일 때까지는 발동률이 0 이거나 100% 일 수 있고, 둘 다 정보가 없다. 첫 주에 한 번 조정하고 `watch_version` 을 올린다. 조정 전후를 섞어 발동률 추이를 보지 않는다.
- **`watch:` 가 gate 로 자동 승격되는 유혹.** 발동률이 높으면 "막아야겠다"로 바로 가기 쉽다. §11.1 의 조건 3(on/off 차이)이 그것을 막는 유일한 장치인데, 이 조건은 대조군이 충분히 쌓여야 확인된다. 즉 `k` 를 3~5 로 내린 것(§9.6)과 승격 조건이 같은 재료를 두고 경쟁한다.
- **`watch:` 가 05 의 전제를 흔드는가.** threshold 를 profile 에 적는 순간 "upstream 을 믿는다"는 전제가 말로만 남는다는 반론이 가능하다. 구분해 둔다 — 믿지 않는 것은 upstream 의 **동작**이 아니라 **효과**이고, 04a 가 전제의 두 층위를 나눌 때 이미 후자는 약하다고 적었다. `watch:` 는 그 약한 쪽을 재는 장치이지 upstream 을 의심하는 장치가 아니다.
- **stop-slop-ko 의 위치.** 생성 모드 규칙을 policy 로 쓸지, 교정 모드를 edit preset 에 넣을지. 후자는 rewrite taxonomy 가 둘이 되므로 넣지 않는다. 전자만, 선택 블록으로.
