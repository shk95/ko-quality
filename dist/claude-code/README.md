# ko-quality — Claude Code 플러그인

빌드 산출물입니다. 직접 고치지 말고 저장소 루트에서 `python3 -m build.claude_code`로 다시 만듭니다.

## 무엇이 들어 있나

프로파일마다 플러그인이 하나씩 있습니다. **둘 중 하나만 켭니다.** 두 플러그인은 각자 자기 출력 스타일을 강제(`force-for-plugin`)하므로, 둘 다 켜면 먼저 로드된 쪽만 적용되고 어느 쪽인지 정해져 있지 않습니다.

| 플러그인 | 프로파일 | 메인 대화에 적용되는 정책 | 기본 프리셋 |
|---|---|---|---|
| `ko-quality` | agent-reply | fluent-korean 코딩판 | standard |
| `ko-quality-formal` | formal-report | fluent-korean 비코딩판 + 존대 블록 | full |

두 플러그인 모두 스킬 넷(`ko-rewrite`, `ko-diagnose`, `ko-grammar`, `ko-route`)과 에이전트 셋(`korean-reviewer`, `korean-writer`, `korean-editor`)을 담습니다. 스킬은 두 플러그인에서 같고, 에이전트는 각 프로파일의 정책을 담습니다.

## 설치

이 디렉터리(`dist/claude-code`)를 로컬 마켓플레이스로 추가한 뒤 플러그인 하나를 설치합니다.

```sh
claude plugin marketplace add <저장소 경로>/dist/claude-code
claude plugin install ko-quality@ko-quality          # 또는 ko-quality-formal@ko-quality
```

`--scope local`을 붙이면 현재 프로젝트에만 설치됩니다(`.claude/settings.local.json`). 설치 없이 한 번만 써 보려면 `claude --plugin-dir <저장소 경로>/dist/claude-code/agent-reply`로 실행합니다.

## 제거

```sh
claude plugin uninstall ko-quality@ko-quality        # 설치할 때 --scope를 줬다면 같은 값을 줍니다
claude plugin marketplace remove ko-quality
```

플러그인을 끄기만 하려면 `claude plugin disable ko-quality@ko-quality`입니다.

제거 뒤에 남는 것(2.1.270에서 확인): 사용자 설정(`~/.claude/settings.json`)의 빈 `"extraKnownMarketplaces": {}` 항목, 그리고 `~/.claude/plugins/cache/ko-quality/`의 플러그인 사본입니다. 사본에는 `.orphaned_at` 표시가 붙어 Claude Code가 나중에 정리합니다. 둘 다 동작에는 영향이 없고 바로 지워도 됩니다.

## 알아둘 것

- 로그: 플러그인은 hook으로 최소 로거(`logger/ko_quality_log.py`)를 돌립니다. 메인 답변과 서브에이전트 답변마다 레코드 한 줄을 `~/.ko-quality/logs/<프로파일>/<연-월>.jsonl`에 남깁니다(`KO_QUALITY_HOME`으로 위치를 바꿀 수 있습니다). 프롬프트와 답변 원문이 들어가며, API 키·토큰·이메일 꼴은 `[masked]`로 가립니다. 로거는 판정하거나 막지 않고, 실패해도 세션에 영향을 주지 않습니다(실패 기록은 `logger-errors.log`). 로그를 남기지 않으려면 플러그인을 끄거나 그 디렉터리를 지웁니다.

- 출처: 플러그인 안의 upstream 문장은 고치지 않았습니다. 어느 줄이 upstream이고 어느 줄이 우리 것인지는 `skills/*/SKILL.provenance.yaml`과 `provenance/policy.yaml`에 있습니다.
- upstream 4종(fluent-korean, im-not-ai, korean-skills, yoonmoon)은 모두 MIT이며 커밋은 저장소의 `upstream/lock.yaml`에 고정돼 있습니다.
