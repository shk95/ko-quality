# ko-quality — Codex 플러그인 (Agent Plugins)

빌드 산출물입니다. 직접 고치지 말고 저장소 루트에서 `python3 -m build.agent_plugin`으로 다시 만듭니다.

## 무엇이 들어 있나

프로파일마다 디렉터리가 하나씩 있습니다. **둘 중 하나만 설치합니다.**

| 플러그인 | 프로파일 | 정책 | 
|---|---|---|
| `ko-quality` (`agent-reply/`) | agent-reply | fluent-korean 코딩판 |
| `ko-quality-formal` (`formal-report/`) | formal-report | fluent-korean 비코딩판 + 존대 블록 |

Codex 플러그인은 스킬만 나를 수 있습니다. 메인 대화의 정책과 서브에이전트 정의는 플러그인에 실을 수 없어서 `install/`에 따로 있습니다.

| 경로 | 무엇 | 어떻게 들어가나 |
|---|---|---|
| `skills/` | `ko-rewrite`, `ko-diagnose`, `ko-grammar`, `ko-route` | 플러그인 설치 |
| `install/AGENTS.section.md` | 프로파일 정책 (`<!-- ko-quality:begin … -->` ~ `<!-- ko-quality:end -->`) | `install/ko_quality_codex.py` |
| `install/.codex/agents/*.toml` | `korean-reviewer`, `korean-writer`, `korean-editor` | `install/ko_quality_codex.py` |

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

## 제거

```sh
python3 <저장소 경로>/dist/agent-plugin/agent-reply/install/ko_quality_codex.py uninstall   # 설치할 때 준 --scope와 같게
codex plugin remove ko-quality@ko-quality
codex plugin marketplace remove ko-quality
```

`uninstall`은 정책 절과 자신이 쓴 에이전트 파일만 지웁니다. 설치 때 AGENTS.md를 새로 만들었고 다른 내용이 없으면 파일도 지웁니다. `codex plugin remove` 뒤에는 빈 `~/.codex/plugins/cache/ko-quality/` 디렉터리가 남을 수 있습니다(0.154.0에서 확인). 지워도 됩니다.

## 알아둘 것

- 로그: 플러그인은 hook으로 최소 로거(`logger/ko_quality_log.py`)를 돌립니다. Codex는 플러그인 hook을 처음 한 번 `/hooks`에서 신뢰해야 실행합니다. 메인 답변과 서브에이전트 답변마다 레코드 한 줄을 `~/.ko-quality/logs/<프로파일>/<연-월>.jsonl`에 남깁니다(`KO_QUALITY_HOME`으로 위치를 바꿀 수 있습니다). 프롬프트와 답변 원문이 들어가며, API 키·토큰·이메일 꼴은 `[masked]`로 가립니다. 로거는 판정하거나 막지 않고, 실패해도 세션에 영향을 주지 않습니다. Codex에서 레코드가 실제로 쌓이는지는 아직 확인하지 못했습니다(`design/01-toolkit/6-build/P7_server-logger.md`).

- 서브에이전트는 이름으로 부르는 것이 아니라 자연어로 위임합니다("korean-reviewer 에이전트를 띄워서 …"). 0.154.0에서 전역 에이전트 파일로는 호출이 확인됐습니다. 모델과 설정에 따라 호출이 실패할 수 있습니다(자세한 내용은 저장소의 `design/01-toolkit/6-build/P6_codex-build.md`).
- 출처: 플러그인 안의 upstream 문장은 고치지 않았습니다. 어느 줄이 upstream인지는 `skills/*/SKILL.provenance.yaml`과 `provenance/policy.yaml`에 있습니다. upstream 4종은 모두 MIT이고 커밋은 `upstream/lock.yaml`에 고정돼 있습니다.
