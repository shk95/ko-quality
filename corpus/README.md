# corpus

검증 단계에서 쓸 임시 코퍼스를 만드는 생성기입니다(설계 09 §18). 헤드리스 `claude -p` 세션을 배포되는 로거에 통과시켜 실제 레코드를 만들고, 세션마다 어떤 조건(arm)으로 돌렸는지 주석(annotation)을 남깁니다. **레코드와 주석은 저장소 밖 코퍼스 홈에만 쌓입니다.**

## 무엇을 하나

| arm | 플러그인 | 스타일 | 무엇을 가르나 |
|---|---|---|---|
| A | 로거만 담은 플러그인(스탬프 없음) | 없음 | 바닥값 |
| B | 빌드된 플러그인 사본 | 선택 안 함 | 스킬과 에이전트의 효과 |
| C | 같은 사본 | 프로젝트 설정에서 선택하고, 첫 프롬프트 뒤에 `/output-style`로 다른 프로필로 바꿉니다 | 정책의 효과 |

- 세션마다 새 임시 프로젝트(`fixtures/project` 복사본)를 만들기 때문에 앞 세션의 스타일 선택이 이어지지 않습니다.
- 입력은 한 줄씩 보냅니다. 앞 턴의 `result` 이벤트가 오고, 백그라운드 에이전트가 모두 끝난 뒤에 다음 줄을 보냅니다.
- 턴마다 `init.output_style`이 arm과 맞는지 확인하고, 로그 레코드의 `task`가 프롬프트와 같은지 확인해서 주석에 적습니다.
- 배치마다 arm별 카나리 세션을 돌립니다. 표지 문장이 엉뚱한 arm에서 나오면 배치를 거부합니다.

## 실행

```sh
W=~/.ko-quality-work/<시대>
python3 -m corpus canary --batch pilot-01 --home $W/corpus/canary --work $W/build/pilot-01 --report tests/runs/<시대>/canary-pilot-01.json
python3 -m corpus run --batch pilot-01 --home $W/corpus/pilot-01 --work $W/build/pilot-01 --ceiling-usd 20
python3 -m corpus summary --progress $W/build/pilot-01/pilot-01.progress.jsonl --out tests/runs/<시대>/pilot-01-sessions.json
measure/.venv/bin/python -m measure run --home $W/corpus/pilot-01
measure/.venv/bin/python -m measure pilot --home $W/corpus/pilot-01 --batch pilot-01
```

코퍼스 홈과 작업 디렉터리는 로컬 루트(`~/.ko-quality-work`, 설계 98 스펙 §2.3) 아래에 둡니다. 커밋하는 파일은 `--report`와 `summary`가 만든 것뿐입니다. 두 파일에는 세션 ID가 없고, 세션 ID와 키의 대응은 로컬 진행 기록에만 남습니다.

`--ceiling-usd`에 이른 뒤에는 새 세션을 시작하지 않습니다. 진행 기록(`<batch>.progress.jsonl`)이 남아 있으면 끝난 세션은 건너뛰고 이어서 돌립니다.

## 프롬프트

`prompts/set-1.json`에 층(stratum)별 프롬프트와 이 집합이 다루지 못하는 범위(`gaps`)를 적어 두었습니다. 붙여 넣기 프롬프트는 지시문 한 단락, 빈 줄, 원문 순서로 씁니다. 맞는 한국어와 틀린 한국어 층은 글을 그대로 다시 적게 하는 프롬프트여서, 답에 들어간 구역과 결함을 우리가 미리 압니다.
