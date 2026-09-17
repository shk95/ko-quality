# ko-quality — Codex 플러그인 (Agent Plugins)

빌드 산출물입니다. 직접 고치지 말고 저장소 루트에서 `python3 -m build.agent_plugin`으로 다시 만듭니다.

## 무엇이 들어 있나

프로파일마다 디렉터리가 하나씩 있습니다(0.2.0). **둘 중 하나만 설치합니다.** Codex에는 출력 스타일이 없어서, 메인 대화의 정책은 설치기가 `AGENTS.md`에 넣는 절이 나릅니다.

| 플러그인 | 프로파일 | 메인 대화의 정책 |
|---|---|---|
| `ko-quality` (`agent-reply/`) | agent-reply | fluent-korean 코딩판. 사용자에게 하는 간결한 코딩 답변 |
| `ko-quality-formal` (`formal-report/`) | formal-report | fluent-korean 비코딩판 + 존대 블록. 사용자를 사용자님으로 부르는 높임말 |

Codex 플러그인은 스킬만 나를 수 있습니다. 메인 대화의 정책과 서브에이전트 정의는 플러그인에 실을 수 없어서 `install/`에 따로 있습니다.

| 경로 | 무엇 | 어떻게 들어가나 |
|---|---|---|
| `skills/` | `ko-rewrite`, `ko-diagnose`, `ko-grammar`, `ko-route` | 플러그인 설치 |
| `install/AGENTS.section.md` | 프로파일 정책 (`<!-- ko-quality:begin … -->` ~ `<!-- ko-quality:end -->`) | `install/ko_quality_codex.py` |
| `install/.codex/agents/*.toml` | `korean-reviewer`, `korean-writer`, `korean-editor` | `install/ko_quality_codex.py` |

에이전트는 두 프로파일 모두 **agent-reply 정책**을 담습니다. 에이전트의 답은 사용자가 아니라 메인 대화로 돌아가기 때문입니다.

## 설치

```sh
codex plugin marketplace add <저장소 경로>/dist/agent-plugin
codex plugin add ko-quality@ko-quality                               # 또는 ko-quality-formal@ko-quality
python3 <저장소 경로>/dist/agent-plugin/agent-reply/install/ko_quality_codex.py install   # formal이면 formal-report/install/…
```

`ko_quality_codex.py install`은 기본으로 전역에 설치합니다: `$CODEX_HOME/AGENTS.md`(없으면 `~/.codex/AGENTS.md`)에 정책 절을 넣고 `$CODEX_HOME/agents/`에 에이전트 파일을 둡니다. 한 프로젝트에만 쓰려면 `--scope project --project <디렉터리>`를 줍니다(`<디렉터리>/AGENTS.md`, `<디렉터리>/.codex/agents/`).

- 여러 번 실행해도 절은 하나만 남습니다. 다른 프로파일로 다시 설치하면 절이 그 자리에서 바뀝니다.
- 기존 AGENTS.md 내용은 그대로 두고 끝에 절을 붙입니다.
- 같은 이름의 에이전트 파일이 이미 있고 ko-quality가 쓴 것이 아니면 덮어쓰지 않고 건너뜁니다.
- `python3 … status`로 설치 상태를 봅니다.

### 에이전트를 쓰려면: `multi_agent_v2`

**에이전트는 `multi_agent_v2`를 켜야 불립니다.** 설치기는 이 설정을 쓰지 않으니 `~/.codex/config.toml`에 직접 넣습니다.

```toml
[features]
multi_agent_v2 = true
```

- 기본값(`multi_agent`)에서는 `codex exec`에 에이전트를 띄우는 도구가 없어서, 모델이 메인 대화에서 직접 검토합니다.
- `codex exec --ephemeral`로 실행하면 v2에서도 에이전트 호출이 "no thread with id"로 실패합니다. 에이전트를 쓸 때는 `--ephemeral`을 빼 주세요.
- 0.154.0의 `codex exec`와 전역 에이전트 파일에서 확인했습니다. 대화형 세션과 프로젝트 범위 에이전트는 아직 확인하지 못했습니다.

## 제거

```sh
python3 <저장소 경로>/dist/agent-plugin/agent-reply/install/ko_quality_codex.py uninstall   # 설치할 때 준 --scope와 같게
codex plugin remove ko-quality@ko-quality
codex plugin marketplace remove ko-quality
```

`uninstall`은 정책 절과 자신이 쓴 에이전트 파일만 지웁니다. 설치 때 AGENTS.md를 새로 만들었고 다른 내용이 없으면 파일도 지웁니다. `codex plugin remove` 뒤에는 빈 `~/.codex/plugins/cache/ko-quality/` 디렉터리가 남을 수 있습니다(0.154.0에서 확인). 지워도 됩니다. `multi_agent_v2` 설정은 다른 곳에서 쓰지 않는다면 직접 지웁니다.

## 알아둘 것

- 로그: 플러그인은 hook으로 로거(`logger/ko_quality_log.py`)를 돌립니다. Codex는 플러그인 hook을 처음 한 번 `/hooks`에서 신뢰해야 실행합니다. 메인 답변과 서브에이전트 답변마다 레코드 한 줄을 `~/.ko-quality/logs/<연-월>.jsonl`에 남깁니다. `KO_QUALITY_HOME`으로 위치를 바꿀 수 있고 `~`도 풀어 씁니다. 프롬프트와 답변 원문이 들어가며, API 키·토큰·이메일·전화번호·주민등록번호·카드 번호 꼴과 경로 속 홈 디렉터리는 가립니다. 가림은 최선의 노력일 뿐이고 이름은 가리지 않습니다. 로거는 판정하거나 막지 않고, 실패해도 세션에 영향을 주지 않습니다.
- 서브에이전트는 자연어로 위임합니다("korean-reviewer 에이전트를 띄워서 …").
- 출처: 플러그인 안의 upstream 문장은 고치지 않았습니다. 어느 줄이 upstream인지는 `skills/*/SKILL.provenance.yaml`과 `provenance/policy.yaml`에 있습니다. upstream 4종은 모두 MIT이고 커밋은 `upstream/lock.yaml`에 고정돼 있습니다.
