# 06. 설계 스펙: ko-quality 툴킷

> 단계 문서. 구현 대상. **산출물은 설치하면 바로 쓰이는 도구**이고, 품질 개선의 검증은 다음 단계다.
>
> 05와의 차이: 05는 로거를 중심에 두고 도구를 뒤로 미뤘다. 06은 도구를 앞에 두고 로거를 최소형으로 남긴다. 05는 04와 나란히 보류로 남긴다.
>
> **개정됨 (06a 반영).** upstream과 우리 사이에 **공급 층**을 두고, 추상화(스키마)는 프로토타입 뒤로 미뤘다. 구현은 §14의 프로토타입 계획 P0부터 시작한다. 근거는 `06a_findings_supply.md`.
>
> **개정됨 (06b P0 반영, 2026-09-14).** 정책 조각의 단위(§5.3·§6·§9), 앵커 규칙(§5.5), `ko-rewrite` invariant의 범위와 변경률의 성격(§1·§7·§13.1), Codex 플러그인 사실(§2·§11.5·§12·§13.2). 근거와 기각한 선택지는 `06b_built_prototype.md`의 P0 "06 반영 결정".
>
> **개정됨 (P1 착수 전 문서 검토, 2026-09-14).** 문서 안의 어긋남과 빈 곳을 고치고(§5.2 파일 이름, §6 presets, §7 참조, §8 결합, §9 분량·`force-for-plugin`·`instructions`, §12 검사 2, §13.3 대조군, §15·§16), 공식 문서로 다시 확인한 사실을 반영했다(§2.1 `force-for-plugin` 충돌, §2.2 Codex `developer_instructions`·플러그인 확장 키·hook 기본 활성, §2.4 참여사, §11.2 `model`·에이전트 이름, §13.1 `tokens`·`sub-to-sub`). 기록은 `06b_built_prototype.md`의 "검토 — P1 착수 전 문서 정리".

## 1. 목적과 전제

**목적.** 이미 있는 한국어 품질 upstream들을 하나의 설치 단위로 묶어, Claude Code와 Codex에서 에이전트가 실제로 쓸 수 있는 도구로 만든다.

**전제.**
- upstream은 설치되고 하라는 대로 동작한다.
- upstream이 스스로 내는 수치(변경률, 등급)는 그대로 받아들인다. 단 upstream이 스크립트로 계산하는 값은 06이 받지 못한다. 06이 받는 변경률은 모델의 자기 보고다 (§7, §13.1).
- **upstream의 문장을 신뢰한다. 그러므로 문장을 고치지 않는다.** 구조는 우리 규격으로 바꿔도 된다 (§5).
- **효과의 검증은 다음 단계의 일이다.** 06은 재료만 남긴다.

**범위.**
- upstream 공급 층: 버전 고정, 역할 단위 정규화, 출처 기록
- 조립: 프로파일·프리셋·에이전트 정의·스킬 템플릿
- 하네스별 빌드: Claude Code 플러그인, Agent Plugins 패키지
- hook 기반 최소 로거

**비범위.**
- gate, report 보증, eval (검증 단계로 이월)
- `features` 계산과 threshold, `watch:` 절 (검증 단계로 이월 — `05a` 참조)
- MCP tool (검증 단계에서 채운다. 06의 서버는 `instructions`만 싣는다)
- voice profile

## 2. 확인된 사실

이 스펙은 2026-09-12에 공식 문서로 확인하고 **2026-09-14(P0)에 재확인한** 아래 사실 위에 서 있다. 재확인 결과와 출처는 `06b` P0에 있다. **하네스 사양은 빠르게 바뀌므로 Codex 부분은 P6에서 한 번 더 확인한다 (§14).**

### 2.1 Claude Code

| 항목 | 확인된 것 |
|---|---|
| 플러그인 구성요소 | `skills/`, `commands/`, `agents/`, `workflows/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `monitors/monitors.json`, `bin/`, `scripts/`, `settings.json`, `output-styles/`, `themes/`(실험) |
| 매니페스트 | `.claude-plugin/plugin.json`. 선택이며, 없으면 기본 위치에서 구성요소를 찾는다 |
| 출력 스타일 frontmatter | `name`, `description`, `keep-coding-instructions`, `force-for-plugin` |
| `force-for-plugin: true` | 플러그인이 켜져 있으면 사용자 선택 없이 자동 적용. 사용자의 `outputStyle` 설정을 덮어씀. **여러 플러그인이 켜 두면 먼저 로드된 것이 이긴다** — 사용자가 다른 force 플러그인을 쓰면 우리 정책이 걸리지 않을 수 있다 |
| 플러그인 `settings.json` | `agent`와 `subagentStatusLine` 키만 지원. `agent`는 플러그인 에이전트를 **메인 스레드**로 올림 |
| MCP | tools · resources · prompts 전부 |
| hook | 33개 이벤트. 플러그인이 `hooks/hooks.json`으로 나름. 플러그인 에이전트는 `agent_type`에 `<플러그인>:<에이전트>` 꼴의 범위 이름으로 나타난다 |
| 서브에이전트 중첩 | 기본으로 서브에이전트가 서브에이전트를 띄울 수 있다(메인 아래 3층까지). `sub-to-sub` 경로가 실제로 생긴다 |
| 동작 평가 | `claude plugin eval` — 프롬프트 세트를 플러그인 on/off로 반복 실행해 기여도를 봄 |
| 로컬 로드 | `claude --plugin-dir <dir>`, 변경 후 `/reload-plugins` |

**결정적 제약:** 출력 스타일은 메인 대화와 fork에만 적용되고 **서브에이전트에는 적용되지 않는다.** 서브에이전트는 자기 시스템 프롬프트로 돈다.

### 2.2 Codex

| 항목 | 확인된 것 |
|---|---|
| 플러그인 | 루트 `plugin.json`(Agent Plugins `$schema` 선언) + `skills/` + `mcp.json`. OpenAI 전용 설정은 루트 `plugin.json`의 `extensions.com.openai`이고 문서화된 키는 `apps`, `hooks`, `interface` 셋뿐이다 — **서브에이전트 정의는 플러그인에 실을 수 없다.** `.codex-plugin/plugin.json`은 호환용. 마켓플레이스 있음 |
| skills | `.agents/skills/`(cwd·상위·저장소 루트), `$HOME/.agents/skills`, `/etc/codex/skills`, 시스템, 플러그인. `SKILL.md` frontmatter는 `name`·`description`(그 밖의 키는 문서에 없음). CLI에서 `$`로 명시 호출. 세션 시작에 싣는 스킬 목록은 컨텍스트의 2% 또는 8,000자 안 |
| 서브에이전트 | `~/.codex/agents/` 또는 `.codex/agents/`의 TOML. `name`, `description`, `developer_instructions` 필수. `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers` 지정 가능 |
| 상시 지시문 | `AGENTS.md`. 32 KiB 상한(`project_doc_max_bytes`). 전역(`~/.codex/AGENTS.md`, `AGENTS.override.md` 우선)과 프로젝트(루트에서 cwd까지) 두 범위. 그 밖에 `config.toml`의 `developer_instructions`(세션에 주입되는 추가 개발자 지시)와 `model_instructions_file`(내장 지시 대체)이 있다 |
| hook | 기본 활성(`[features] hooks = false`로 끔. `codex_hooks`는 낡은 별칭). `~/.codex/hooks.json`, `<repo>/.codex/hooks.json`, `config.toml`의 `[hooks]`, **플러그인 번들**(`extensions.com.openai.hooks`, 없으면 기본 `hooks/hooks.json`). 플러그인 hook은 설치·활성화만으로 신뢰되지 않으며, 사용자가 정의를 검토하고 신뢰해야 실행된다(다른 비관리 hook과 같은 절차). hook 스크립트는 실행 환경에 있어야 한다. 공통 입력에 `model`(활성 모델 slug)이 있다 |
| MCP | **tools 전용.** STDIO / Streamable HTTP / 서버 `instructions` 필드만 지원 목록에 있음. `instructions`는 "서버의 tools와 함께 서버 전역 지침으로 쓴다"고만 적혀 있어, tool이 없는 서버의 `instructions`가 모델에 닿는지는 문서에 없다 |

**결정적 제약:** Codex의 MCP 클라이언트는 `tools/list`와 `tools/call`만 발행한다. **resources와 prompts가 도달하지 않는다.**

### 2.3 공통 hook 이벤트

| 이벤트 | Claude Code | Codex | 06에서 쓰는 것 |
|---|---|---|---|
| `SessionStart` | ✅ | ✅ | 정책 상태 |
| `UserPromptSubmit` | ✅ | ✅ | 지시 원문 |
| `PostToolUse` | ✅ | ✅ | 도구 호출 누적 |
| `Stop` | ✅ | ✅ | `last_assistant_message` |
| `SubagentStop` | ✅ | ✅ | `last_assistant_message` + 에이전트 식별 |
| `SessionEnd` | ✅ | ✅ | 레코드 확정 |

`Stop`과 `SubagentStop`은 양쪽 모두 `last_assistant_message`를 준다. Codex의 `SubagentStop`은 `agent_id`와 `agent_type`까지 준다.

**결정적 제약:** transcript 파일을 읽으면 안 된다. Claude Code는 "비동기로 쓰여 현재 턴이 아직 없을 수 있으니 `last_assistant_message`를 쓰라"고 하고, Codex는 "transcript 형식은 hook을 위한 안정적 인터페이스가 아니며 바뀔 수 있다"고 한다.

### 2.4 Agent Plugins 1.0

벤더 중립 패키징 표준. `plugin.json` + `skills/` + `mcp.json` + `com.example.client/` 네임스페이스.

- 구성요소는 **Agent Skills와 MCP 서버 둘뿐**이다. 에이전트 정의·hook·출력 스타일은 표준에 없다.
- 표준 밖의 것은 역도메인 확장 자리에 싣는다. Codex는 hook을 `extensions.com.openai`에 싣는다 (§2.2).
- 사이트의 기술 운영 위원회는 Amazon · Cursor · Microsoft · OpenAI · Vercel이다. **지원 클라이언트 목록은 사이트에 없다.** 이전 판본이 적은 "Codex · Cursor · GitHub Copilot · Kiro · VS Code"는 확인되지 않은 목록이었다. 06이 실제로 시험하는 Agent Plugins 클라이언트는 Codex뿐이다 (§12).
- **Claude Code는 참여하지 않고 자체 포맷을 유지한다.**

## 3. 층 구조

능력이 아니라 **성질**로 층을 가른다.

| 층 | 무엇 | 왜 거기인가 |
|---|---|---|
| **공급** | upstream 문장을 역할별 규격으로 정규화 | 문장은 그들의 것, 형식은 우리의 것. 하류가 upstream 형식을 모르게 한다 (06a) |
| **Skill** | 절차 지시문 + taxonomy 참조 | 두 하네스가 네이티브 지원. 점진적 공개가 "절차만 짧게, 목록은 필요할 때"와 같은 메커니즘 |
| **MCP** | (검증 단계) gate · features · change_rate 계산 | 계산은 하네스 무관. Codex 제약 때문에 **tools만** 쓴다 |
| **하네스별 렌더** | 정책 주입, 에이전트 정의, hook 배선 | 형식과 위치가 하네스마다 다르고, 세션 시작 전에 파일로 있어야 함 |

03이 MCP를 고른 판단은 맞았지만, MCP가 맡을 것은 텍스트가 아니라 계산이었다. 지시문은 Skill이 나르고, Skill의 본문은 공급 층에서 온다.

## 4. 디렉터리

**그들의 것 / 우리의 것 / 만들어진 것**을 디렉터리로 가른다.

```text
ko-quality/
├── design/                      # 설계 기록
├── upstream/                    # 그들의 것 — 공급 층
│   ├── lock.yaml                # name, url, commit, license, license_checked
│   ├── interface/               # 역할별 규격. P4에서 역산. 그 전까지 비어 있음
│   ├── extractors/              # 벤더별 추출기. P4에서 코드화
│   ├── normalized/              # 커밋됨. 하류가 읽는 유일한 upstream 내용
│   │   ├── policy/
│   │   ├── procedure/
│   │   └── taxonomy/
│   └── .cache/                  # 받아온 원본. 커밋하지 않음
├── assemble/                    # 우리의 것 — 조립
│   ├── profiles/
│   ├── presets.yaml
│   ├── agents/                  # 중립 YAML
│   └── skills/                  # 템플릿: 발동 조건, 호출 규약, 우리 문장
├── server/                      # MCP. 06에서는 instructions만
├── logger/                      # hook 기반 최소형
├── build/                       # 공급 + 조립 → dist
│   ├── claude_code.py
│   └── agent_plugin.py
└── dist/                        # 만들어진 것. 손으로 쓰지 않음
    ├── claude-code/
    └── agent-plugin/
```

**예외:** P1~P3 프로토타입 동안에는 `upstream/normalized/`와 `dist/`를 손으로 만든다. P4에서 추출기와 빌드가 같은 결과를 재생성해야 하며, **손 산출물과 코드 산출물의 diff가 0이어야 한다.** 그 diff가 추출기의 첫 테스트다.

`upstream/.cache/`는 `.gitignore`에 넣는다.

## 5. 공급 층

upstream을 dump로 쌓지 않고, 버전을 고정해 받아온 뒤 우리 규격으로 정규화한다. 상세 근거는 06a.

### 5.1 왜 복사인가

1. **설치가 한 번이다.** 사용자가 upstream 넷을 따로 깔지 않는다. "우선 쓸 수 있게"라는 목표에 직결된다.
2. **버전이 사실이 된다.** lock이 커밋을 고정하므로 기록된 버전이 추측이 아니다.
3. **정책은 합성 말고는 길이 없다.** 출력 스타일은 하나만 활성화되므로 fluent-korean의 스타일과 선택 블록을 층으로 얹을 수 없다. 합쳐서 하나로 렌더하려면 문장이 손에 있어야 한다.

### 5.2 흐름

```text
lock.yaml ─ 받아오기 ─→ .cache/<name>@<commit>/
                            │ 추출기 (P1~P3은 손, P4부터 코드)
                            ↓
                      normalized/<role>/<slot 또는 name>.yaml   ← 커밋
                            │ build/
                            ↓
                          dist/
```

원본은 커밋하지 않는다. 대가는 upstream 저장소가 사라지면 재추출을 못 한다는 것이고, 정규화 산출물이 커밋돼 있으므로 도구는 계속 동작한다.

**파일 이름.** `procedure/`와 `taxonomy/`는 슬롯 이름으로 둔다 (`rewrite.yaml`, `diagnose.yaml`, `grammar.yaml`). 슬롯당 공급자가 하나라 공급자 이름이 필요 없고, 하류가 역할만 알면 되기 때문이다. `policy/`는 공급자 이름으로 둔다 (`fluent-korean.yaml`). 조각 합성이 가능해 공급자가 여럿일 수 있다. §7과 §14의 경로가 이 규칙을 따른다.

### 5.3 역할

인터페이스는 벤더가 아니라 역할 단위다. 하류는 "im-not-ai"가 아니라 "rewrite 절차"를 요청한다.

| 역할 | 담는 것 | 슬롯 | 현재 공급자 |
|---|---|---|---|
| `policy` | 본문, 변형(coding / not-coding), **선택 블록**, 원본 frontmatter | 조각 합성 가능 | fluent-korean |
| `procedure` | 단계, invariant, 입출력 계약, 참조 | **슬롯당 하나** | im-not-ai(rewrite), korean-skills(grammar), yoonmoon(diagnose) |
| `taxonomy` | 범주, 패턴, 심각도 | **슬롯당 하나** | im-not-ai(rewrite), yoonmoon(diagnose) |
| (검증 단계) `ruleset` | 결정론 규칙 | 미정 | 미정 |

- 형식을 맞추는 것이지 내용을 합치는 게 아니다. rewrite taxonomy와 diagnose taxonomy는 별개 슬롯이고 한 컨텍스트에 함께 올리지 않는다.
- **`policy`의 정규화 단위는 upstream이 배포한 단위와 같다.** 변형 파일 2개(`fluent-korean` = coding, `fluent-korean-not-coding`)와 README `## 세부 동작` 절의 **선택 블록 7개**다. 블록은 fluent-korean README의 문장이고 `normalized/policy/`에 둔다. 조립 쪽은 프로파일별로 어느 블록을 켤지만 고른다.
- **서브에이전트 조항은 블록이 아니다.** coding 변형 본문의 `## 추가 사항` 절이고 not-coding 변형에는 없다. not-coding 정책에도 이 조항을 붙일지는 P3 합성 규칙에서 정한다(붙이면 `selected`).

### 5.4 변환 등급

| 등급 | 허용 | 예 |
|---|---|---|
| `verbatim` | 문장 그대로, 위치만 옮김 | 기본값 |
| `selected` | 부분만 고름 | Claude Code 다중 에이전트 구성 부분을 뺌 |
| `adapted` | 문장을 바꿈. **불가피할 때만** | 원문을 `original`에 남기고 개수를 셈 |

`adapted` 개수는 우리가 upstream에서 얼마나 멀어졌는가의 지표다. P1에서 첫 실측을 한다.

### 5.5 출처

모든 조각에 붙는다.

```yaml
provenance:
  upstream: im-not-ai
  commit: <sha>
  path: <upstream 안의 파일>
  anchor: <구조적 위치 표지>          # 형식은 P1~P3에서 써 보고 P4에서 확정
  content_hash: sha256:<조각 해시>
  transform: verbatim | selected | adapted
```

앵커로 찾고 해시로 확인한다. 앵커는 줄 번호가 아닌 **구조적 위치 표지**다. upstream마다 조각을 가르는 표지가 달라서(제목, XML형 태그, 패턴 id, 굵은 라벨, 표 행 — 06b P0) **형식은 P1~P3에서 써 보고 P4에서 확정한다.** 지금 정해진 규칙은 셋이다.

1. 코드블록 안의 줄은 제목으로 치지 않는다.
2. 앵커는 파일 안에서 유일해야 한다. 유일하지 않으면 상위 위치까지 적는다.
3. 재추출 때 "앵커 없음"과 "해시 다름"을 다른 실패로 보고한다. 둘 다 빌드를 멈춘다.

### 5.6 lock

```yaml
# upstream/lock.yaml
- name: im-not-ai
  url: https://github.com/epoko77-ai/im-not-ai
  commit: <sha>
  license: <SPDX>
  license_checked: <날짜>
  roles: [procedure.rewrite, taxonomy.rewrite]
```

저장소 목록은 01a의 조사에서 온다 — `snflkd/fluent-korean`, `epoko77-ai/im-not-ai`, `DaleSeo/korean-skills`, `amondnet/yoonmoon`. **P0에서 URL과 라이선스를 실제로 확인한다.**

## 6. profiles와 presets

`assemble/`에 둔다. 우리의 것이다.

```yaml
# assemble/profiles/agent-reply.yaml
id: agent-reply
register: 에이전트가 사용자에게 하는 보고·설명
policy: policy/fluent-korean#coding          # normalized 참조
blocks: []                                   # normalized 의 선택 블록 id. 서브에이전트 조항은 coding 본문에 있다 (§5.3)
default_preset: standard
intensity: default
exempt: []
```

```yaml
# assemble/profiles/formal-report.yaml
id: formal-report
register: 사용자에게 전달되는 문서
policy: policy/fluent-korean#not-coding
blocks: [honorific]                          # 블록 id는 P3에서 정한다
default_preset: full
intensity: conservative
exempt: []            # stop-slop-ko 공급 여부 결정 전까지 비움 (§16)
```

```yaml
# assemble/presets.yaml
quick:    []
standard: [policy]
review:   [diagnose]
edit:     [rewrite, grammar]
full:     [policy, rewrite, grammar, diagnose]
```

`quick`은 06에서 비어 있다. 검증 단계에서 `gate`가 각 preset 끝에 들어오면 `quick = [gate]`가 된다 (§15).

**`policy`가 preset 항목으로서 런타임에 뜻하는 바는 정해지지 않았다.** 정책은 빌드타임에 파일로 주입된다 (§9). `ko-route`가 실행 중에 `policy` 단계를 만나면 할 일이 없거나, 산출물 경계에서 정책 본문을 다시 읽어 넣는 재주입(02a)이 된다. 둘 중 무엇인지는 결정 ②와 함께 P5에서 정한다 (§16).

`exempt`를 비운 이유: 이전 판본의 `[slop.cta_in_sns, slop.polite_email_ending]`는 stop-slop-ko의 규칙 id인데 공급자 목록에 stop-slop-ko가 없어 참조 대상이 없었다.

04와 형식을 공유한다. `gate`, `baseline`, `on_final_fail`, `watch`는 검증 단계에서 더한다.

## 7. skills

`dist/`의 `skills/<name>/SKILL.md`는 **빌드 산출물**이다. 두 원천을 합친다.

| 원천 | 들어가는 것 | 누구의 문장 |
|---|---|---|
| `upstream/normalized/procedure/<role>.yaml` | 절차 단계, upstream invariant | upstream |
| `upstream/normalized/taxonomy/<role>.yaml` | `references/taxonomy-<role>.md`로 렌더 | upstream |
| `assemble/skills/<name>.md` | `description` frontmatter, 호출 규약 | 우리 |

| skill | 절차 원천 | 참조 |
|---|---|---|
| `ko-route` | 없음 — 조립 쪽만 | 프로파일, 프리셋 |
| `ko-rewrite` | `procedure/rewrite` (im-not-ai) | `taxonomy/rewrite` |
| `ko-grammar` | `procedure/grammar` (korean-skills) | 미정. upstream에 `references/rules.md`·`common-errors.md`가 있으나 P0에서 본문을 읽지 않았다. P4에서 정한다 |
| `ko-diagnose` | `procedure/diagnose` (yoonmoon) | `taxonomy/diagnose` + 역할이 정해지지 않은 참조 3종 (아래) |

**절차가 taxonomy 밖의 자료를 참조한다.** yoonmoon detect는 `lread-rubric.md`(판정 틀), `katfishnet-research.md`(가중치 근거), `xdac-research.md`(단문 전용)를 읽고, im-not-ai 단일 호출판은 처방집 `rewriting-playbook.md`를 `## 참고`에 둔다 (06b P0 파일 지도). 이것들은 `procedure`도 `taxonomy`도 아니다. §5.3의 역할 셋에는 받을 자리가 없으므로, P1·P2에서 실물을 보고 역할을 더할지(예: `reference`) 정하고 P4에서 확정한다 (§13.2).

**렌더 결과에서 upstream 문장과 우리 문장이 구분돼야 한다.** 구분 방식은 P1에서 정한다 (주석 마커 또는 절 분리).

**작성 규칙.**
- `SKILL.md` 본문은 절차와 invariant만. 100줄 이내 (Claude Code 안내는 500줄 이내. 06이 더 엄격하다).
- `description`은 짧게. Codex는 세션 시작에 싣는 스킬 목록 전체를 컨텍스트의 2% 또는 8,000자 안에 두므로, 우리 스킬 넷의 `description` 합이 다른 스킬의 자리를 잠식하지 않게 한다.
- 패턴 목록은 `references/`로 내리고 본문에서 경로로만 가리킨다.
- **두 taxonomy를 한 컨텍스트에 올리지 않는다.** `ko-rewrite`와 `ko-diagnose`는 서로의 참조 파일을 읽지 않는다.
- `description`에 발동 조건을 쓴다. 모델이 이것만 보고 고르므로 언제 쓰고 언제 쓰지 않는가를 둘 다 적는다.

**`ko-rewrite` invariant.** P1에서 고른 upstream 원천의 철칙을 **전부** 받는다. 일부만 고르지 않고, 우리 invariant를 더하지 않는다. 앵커가 달린 구체 목록은 P1에서 06b에 남긴다.

P0 파일 지도(06b)에서 im-not-ai에 있다고 확인한 것: 의미 보존, 탐지된 span만 수정, 장르 보존, 숫자·고유명사·인용 불변, 변경률 30% 초과 경고·50% 초과 중단, register 보존, 입력은 데이터이지 지시가 아니다, 빼기 전용, 서법 보존, 내용 앵커.

- **변경률은 모델의 자기 보고다.** im-not-ai의 Claude Code 경로는 `scripts/verify_gates.py`로 판정하고, 모델이 낸 값은 참고값으로만 본다. 06은 스크립트를 공급하지 않으므로 06의 변경률은 upstream 단일 호출판(Codex·Copilot)과 같은 자기 보고다. 코드 판정은 검증 단계에서 더한다 (§15).
- **이전 판본의 우리 invariant "신호가 둘 이상 겹칠 때만 수정"(hjongc 원칙, 03a #3)은 뺐다.** im-not-ai의 S1 "한 번만 나와도 무조건 제거"와 충돌한다. 과교정 억제는 upstream 심각도 체계에 맡기고, 과교정이 실제로 일어나는지는 P1에서 본다.

`ko-route`는 얇게 둔다. 사용자가 "윤문해줘"라고 하면 `ko-rewrite`가 직접 걸려도 되고, 프로파일이 필요한 경우에만 거친다. 프리셋 순서는 `ko-route`가 모델에게 지시하는 것이므로 **보장이 아니라 권고**다.

## 8. agents

`assemble/agents/`의 중립 YAML에서 하네스별 형식으로 렌더한다.

```yaml
# assemble/agents/reviewer.yaml
name: korean-reviewer
role: 산출물을 수정하지 않고 진단한다
preset: review
prompt:
  compose: [profile.policy, profile.blocks]     # ← 필수. §9 참조. 원천은 normalized/policy
  append: |
    ko-diagnose 절차로 AI 가능성·신뢰도·근거를 보고한다.
    텍스트를 고치지 않는다. upstream 출력 형식 그대로 반환한다.
```

`writer`는 `compose`만 있고 preset이 없다. `editor`는 `preset: edit`에 rewrite → grammar 순서를 `append`에 적는다. `append`는 우리 문장이다.

| 하네스 | 렌더 형식 |
|---|---|
| Claude Code | `agents/<name>.md` — frontmatter + 시스템 프롬프트 본문 |
| Codex | `.codex/agents/<name>.toml` — `name`, `description`, `developer_instructions` |

**에이전트와 프로파일의 결합은 정해지지 않았다.** `compose`가 `profile.policy`를 가리키지만 어느 프로파일인지는 에이전트 YAML에 없다. 에이전트마다 프로파일 하나를 고정할지(`korean-reviewer` = agent-reply), 프로파일별로 렌더해 이름을 나눌지(`korean-reviewer-formal` 같은)는 §12 검사 3의 "같은 profile에 대해"가 무엇을 뜻하는지를 정하는 일이다. 결정 ②와 함께 P5에서 정한다 (§16).

## 9. 정책 주입

**06에서 가장 중요한 절이다.**

출력 스타일은 서브에이전트에 도달하지 않는다. fluent-korean coding 변형의 `## 추가 사항` 조항은 서브에이전트를 호출하기 전에 한국어 프롬프트가 지침을 지키는지 점검하라고 모델에게 부탁할 뿐, 정책을 서브에이전트에 넘기지 않는다. **구조적으로 출력 스타일이 애초에 거기 닿지 않는다.**

그러므로 정책 텍스트를 각 에이전트 정의에 **직접 써넣는 것이 선택이 아니라 필수**다.

| 주입 지점 | Claude Code | Codex |
|---|---|---|
| 메인 스레드 | `output-styles/<profile>.md` + `force-for-plugin: true` | `AGENTS.md` 절 (전역 또는 프로젝트) — 대안: `config.toml`의 `developer_instructions` (§2.2). P6에서 정한다 |
| 서브에이전트 | `agents/<name>.md` 본문에 정책 텍스트 포함 | `developer_instructions`에 포함 |
| 보조 채널 | — | MCP 서버 `instructions` 필드 |

**합성 규칙은 P3에서 확정한다** (§16 결정 ③). 정할 것: 선택 블록의 위치(README는 "지침 끝에 추가"하라고 안내한다), 블록 id, not-coding 정책에 서브에이전트 조항을 붙일지, `keep-coding-instructions` 값, 원본 frontmatter 보존 여부, **두 프로파일 중 어느 출력 스타일에 `force-for-plugin`을 켤지.** 출력 스타일은 하나만 활성이고 `force-for-plugin`이 여럿이면 먼저 로드된 것이 이긴다(§2.1). 프로파일 둘을 둘 다 강제할 수 없으므로 하나(agent-reply 예상)만 강제하고 다른 하나는 사용자 선택으로 둔다.

**분량 실측 (2026-09-14).** fluent-korean 변형 본문은 coding 6,317바이트, not-coding 5,932바이트다. 선택 블록 7개를 다 붙여도 Codex `AGENTS.md` 상한 32 KiB의 1/4 안에 든다. 분량 때문에 정책을 줄일 이유는 없다.

**메인 스레드 대안.** Claude Code는 플러그인 `settings.json`의 `agent` 키로 플러그인 에이전트를 메인 스레드로 올릴 수 있다. 출력 스타일보다 강하게 걸리지만 사용자의 메인 에이전트를 통째로 바꾸므로 기본값으로 쓰지 않는다. 설치 안내에 선택지로만 적는다.

**Codex의 `instructions` 채널.** Codex는 MCP 서버의 `instructions` 필드를 서버 전역 지침으로 읽는다. 시스템 프롬프트는 아니지만 세션 내내 유지된다. 이전 판본은 여기에 압축한 정책 요약(`adapted`)을 싣기로 했으나, 두 가지가 그 결정을 흔든다. fluent-korean README는 다른 환경에는 "파일 본문을 적절한 자리에 삽입"하라고 안내하고, 본문은 6 KB다(위). 요약을 새로 쓰지 않고 본문을 그대로(`verbatim`) 실을 수 있고, `AGENTS.md`가 이미 같은 본문을 나르므로 채널을 아예 두지 않을 수도 있다. 요약 / 본문 / 없음은 P6에서 정한다 (§16). 요약을 택하면 `adapted`이고 출처와 원문을 남긴다.

## 10. MCP 서버

06에서는 거의 비어 있다.

- **tools**: 없음. 검증 단계에서 `ko.gate`, `ko.features`, `ko.change_rate`, `ko.preserve`가 들어온다.
- **resources / prompts**: **쓰지 않는다.** Codex에 도달하지 않는다.
- **`instructions`**: 정책을 싣는다. 06에서 서버가 하는 유일한 일이다. 요약인지 본문인지, 채널을 둘지는 P6에서 정한다 (§9).

검증 단계에서 문서를 서빙하고 싶어지면 텍스트를 반환하는 tool로 만든다.

> **미확인.** Codex의 MCP resources 지원은 상태가 모호하다. 공식 문서 지원 목록에 없고, 이슈 #4956("클라이언트 계층은 `tools/list`와 `tools/call`만 발행한다")은 PR과 함께 닫혔으나 문서에 반영되지 않았다. **tools만 있다고 가정한다.** 나중에 확인되면 최적화로 더할 수 있고, 반대는 재작업이다.

## 11. hook과 최소 로거

검증 단계의 계측 장치는 오지 않는다. 재료가 쌓이기 시작하는 것만 지금부터다.

### 11.1 원칙

- 하네스 밖에서 돈다. 모델은 로거의 존재를 모른다.
- 판정하지 않고 차단하지 않는다.
- **transcript를 읽지 않는다.** hook 입력에서 점진적으로 조립한다.
- 토큰을 쓰지 않는다.

### 11.2 조립

| 레코드 항목 | 출처 hook | 필드 |
|---|---|---|
| `policy_on`, `injection_point`, `model` | `SessionStart` | 설정 상태. `model`은 Claude Code에서 선택 필드라 없으면 `unknown`. Codex는 공통 입력에 있다 |
| `task`, `instruction_lang` | `UserPromptSubmit` | 프롬프트 원문 |
| `task_type`, `tool_errors` | `PostToolUse` (누적) | 도구 이름·결과 |
| `output`, `harness_position: main-to-user` | `Stop` | `last_assistant_message` |
| `output`, `harness_position: sub-*`, 에이전트 | `SubagentStop` | `last_assistant_message`, `agent_type` (Claude Code 플러그인 에이전트는 `<플러그인>:<이름>` 꼴) |
| 레코드 확정·append | `SessionEnd` | — |

`profile`과 `upstream_versions`는 hook이 모르는 ko-quality 개념이다. **빌드가 `dist/`에 스탬프 파일을 남기고 로거가 그것을 읽는 방식**을 P7에서 확정한다.

### 11.3 레코드

```yaml
id: string
ts: datetime
profile: string                        # 빌드 스탬프에서
preset: string
policy_on: bool
injection_point: output-style | agents-md | agent-definition | none | unknown
upstream_versions: {name: commit}      # 빌드 스탬프 ← upstream/lock.yaml. 추측 아님
model: string
instruction_lang: ko | en | mixed
artifact_lang: ko | en | mixed
harness: claude-code | codex
harness_position: main-to-user | sub-to-orchestrator | sub-to-sub
agent_type: string?
task: string
task_type: coding | writing | null
task_type_method: rule
output: string
tokens: {output: int, method: estimate}   # hook 입력에 토큰 수가 없다. 문자 수 기반 추정 (§13.1)
upstream_report: string?
usable: bool
expect: null                           # 검증 단계에서 채움
```

`features`, `outcome`, `watch_hits`는 검증 단계의 것이다. 06의 레코드는 원문과 조건만 담는다.

### 11.4 저장과 금지

- `~/.ko-quality/logs/<profile>/<yyyy-mm>.jsonl`. **작업 트리 밖.**
- 에이전트에게 로그를 쓰게 하지 않는다.
- `task_type`을 LLM으로 분류하지 않는다.
- 비밀·개인정보는 캡처 단계에서 마스킹하고 `masked: true`를 남긴다.

### 11.5 설치

| 하네스 | 방법 |
|---|---|
| Claude Code | 플러그인이 `hooks/hooks.json`으로 나른다 |
| Codex | **플러그인 번들이 1순위 후보다** (`extensions.com.openai.hooks`). 대안은 설치 안내가 `.codex/hooks.json`을 쓰게 하는 설치 단계다. 어느 쪽이든 사용자의 hook 신뢰 검토가 필요하다. P6 실측 후 확정한다 |

> **확인됨 (2026-09-14).** Codex 플러그인은 hook을 번들할 수 있다 (§2.2). 신뢰 검토가 설치 흐름과 로거 가동에 주는 영향, 다른 Agent Plugins 클라이언트가 `extensions.com.openai`를 무시하는지, 제거 절차와의 관계는 P6에서 실측한다.

## 12. 빌드와 배포

```text
upstream/normalized/ ─┐
                      ├─ build/claude_code.py ──→ dist/claude-code/
assemble/ ────────────┤
                      └─ build/agent_plugin.py ─→ dist/agent-plugin/
```

| 산출물 | 대상 | 담기는 것 |
|---|---|---|
| `dist/claude-code/` | Claude Code | `.claude-plugin/plugin.json`, `skills/`, `agents/`, `output-styles/`, `hooks/hooks.json`, `.mcp.json`, 빌드 스탬프 |
| `dist/agent-plugin/` | Codex (Agent Plugins 클라이언트. 다른 클라이언트는 시험하지 않는다, §2.4) | `plugin.json`, `skills/`, `mcp.json`, `install/`, 빌드 스탬프 |

`install/`에는 표준이 담지 못하는 것이 들어간다 — `.codex/agents/*.toml`(Codex 플러그인은 서브에이전트를 싣지 못한다, §2.2), `AGENTS.md`에 붙일 절. hook을 플러그인에 번들하지 않기로 하면 `.codex/hooks.json`도 여기에 들어간다 (§11.5, P6).

`.mcp.json`·`mcp.json`이 가리키는 서버는 06에서 tool이 없다. Claude Code도 서버 `instructions`를 세션 시작에 싣지만(§13.2) 정책은 출력 스타일과 에이전트 정의로 이미 받으므로, Claude Code 산출물에 서버를 실을지는 P7에서 정한다 (§16).

**검사 (필수).**

1. **출처:** 재추출 시 모든 조각의 `content_hash`가 일치한다. 불일치하면 빌드 중단.
2. **정책 동일:** 같은 profile에 대해 두 산출물의 정책 텍스트가 문자열로 동일하다. 비교 대상은 본문이다. 하네스별 frontmatter(`force-for-plugin` 등)와 감싸는 마커는 뺀다.
3. **에이전트 동일:** 같은 profile에 대해 두 산출물의 에이전트 시스템 프롬프트가 동일하다.
4. **스킬 동일:** `skills/`가 두 산출물에서 바이트 동일하다.

2~4는 빌드가 렌더만 하고 내용을 만들지 않는다는 것을, 1은 upstream 문장이 조용히 바뀌지 않았다는 것을 강제한다.

**동작 확인.** 위 검사는 빌드만 본다. 플러그인이 실제로 걸리는지는 `claude plugin eval`로 on/off를 돌려 확인한다. 도입 범위는 P5에서 정한다 (§16).

**제거.** Claude Code는 플러그인 비활성화로 끝난다. Codex는 `install/`이 쓴 파일과 `AGENTS.md` 절을 되돌리는 절차가 필요하다 — P6에서 마커 방식으로 정한다.

## 13. 근사치와 미확인

**이 절은 스펙의 일부다.** 아래 항목은 정확한 값이 아니거나 확인되지 않았다. 검증 단계에서 threshold를 걸기 전에 각각을 다시 본다.

### 13.1 근사치 — 값은 나오지만 정확하지 않다

| 항목 | 왜 근사치인가 | 다룰 방법 |
|---|---|---|
| `context_en_ratio` | **시스템 프롬프트가 hook 입력에 보이지 않는다.** `PostToolUse`로 도구 출력은 누적할 수 있지만 시스템 프롬프트와 skill 본문의 영어량은 관측 불가 | 06에서는 **레코드에서 뺀다.** 검증 단계에서 되살릴 때 "도구 출력 기준 영어 비율"로 이름과 정의를 바꾼다 |
| `task_type` | 도구 호출 규칙(Edit/Write 있으면 coding)은 근사다. 문서 편집 작업도 coding으로 잡힌다 | 값과 함께 `task_type_method: rule`을 남긴다. LLM 분류로 도망가지 않는다 |
| `instruction_lang` | `UserPromptSubmit`의 사용자 입력만 본다. 시스템 컨텍스트와 이전 턴의 언어는 반영되지 않는다 | 정의를 "직전 사용자 입력의 한글 비율"로 좁혀 적는다 |
| `artifact_lang`의 mixed | 코드 + 한국어 주석 산출물에서 한국어 span 추출이 불완전하면 `output`이 오염된다 | 주석·문자열 리터럴·마크다운 문단만 추출하고 코드 토큰은 버린다. 추출 실패 시 `usable: false` |
| `output`의 순도 | `last_assistant_message`는 모델 생성분이지만 사용자 입력 인용이나 도구 출력 붙여넣기가 섞일 수 있다 | 인용 블록과 코드 블록을 제거한 뒤 한국어 어절 20개 미만이면 버린다 |
| `tokens.output` | **hook 입력에 토큰 수가 없다.** Claude Code·Codex 모두 `Stop`·`SubagentStop`·`SessionEnd` 입력에 usage가 없다. 예외는 Claude Code에서 `Agent` 도구의 `PostToolUse`가 그 서브에이전트 호출의 `usage`를 주는 것뿐 | `last_assistant_message`의 문자 수로 추정하고 `method: estimate`를 남긴다. 서브에이전트는 `Agent` 도구 `PostToolUse`의 `usage`를 쓸 수 있으면 `method: agent_tool` |
| `harness_position`의 `sub-to-sub` | Claude Code는 서브에이전트 중첩을 허용하지만(§2.1) `SubagentStop` 입력에 부모가 없다. 같은 층의 병렬 서브에이전트와 중첩을 hook 순서만으로 가를 수 없다 | 06에서는 `sub-*`를 `sub-to-orchestrator`로 적고 `sub-to-sub`는 비워 둔다. 판별 방법은 P7에서 찾고, 없으면 값 자체를 뺀다 |
| 변경률 | 모델이 im-not-ai 절차에 따라 스스로 낸 값이다. 우리가 계산한 것이 아니고, upstream의 Claude Code 경로도 이 값을 참고값으로만 본다(판정은 스크립트) | `upstream_report`에 원문 그대로 두고 별도 필드로 올리지 않는다. 코드 판정은 검증 단계 `ko.change_rate` (§15) |
| Codex `instructions`의 정책 요약 | 요약을 쓰기로 하면 원문이 아니다 | `adapted`로 분류하고 원문과 출처를 남긴다. 본문을 그대로 싣거나 채널을 빼면 이 행은 사라진다 (§9, P6) |

### 13.2 미확인 — 확인 시점이 정해져 있다

| 항목 | 상태 | 가정 | 확인 시점 |
|---|---|---|---|
| upstream 저장소 URL과 라이선스 | **확인됨.** 4종 모두 MIT (2026-09-14, 06b P0) | — | P0 완료 |
| upstream 파일 구조 | P0 지도 완료(06b). 제목으로 찾을 수 없는 조각이 있음 | 구조적 위치 표지로 찾을 수 있음 (§5.5) | P1~P3 실측, P4 확정 |
| `adapted`가 필요한 양 | 모름 | 적음 | P1 |
| Codex MCP resources | 문서 지원 목록에 없음. 이슈는 닫혔으나 문서 미반영 | 없음 | P6 재확인 |
| Codex 플러그인의 hook 번들 | 문서에 있음 (2026-09-14). 사용자 신뢰 검토가 필요 | 가능 | P6 실측 |
| 절차가 참조하는 rubric·연구 노트의 역할 | yoonmoon detect 참조 3종, im-not-ai 처방집. `procedure`·`taxonomy` 어느 쪽도 아님 (§7) | 새 역할이 필요할 수 있음 | P1·P2 실측, P4 확정 |
| tool 없는 MCP 서버의 `instructions`가 모델에 닿는지 | Codex 문서는 tools와 함께 쓴다고만 적음. Claude Code는 세션 시작에 서버 instructions를 싣는다(2026-09-14 확인) | 닿지 않을 수 있음 | P6 (Codex), P7 (Claude Code) |
| Codex 서브에이전트 중첩 | 문서에 없음 | 모름 | P6 |
| Codex `injection_point` 구분 | `AGENTS.md`와 `developer_instructions`를 로거가 구분할 수 있는지 모름 | 못 읽으면 `unknown` | P7 |
| 하네스 사양 전반 | 2026-09-14 재확인 (06b P0) | §2 그대로 | P6에서 Codex 재확인 |

### 13.3 구조적 한계 — 고칠 수 없다

- **정책 효과는 06에서 측정되지 않는다.** 결함이 아니라 범위다.
- **서브에이전트 조항은 여전히 조항이다.** 정책을 에이전트 정의에 써넣는 것으로 서브에이전트 **한 겹**은 해결되지만, 그 서브에이전트가 또 다른 에이전트를 띄울 때 정책을 넘기는 것은 여전히 모델에게 부탁하는 일이다. `sub-to-sub` 경로는 구조로 보장되지 않는다.
- **프리셋 순서는 권고다.** `ko-route`가 모델에게 지시하는 것이라 실행 순서를 강제하지 못한다.
- **초기 로그에는 `sub-*` 샘플이 적다.** 서브에이전트를 실제로 쓰는 작업에서만 생긴다.
- **06의 로그에는 대조군이 없다.** 로거는 플러그인이 켜진 세션에서만 돌므로 `policy_on`은 사실상 항상 참이다. 04a가 로그의 조건으로 둔 "간헐적으로 policy를 끄고 돌린다"(off 교대)는 검증 단계에서 더한다 (§15). 그때까지 쌓이는 것은 on 표본뿐이고, 06의 레코드는 A/B가 아니라 분포와 형식의 재료다.

## 14. 프로토타입 계획

**구체에서 시작해 추상으로 간다.** 스키마를 먼저 설계하지 않는다. 실물 셋에서 스키마를 역산하고, 보지 않은 네 번째로 추상화를 시험한다 (06a).

### 14.1 규칙

- **각 P를 시작하기 전에** 이 절, `5-preflight/flow.md`, `6-build/`의 최신 기록을 읽는다.
- **각 P가 끝나면** 발견을 `6-build/P<n>_<이름>.md`에 남긴다. 스펙과 달랐던 것, 스펙이 몰랐던 것, 임시 형식에서 불편했던 것, 구현이 내린 판단과 확신 수준. (P0의 기록은 `5-preflight/06b_built_prototype.md`에 있다. 프로세스 재배치 전의 규칙은 06b에 덧붙이는 것이었다.)
- **실측 문서는 스펙을 고치지 않는다.** 구현(6-build)에 들어가면 06은 개정하지 않는다. 스펙을 바꿀 만한 발견은 7-review를 거쳐 다음 시대로 간다. 구현 중 판단은 `CLAUDE.md`의 기준으로 자율적으로 내린다.
- 각 P의 끝나는 조건을 넘기지 못하면 다음 P로 가지 않는다.

### 14.2 단계

**P0 — 사전 확인**
- 저장소 초기화 (`git init`, `.gitignore`에 `upstream/.cache/`)
- upstream 4종의 URL·기본 브랜치 HEAD 커밋·LICENSE 확인 → `upstream/lock.yaml`
- `upstream/.cache/`에 받아오기
- **파일 지도:** 각 upstream에서 정책·절차·taxonomy·선택 블록이 어느 파일의 어느 제목 아래 있는지
- §2 하네스 사양 재확인. 달라졌으면 06b에 기록
- *끝나는 조건:* lock에 4종이 커밋·라이선스와 함께 있고 파일 지도가 06b에 있다
- *멈추는 조건:* MIT가 아닌 upstream이 있으면 그 역할의 공급 방식을 사용자와 정한다

**P1 — 수직 슬라이스: im-not-ai → `ko-rewrite`**
- **절차 원천 선택:** 오케스트레이터(`skills/humanize-korean/SKILL.md`)에서 골라낼지, 단일 호출판(`codex/skills/humanize-korean/SKILL.md`)을 쓸지 (06b P0)
- 스키마 없이 임시 YAML로 손 추출 → `upstream/normalized/procedure/rewrite.yaml`, `taxonomy/rewrite.yaml`. 모든 조각에 §5.5 출처
- `assemble/skills/ko-rewrite.md` — `description`, 호출 규약
- 손으로 `dist/claude-code/` 최소형: `.claude-plugin/plugin.json` + `skills/ko-rewrite/SKILL.md` + `references/taxonomy-rewrite.md`
- upstream 문장과 우리 문장의 구분 방식 정하기
- `claude --plugin-dir dist/claude-code`로 로드하고 윤문 요청 3~5건
- *확인:* 스킬이 걸리는가 / 절차를 따르는가 / 참조 파일을 필요할 때만 읽는가 / 변경률 보고가 나오는가
- *06b 기록:* `adapted` 개수와 위치, 앵커가 버텼는지, 임시 YAML에서 불편했던 필드, 100줄 제한, 받은 invariant 목록과 앵커, 과교정이 관측됐는지 (§7)
- *끝나는 조건:* 한 건 이상 실제 윤문이 절차대로 수행된다

**P2 — 같은 역할, 다른 벤더: yoonmoon → `ko-diagnose`**
- P1의 임시 형식을 그대로 써본다. **안 맞는 곳이 추상화 재료다** — 06b에 기록
- `normalized/procedure/diagnose.yaml`, `taxonomy/diagnose.yaml`, `ko-diagnose` 스킬
- 두 taxonomy가 서로 참조하지 않는지 확인
- detect가 참조하는 rubric·연구 노트 3종을 어느 역할로 받을지 (§7). P1의 처방집과 함께 P4 추상화 재료
- *끝나는 조건:* 진단 보고가 텍스트 수정 없이 나온다

**P3 — 다른 성격의 역할: fluent-korean → `policy`**
- `normalized/policy/fluent-korean.yaml` — 두 변형과 README 선택 블록 7종
- **결정 ③ 확정:** 선택 블록 위치와 id, not-coding 정책의 서브에이전트 조항, `keep-coding-instructions`, 원본 frontmatter, 두 프로파일 중 `force-for-plugin`을 켤 것 (§9)
- `output-styles/agent-reply.md` + `agents/korean-reviewer.md`에 같은 정책 텍스트
- *확인:* 메인 대화와 서브에이전트 **양쪽에** 정책이 걸리는가 (§2.1 제약 실측)
- *끝나는 조건:* 결정 ③이 06b에 있고, 06 반영 여부를 사용자와 정했다

**P4 — 추상화**
- P1~P3 실물에서 `upstream/interface/{policy,procedure,taxonomy}.schema.yaml` 역산
- 추출기 코드화 `upstream/extractors/*.py` — 앵커 탐색, 해시, 등급
- **손 산출물과 코드 산출물의 diff가 0**
- **추상화 시험:** korean-skills grammar를 **스키마만 보고** 추출. 스키마를 고치지 않고 들어가면 성공. 고쳐야 하면 무엇을 왜 고쳤는지 06b에 기록
- **업데이트 흐름 실측:** lock의 커밋 하나를 올려 재추출하고 normalized diff가 읽히는지 본다
- *끝나는 조건:* 네 번째 벤더가 들어갔고 §12 검사 1이 돈다

**P5 — 조립과 Claude Code 빌드**
- **결정 ② 확정** (빌드타임 예상). 함께: 에이전트와 프로파일의 결합 (§8), presets의 `policy` 항목이 런타임에 뜻하는 것 (§6)
- `assemble/` 완성: profiles 2, presets, agents 3, skills 템플릿 4
- `build/claude_code.py` → `dist/claude-code/` 재생성, P1~P3 손 산출물과 diff 확인
- §12 검사 2~4
- `claude plugin eval` 도입 범위 결정
- 제거 절차 문서화
- *끝나는 조건:* §14.3 구현 완료 중 Claude Code 부분

**P6 — Codex 빌드**
- `build/agent_plugin.py` → `dist/agent-plugin/` + `install/`
- `AGENTS.md` 절 삽입·제거를 마커로 멱등하게
- Codex MCP resources 재확인
- **`instructions` 채널 확정:** 요약 / 본문 / 없음 (§9)
- **hook 배포 확정:** 플러그인 번들(`extensions.com.openai.hooks`) 실측 — 신뢰 검토, 다른 클라이언트의 `extensions.com.openai` 처리, 제거 절차와의 관계. 안 되면 `install/`의 `.codex/hooks.json` (§11.5)
- §12 검사 2~4 양쪽
- *끝나는 조건:* Codex에서 정책이 메인과 서브에이전트에 걸리고 스킬이 호출된다

**P7 — 서버와 최소 로거**
- `server/` — `instructions`만
- 빌드 스탬프 형식 확정, 로거가 `profile`과 `upstream_versions`를 읽는 방식
- `logger/` — §11 조립, 양쪽 hook 배선. `tokens` 추정, `sub-to-sub` 판별 여부 (§13.1)
- Claude Code 산출물에 tool 없는 서버를 실을지 (§12)
- *끝나는 조건:* `~/.ko-quality/logs/`에 `usable: true` 레코드가 양쪽 하네스에서 쌓인다

### 14.3 완료 기준

- **구현 완료:** 두 `dist/`가 각 하네스에 설치되고, 정책이 메인과 서브에이전트 양쪽에 걸리며, `korean-reviewer`와 `korean-editor`가 호출되고, §12 검사 4종이 통과한다. (P6 끝)
- **계획 완료:** 위에 더해 로거 레코드가 쌓인다. (P7 끝)

## 15. 검증 단계로 가는 길

06은 검증 단계의 부분집합이다. 형식을 공유하고 절만 더한다. 검증 단계 문서의 번호는 열 때 정한다.

| 더하는 것 | 어디에 |
|---|---|
| `ruleset` 역할 | `upstream/interface/`, `normalized/ruleset/` |
| `features.py` (측정) | `logger/` — threshold 없이 |
| `watch:` 절 (표시만 하는 threshold) | `assemble/profiles/*.yaml` |
| `outcome` (작업 결과) | 레코드 |
| `ko.gate` 외 MCP tool | `server/` — tools로만 |
| `gate:` 절 | `assemble/profiles/*.yaml` — `watch:`에서 키 이름만 바꾼다 |
| off 교대 (대조군) | `logger/` — 05a의 층화 축 2개 |
| `gate` 단계 | `assemble/presets.yaml` 각 preset 끝. `quick: []`이 그 자리다 |
| eval runner, cases | 새 디렉터리 |

`05a_findings_measurement.md`가 검증 단계의 준비 문서다. 판정과 측정을 가르는 기준, 측정이 판정으로 새는 네 문, `watch:`의 승격 조건이 거기 있다.

## 16. 결정 현황

**구현 중 이 표를 갱신한다.** 새 세션은 여기서 무엇이 정해졌고 무엇이 열려 있는지 확인한다.

### 16.1 정해진 것

| 결정 | 근거 |
|---|---|
| 산출물은 설치하면 쓰이는 도구. 검증은 다음 단계 | §1 |
| 층: 공급 / Skill / MCP(tools만, 검증 단계부터) / 하네스별 렌더 | §3, 06a |
| 정책은 에이전트 정의마다 직접 주입 | §9, §2.1 |
| 로거는 hook 입력 조립. transcript 금지 | §11, §2.3 |
| upstream은 lock으로 받아오고 정규화 산출물만 커밋 | §5, 06a |
| 인터페이스는 역할 단위. `procedure`·`taxonomy`는 슬롯당 공급자 하나 | §5.3, 06a |
| 변환 3등급, 문장 변환 금지가 기본 | §5.4, 06a |
| 출처는 앵커 + 해시 | §5.5, 06a |
| 추상화는 프로토타입 뒤. 네 번째 벤더가 시험 | §14, 06a |
| ① upstream 텍스트 복사/동봉/참조 → 공급 층으로 해소 | 06a |
| `policy` 정규화 단위는 upstream 배포 단위: 변형 2개 + README 선택 블록 7개. 서브에이전트 조항은 coding 본문 | §5.3, 06b P0 |
| 앵커는 구조적 위치 표지. 규칙 3개만 확정, 형식은 P4 | §5.5, 06b P0 |
| `ko-rewrite` invariant는 upstream 원천의 철칙 전부. 우리 invariant 없음(hjongc 원칙 제외) | §7, 06b P0 |
| 06의 변경률은 모델 자기 보고. 코드 판정은 검증 단계 | §1, §7, §13.1, 06b P0 |
| upstream 4종 URL·커밋·라이선스 — 모두 MIT, `upstream/lock.yaml`에 고정 (2026-09-14) | 06b P0 |

### 16.2 열린 것

| 결정 | 기울기 | 정하는 곳 |
|---|---|---|
| im-not-ai 절차 원천 (오케스트레이터 / 단일 호출판) | — | P1 |
| upstream 문장과 우리 문장의 렌더 구분 방식 | — | P1 |
| 앵커 형식 | — | P1~P3 시험, P4 확정 |
| ③ 정책 합성 규칙 | — | P3 |
| ② 프로파일 런타임 / 빌드타임 | 빌드타임 | P5 |
| `claude plugin eval` 도입 범위 | — | P5 |
| Codex 메인 스레드 주입 지점 (`AGENTS.md` 전역 / 프로젝트 / `config.toml` `developer_instructions`) | — | P6 (§9) |
| Codex 제거 절차 (마커) | — | P6 |
| Codex hook 배포 (플러그인 번들 / 설치 단계) | 플러그인 번들 | P6 |
| 빌드 스탬프 형식, 로거의 profile 인식 | 스탬프 파일 | P7 |
| stop-slop-ko를 `policy` 조각 공급자로 넣을지 | — | P3 이후, `exempt` 복구와 함께 |
| 두 프로파일 중 `force-for-plugin`을 켤 출력 스타일 | agent-reply | P3, 결정 ③ (§9) |
| 에이전트와 프로파일의 결합 (고정 / 프로파일별 렌더) | — | P5 (§8) |
| presets의 `policy` 항목이 런타임에 뜻하는 것 (없음 / 재주입) | — | P5 (§6) |
| Codex `instructions` 채널 (요약 / 본문 / 없음) | — | P6 (§9) |
| 절차가 참조하는 rubric·연구 노트의 역할 | — | P1·P2 실측, P4 (§7) |
| Claude Code 산출물에 tool 없는 MCP 서버를 실을지 | — | P7 (§12) |
| `sub-to-sub` 판별 방법 (없으면 값 삭제) | — | P7 (§13.1) |
