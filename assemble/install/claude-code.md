# ko-quality — Claude Code 플러그인

빌드 산출물입니다. 직접 고치지 말고 저장소 루트에서 `python3 -m build.claude_code`로 다시 만듭니다.

## 무엇이 들어 있나

플러그인은 `ko-quality` 하나입니다(0.2.0). 두 프로파일이 **선택할 수 있는 출력 스타일**로 들어 있고, 어느 쪽도 강제하지 않습니다.

| 출력 스타일 | 프로파일 | 메인 대화에 적용되는 정책 | 기본 프리셋 |
|---|---|---|---|
| `ko-quality:agent-reply` | agent-reply | fluent-korean 코딩판. 사용자에게 하는 간결한 코딩 답변 | standard |
| `ko-quality:formal-report` | formal-report | fluent-korean 비코딩판 + 존대 블록. 사용자를 사용자님으로 부르는 높임말 | full |

그 밖에 스킬 넷(`ko-rewrite`, `ko-diagnose`, `ko-grammar`, `ko-route`)과 에이전트 셋(`ko-quality:korean-reviewer`, `ko-quality:korean-writer`, `ko-quality:korean-editor`)이 들어 있습니다. 에이전트는 어느 스타일을 고르든 **agent-reply 정책**을 담습니다. 에이전트의 답은 사용자가 아니라 메인 대화로 돌아가기 때문입니다. formal-report를 골랐다면 메인 대화가 그 보고를 높임말로 다시 전합니다.

## 설치

이 디렉터리(`dist/claude-code`)를 로컬 마켓플레이스로 추가하고 플러그인을 설치합니다.

```sh
claude plugin marketplace add <저장소 경로>/dist/claude-code
claude plugin install ko-quality@ko-quality
```

`--scope local`을 붙이면 현재 프로젝트에만 설치됩니다(`.claude/settings.local.json`). `--scope project`는 커밋되는 `.claude/settings.json`에 씁니다.

## 스타일 선택: 프로젝트마다 한 번

**설치만으로는 메인 대화에 정책이 걸리지 않습니다.** 스킬과 에이전트는 바로 쓸 수 있지만, 메인 대화의 정책은 스타일을 골라야 적용됩니다. 프로젝트에서 Claude Code를 띄우고 한 번 실행합니다.

```text
/output-style ko-quality:agent-reply
```

또는 `/output-style ko-quality:formal-report`. 선택은 그 프로젝트의 `.claude/settings.local.json`에 `"outputStyle": "ko-quality:agent-reply"`로 남고, 이후 그 프로젝트의 모든 세션에 적용됩니다. 다음 턴부터 바뀝니다.

- 이름은 반드시 `ko-quality:<스타일>` 꼴로 씁니다. `agent-reply`만 쓰면 적용되지 않습니다.
- 커밋된 `.claude/settings.json`에 둔 선택보다 `settings.local.json`의 선택이 이깁니다.
- 스타일 설정은 Claude Code를 띄운 디렉터리의 것만 읽습니다. 하위 디렉터리에서 띄우면 적용되지 않습니다.

## 제거

```sh
claude plugin uninstall ko-quality@ko-quality        # 설치할 때 --scope를 줬다면 같은 값을 줍니다
claude plugin marketplace remove ko-quality
```

**스타일 선택도 지웁니다.** 스타일을 고른 프로젝트마다 `.claude/settings.local.json`(또는 `.claude/settings.json`)에서 `"outputStyle": "ko-quality:…"` 줄을 지우거나, 플러그인을 지우기 전에 `/output-style default`로 되돌립니다. 남겨 두면 다음 세션이 없는 스타일을 찾습니다.

플러그인을 끄기만 하려면 `claude plugin disable ko-quality@ko-quality`입니다. 이때도 스타일 선택은 남습니다.

제거 뒤에 남는 것(2.1.270에서 확인): 사용자 설정(`~/.claude/settings.json`)의 빈 `"extraKnownMarketplaces": {}` 항목, 그리고 `~/.claude/plugins/cache/ko-quality/`의 플러그인 사본입니다. 사본에는 `.orphaned_at` 표시가 붙어 Claude Code가 나중에 정리합니다. 둘 다 동작에는 영향이 없고 바로 지워도 됩니다.

### 시대 01(0.1.0)에서 올라오는 경우

0.1.0은 프로파일마다 플러그인이 하나였고 스타일을 강제했습니다. `ko-quality-formal`을 설치했다면 지웁니다.

```sh
claude plugin uninstall ko-quality-formal@ko-quality
```

0.2.0의 `ko-quality`로 업데이트한 뒤에는 위의 스타일 선택을 한 번 해야 이전처럼 정책이 걸립니다.

## 알아둘 것

- 로그: 플러그인은 hook으로 로거(`logger/ko_quality_log.py`)를 돌립니다. 메인 답변과 서브에이전트 답변마다 레코드 한 줄을 `~/.ko-quality/logs/<연-월>.jsonl`에 남깁니다. `KO_QUALITY_HOME`으로 위치를 바꿀 수 있고 `~`도 풀어 씁니다. 프롬프트와 답변 원문이 들어가며, API 키·토큰·이메일·전화번호·주민등록번호·카드 번호 꼴과 경로 속 홈 디렉터리는 가립니다. 가림은 최선의 노력일 뿐이고 이름은 가리지 않습니다. 로거는 판정하거나 막지 않고, 실패해도 세션에 영향을 주지 않습니다. 로그를 남기지 않으려면 플러그인을 끄거나 그 디렉터리를 지웁니다.
- 출처: 플러그인 안의 upstream 문장은 고치지 않았습니다. 어느 줄이 upstream이고 어느 줄이 우리 것인지는 `skills/*/SKILL.provenance.yaml`과 `provenance/policy.yaml`에 있습니다.
- upstream 4종(fluent-korean, im-not-ai, korean-skills, yoonmoon)은 모두 MIT이며 커밋은 저장소의 `upstream/lock.yaml`에 고정돼 있습니다.
