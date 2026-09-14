# 06b. 실측: 프로토타입을 지으며 알게 된 것

> 실측 문서. 06 §14 프로토타입 계획을 실행하면서 스펙과 달랐던 것, 스펙이 몰랐던 것, 임시 형식에서 불편했던 것을 P 단계마다 절로 덧붙인다.
>
> **이 문서는 06을 고치지 않는다.** 06에 반영할지는 이 기록을 읽고 사용자와 정한다 (06 §14.1).

## P0 — 사전 확인

2026-09-14. 끝나는 조건을 충족했고 멈추는 조건(MIT가 아닌 upstream)에는 해당하지 않았다. 다만 06의 서술과 어긋나는 것이 upstream 쪽에서 12건 나왔다. 반영 검토 후보는 이 절 끝에 모았다.

### 진행 방식

- **커밋:** 단계마다 커밋한다 (저장소 초기화 → lock → 파일 지도 → 하네스 재확인 → 결정 현황).
- **파일 지도 크로스체크:** 주 작성자(Opus 5)와 서브에이전트(Sonnet, upstream당 하나)가 서로의 결과를 보지 않고 따로 지도를 만든 뒤 대조했다. 어긋난 곳은 `.cache/` 원본에서 직접 확인해 확정했다.
- **korean-skills는 얕게 봤다.** P4에서 "스키마만 보고 넣는" 시험 대상이므로 양쪽 모두 파일 구성, 제목 트리, frontmatter 키 이름까지만 확인했다. 본문 규칙은 읽지 않았다.

### lock

`upstream/lock.yaml`. 모두 `main` HEAD 기준이다.

| name | commit | 커밋 날짜 | license | 근거 |
|---|---|---|---|---|
| fluent-korean | `ce8683f` | 2026-08-23 | MIT | 루트 `LICENSE`, `plugin.json` |
| im-not-ai | `9747f03` | 2026-09-06 | MIT | 루트 `LICENSE`. README `## 라이선스 & 윤리`가 "코드·스킬·에이전트 정의·분류 체계 문서를 포함한 본 리포 전체에 적용"이라고 명시 |
| korean-skills | `ae12ba2` | 2026-05-05 | MIT | 루트 `LICENSE`, grammar-checker `SKILL.md` frontmatter `license: MIT` |
| yoonmoon | `c888531` | 2026-09-11 | MIT | 루트 `LICENSE`, `plugin.json` |

**라이선스 관찰.**

- im-not-ai HEAD는 `feat/a16-context-licensed` 브랜치의 머지다. 이름의 `a16`은 규칙 id `A-16`이고 라이선스와 관계가 없다.
- im-not-ai의 검증 코퍼스는 저작권 때문에 저장소에 커밋되지 않았다 (`empirical-validation.md`). 공급 대상이 아니다.
- yoonmoon의 `docs/papers/LREAD-2601.19913v3.pdf`는 제3자 논문 사본(Git LFS)이다. 루트 MIT가 이 파일까지 포괄하는지는 알 수 없다. **공급 범위에서 제외한다.**

### 파일 지도

앵커는 제목 텍스트를 그대로 적었다. 제목이 아닌 것은 무엇으로 찾는지 적었다.

#### fluent-korean → `policy`

| 항목 | 파일 | 앵커 | 비고 |
|---|---|---|---|
| 본문 — coding | `plugins/fluent-korean/output-styles/fluent-korean.md` | 제목 없는 도입 문단, `## 상황과 목표`, `## 동작 범위`, `## 문장 단위`, `## 구 단위`, `## 추가 사항` | frontmatter `name`, `description`, `keep-coding-instructions: true` |
| 본문 — not-coding | `plugins/fluent-korean/output-styles/fluent-korean-not-coding.md` | 제목 없는 도입 문단, `## 상황과 목표`, `## 동작 범위`, `## 문장 단위`, `## 구 단위` | frontmatter `name`, `description`만. `keep-coding-instructions` 키가 없다(기본값 false) |
| 선택 블록 7종 | `README.md` | `## 세부 동작 - 저는 Claude가 이랬으면 좋겠어요.` 아래 | 제목이 아니라 `- **질문** →` 불릿 뒤의 코드블록. 아래 표 |
| 설치·환경 안내 | `README.md` | `## 설치 안내 및 구성 (Claude Code CLI 환경)`, `## Claude Code CLI 외 다른 환경에서 사용하는 방법` | 공급 대상 아님 |
| 스스로 밝힌 한계 | `README.md` | `## 유의점` | 참고. 서브에이전트 조항이 코딩판에만 있다고 스스로 적음 |

선택 블록은 굵은 글씨 질문으로만 식별된다.

| # | 식별 텍스트 | 06의 이름 |
|---|---|---|
| 1 | `**내가 초보 개발자라면?**` | — |
| 2 | `**예의 바르게 만들어주고 싶다면?**` | `honorific`. 설명에 "'사용자님' 부분을 '원하는 호칭'으로 바꿔주세요"라는 채울 자리가 있다 |
| 3 | `**오푸스나 페이블이 비유적인 어휘, 사전 속에나 있는 단어를 너무 많이 쓴다면?**` | — |
| 4 | `**나에게 하는 보고 말고, 다른 한국어 출력에도 적용되어야 한다면?**` | — |
| 5 | `**문체에 민감한 작업들을 수행하고 있다면?(소설, 대본, 출제, 연구 등)**` | — |
| 6 | `**애들이 자꾸 영어를 뱉는 게 짜증난다면?**` | `think-in-korean` |
| 7 | `**교정이 잘 안 된다면?**` | — |

두 변형 본문의 차이 (frontmatter 제외):

| 위치 | coding | not-coding |
|---|---|---|
| `## 문장 단위` 1 | "작업 중인", "특히 관형격" | "작업중인", "특히␣␣관형격"(공백 둘) |
| `## 구 단위` 4 | "문맥과 형식에 따라" | "문맥에 따라" |
| `## 추가 사항` | 있음 (서브에이전트 조항) | 없음 |

#### im-not-ai → `procedure.rewrite`, `taxonomy.rewrite`

**절차의 원천이 여럿이다.**

| 원천 | 파일 | 주요 앵커 | 성격 |
|---|---|---|---|
| 오케스트레이터 | `skills/humanize-korean/SKILL.md` (331줄, v2.3.2) | `## Phase 0: 컨텍스트 확인 및 경로 결정`, `### 전 경로 공통 의미 앵커`, `## Light 경로 (1콜) — 잘 쓴 글` 외 경로 3절, `## Phase 2.5: 구조 게이트 (철칙 #4 — 결정적 검증, 전 경로 공통)`, `## 에이전트 호출 규칙` | Claude Code 전용. 에이전트 호출과 `scripts/verify_gates.py` 실행에 묶여 있음 |
| 단일 호출판 | `codex/skills/humanize-korean/SKILL.md` (45줄) | `## 철칙 (위반 시 즉시 롤백)`, `## 절차 (단일 호출 안에서)`, `## 등급`, `## 옵션 (인자 끝에 자연어로)`, `## 참고` | Codex·Copilot CLI용. `references/`는 `skills/humanize-korean/references`를 가리키는 심볼릭 링크 |
| 단일 호출 에이전트 | `agents/humanize-monolith.md` | `## 철칙 (Prime Directives — 위반 시 즉시 롤백)`, `## 작업 순서 (한 호출 안에서)`, `## 출력 포맷 — \`final.md\` 끝의 \`<!-- HUMANIZE-SUMMARY -->\` 블록` | Claude Code 에이전트 정의 |
| 처방집 | `skills/humanize-korean/references/rewriting-playbook.md` | `## 0. 대원칙 (The Prime Directives)`, `## 1. 카테고리별 치환 레시피`, `## 2. 변경률 모니터링`, `## 3. 어휘 대체 위험 (Do-NOT list)`, `## 4. 장르별 미세 조정` | 하네스 중립 |
| 슬림 룰북 | `skills/humanize-korean/references/quick-rules.md` | — | **생성물.** `scripts/build_quick_rules.py`가 `quick-rules.header.md` + taxonomy의 `quick: true` 패턴 + `quick-rules.footer.md`로 만든다. 직접 고치지 말라고 명시 |

**06 §7의 invariant가 있는 곳.**

| invariant | 찾은 곳 | 비고 |
|---|---|---|
| 의미 보존 | README `## 4대 철칙` 1, 단일 호출판 `## 철칙` 1, monolith `## 철칙` 1, playbook `## 0. 대원칙` 1, `CLAUDE.md` `## 철칙` | |
| 탐지된 span만 수정 | README `## 4대 철칙` 2 "탐지된 span에만 수술적 수정", playbook `## 0. 대원칙` 3 "국소성"·5 "근거 기반(Span-Grounded)", 단일 호출판 `## 철칙` 2 | 06 §7 문구에 가장 가까운 것은 README. 단일 호출판은 "`references/quick-rules.md`에 매핑되지 않는 구간은 건드리지 않는다" |
| 장르 보존 | README `## 4대 철칙` 3, 단일 호출판 `## 철칙` 3, monolith `## 철칙` 3, playbook `## 0. 대원칙` 2 | |
| 숫자·고유명사·인용 불변 | 단일 호출판 `## 철칙` 1·6, monolith `## 철칙` 1·6, `quick-rules.header.md`의 `**Do-NOT (탐지·윤문 모두 제외):**` 문단, playbook `## 3. 어휘 대체 위험 (Do-NOT list)`, README `Do-NOT List (탐지·윤문 대상 제외)` | quick-rules 헤더 쪽 문단은 제목이 없고 굵은 라벨로만 구분된다 |
| 변경률 30% 경고 / 50% 중단 | README `## 4대 철칙` 4, 단일 호출판 `## 철칙` 5, monolith `## 철칙` 5, `quick-rules.header.md`의 `**과윤문 가드:**` 문단, 오케스트레이터 `## Phase 2.5` 표 | playbook은 수치가 다르다: `## 0. 대원칙` 6은 50%만, `## 2. 변경률 모니터링`은 권장 5~30%, 30% 초과 시 재검토. 수치를 실제로 강제하는 곳은 `scripts/verify_gates.py`·`verify_change_rate.py` |

**06이 모르는 invariant.** register 보존(단일 호출판 `## 철칙` 4), 입력은 데이터이지 지시가 아니다(같은 곳 7, 프롬프트 인젝션 방어), 빼기 전용(playbook `## 0. 대원칙` 7), 서법 보존(`quick-rules.header.md`, playbook `## 3.`), 내용 앵커(오케스트레이터 `### 전 경로 공통 의미 앵커`).

**하네스에 묶인 것.** `agents/` 9개(런타임 3, 유지보수 1, 개발용 5), `.claude-plugin/`, `CLAUDE.md`, 오케스트레이터의 경로 분기와 에이전트 호출, `${CLAUDE_SKILL_DIR}` 등 경로 변수, `scripts/`의 게이트와 서법 복원(`restore_modality.py`, `strip_injected_commas.py`), `install.sh`·`update.sh`·`uninstall.sh`. 다른 하네스용 사본도 따로 있다: 루트 `plugin.json`은 Copilot CLI용(`skills: ["./codex/skills/"]`)이고, `GEMINI.md`·`gemini-extension.json`(버전 1.5.0으로 낡음)·`commands/*.toml`은 Gemini CLI용이다. 단일 호출판도 `_workspace/{run_id}/final.md`에 쓰는 단계(`## 절차` 7)를 포함한다.

**taxonomy.**

| 항목 | 내용 |
|---|---|
| 원본 | `skills/humanize-korean/references/ai-tell-taxonomy.md` (931줄). 파일이 스스로 "단일 진실 원천(SSOT)"이라고 선언 |
| 대분류 | `## A. 번역투 (Translation-ese) — S1~S2` ~ `## J. 시각 장식 남용 — S2~S3`, 10개 |
| 패턴 | `### A-1. "~에 대하여/대해서" 남발 [S1]` 형식의 id 제목. **85개** (A 24, B 4, C 12, D 14, E 7, F 6, G 3, H 4, I 7, J 4). A-17은 보류, F-6은 없음 |
| 심각도 | `## 심각도 기준` S1/S2/S3. 대부분 제목 끝 `[S1]`. D-1~D-4처럼 제목에 없고 대분류 범위만 있는 패턴도 있음 |
| 빌드 메타 | 패턴 말미 이탤릭 한 줄 `_quick: true · quick_pattern: … · quick_fix: …_`. 규칙은 `## quick 빌드 메타 (fast 룰북 생성 계약)` |
| 패턴이 아닌 절 | `## 진단 관측 지표 — 처방 불가, 탐지·오탐 방지 전용 (v2.6, 팀 채굴)`(DS-1~DS-6, id 체계가 다름), `## 오탐 방지 원칙 (v2.6 — Pebblous 티어다운·평가자 연구 반영)`, `## 탐지 출력 스키마 (Detector → Rewriter 공유 계약)`, `## post-editese 3축 — metric-only 트랙 (v2.0 도입)`, `## 버전 관리` |
| 쓰이지 않는 계약 | `## 탐지 출력 스키마`의 JSON(`severity_weighted_score` 등)은 이 파일과 `docs/en/taxonomy.md`에만 나오고 스킬·에이전트 파일은 쓰지 않는다. 출력 계약으로 가져오면 실제 동작과 어긋난다 |
| 파생물 | 생성물 `quick-rules.md`(`build_quick_rules.py`, `quick: true`만)와 `diagnosis-rules.md`(`build_diagnosis_rules.py`, 패턴이 굵은 id 불릿). 수기 사본 `docs/en/taxonomy.md`·`docs/en/quick-rules.en.md`(영문, "한국어가 SSOT"라고 명시), `GEMINI.md`(발췌). 대분류 제목 텍스트가 이 파일들에 거의 그대로 반복된다 |

#### korean-skills → `procedure.grammar` (구조만)

| 항목 | 내용 |
|---|---|
| 파일 | `skills/grammar-checker/SKILL.md`(267줄), `references/rules.md`, `references/common-errors.md`, `examples/before.md`, `examples/after.md` |
| 절차로 보이는 제목 | `## 작업 흐름` 아래 `### 1단계: 텍스트 입력 받기` ~ `### 4단계: 결과 제시` |
| 그 밖의 제목 | `## 소개`, `## 중요 지침`(### 1~5), `## 특수 상황 처리`, `## 예시`, `## 최종 확인사항` |
| frontmatter 키 | `name`, `description`, `license`, `metadata.author`, `metadata.version`, `allowed-tools` |
| 참조 방식 | 본문 마크다운 링크 `[references/rules.md](references/rules.md)` |
| 범위 밖 | 같은 저장소의 `humanizer`, `style-guide` 스킬 |

#### yoonmoon → `procedure.diagnose`, `taxonomy.diagnose`

**절차: `skills/detect/SKILL.md`** (148줄). 마크다운 제목은 H1 하나뿐이고, 내용은 XML형 태그로 나뉜다.

| 항목 | 태그 |
|---|---|
| 역할과 "고치지 않는다" | frontmatter `description`, `<role>` |
| 참조 | `<resources>` — `references/lread-rubric.md`, `../humanize/references/ai-tell-taxonomy.md`, `../humanize/references/katfishnet-research.md`, `references/xdac-research.md`(단문일 때만) |
| 단계 | `<workflow>` 안의 `<phase n="0" name="입력·장르">`, `<phase n="1" name="신호 스캔">`, `<phase n="1S" name="단문/SNS 신호 (조건부)">`, `<phase n="2" name="점수·판정">` |
| 판정 원칙 | `<fluencyTrap>`, `<scoringRubric>` |
| 출력 계약 | `<outputFormat>` — 한 줄 판정(AI 가능성 / 신뢰도 / 번역문 가능성 / 장르), 근거 요약, 신호 표, 의심 구간 |
| 제약 | `<cautions>`, `<outOfScope>` |

**taxonomy: `skills/humanize/references/ai-tell-taxonomy.md`** (283줄). detect 폴더가 아니라 humanize 폴더에 있고 두 스킬이 공유한다.

| 항목 | 내용 |
|---|---|
| 대분류 | `## 1. 번역투` ~ `## 11. 과소 서술·의미 불명확`, **11개** |
| 패턴 | 표의 행(패턴 / 예시 / 심각도). **id가 없다.** 52행 |
| 심각도 | `## 심각도 등급` 강/중/약 |
| 그 밖 | `## 보존 원칙 (Do-NOT)`, `### 삭제 과교정 금지` |
| 외부 링크 | 다른 스킬의 `../../translate-polish/references/translationese-research.md`를 세 곳에서 링크 |

**하네스에 묶인 것.** `skills/polish-all/SKILL.md`가 detect를 `yoonmoon:detect`로 호출하고 `<outputFormat>` 1번의 세 값에 의존한다. 그 밖에 `.claude/settings.json`, `.claude/agent-memory/`, bun·eslint 설정이 있다. 런타임 코드는 없다.

### 크로스체크 결과

| upstream | 일치 | 어긋난 곳과 확정 |
|---|---|---|
| fluent-korean | 변형의 파일 분리, 선택 블록 7종과 위치, frontmatter, 두 변형의 문구 차이 3곳, `## 추가 사항`이 서브에이전트 조항이라는 판단 | 없음 |
| im-not-ai | 절차 원천이 오케스트레이터와 단일 호출판으로 나뉨, invariant 위치, playbook의 다른 변경률 수치, taxonomy SSOT, id 제목 85개와 대분류별 수, J-1 제목 수준 이상, 낡은 목차 | 어긋난 곳 없음. 서브에이전트만 찾은 것(원본에서 모두 확인): README `## 4대 철칙`이 06 §7 문구에 가장 가까운 invariant 원천이라는 점, `diagnosis-rules.md`도 생성물이라는 점, "70/71패턴" 문구가 README·CLAUDE.md·생성물 헤더·영문판까지 퍼져 있다는 점, `## 탐지 출력 스키마`의 JSON을 런타임 파일이 쓰지 않는다는 점, 루트 `plugin.json`이 Copilot CLI용이라는 점 |
| korean-skills | 파일 구성, 제목 트리, frontmatter 키 | 서브에이전트는 `## 문법 검사 결과`를 "3번 중복된 제목", `#### 1. 맞춤법/철자 오류 (N개)`를 "템플릿성 제목"으로 봤다. **원본 확인 결과 셋 모두 ` ```markdown ` 코드블록 안의 출력 예시이고 제목이 아니다.** 주 작성자의 1차 추출도 코드블록을 구분하지 않아 같은 착오를 품고 있었다 |
| yoonmoon | XML 태그 구조, taxonomy 공유, 11대 분류, 52행(원본에서 다시 셈) | 없음. 서브에이전트만 찾은 것: LREAD PDF의 라이선스 불명, `.claude/agent-memory/`의 "10 categories" 기록 |

크로스체크 자체에서 나온 것: **같은 원본을 둘이 읽어도 코드블록 안 제목을 제목으로 셌다.** 추출기의 앵커 탐색은 코드블록을 인식해야 한다.

### 06과 달랐던 것 — upstream

1. **`subagent-propagation`은 README의 선택 블록이 아니다.** coding 변형 본문의 `## 추가 사항` 절이고, not-coding 변형에는 없다. 06 §5.3과 06a ②는 이것을 "fluent-korean README의 선택 블록"이라고 적었다. 켜고 끄는 블록이 아니라 변형에 딸린 본문이다. not-coding 정책을 쓰는 `formal-report`가 이 조항을 원하면 coding 본문에서 골라와야 한다(`selected`).
2. **선택 블록은 3종이 아니라 7종이고, 06이 쓴 이름은 README에 없다.** `honorific`·`think-in-korean`은 우리가 붙인 이름이다. honorific 블록은 호칭을 사용자가 채우도록 되어 있어, 호칭을 정하면 `adapted`가 된다.
3. **두 변형은 "한쪽 + 한 절"이 아니다.** 본문 문구가 세 곳에서 다르다. 공통부를 한 번만 정규화하면 한쪽이 `adapted`가 되므로, 변형별로 따로 두어야 문장 불변 원칙에 맞는다. (P3 재료)
4. **yoonmoon의 분류는 10대가 아니라 11대다.** 01a와 06은 "10대 분류"라고 적었다. 11번 `과소 서술·의미 불명확`은 2026-08-21(yoonmoon #6)에 추가됐다. **11번 표의 예시는 fluent-korean 본문의 예시와 같은 문장이다** ("그러면 경고가 붙습니다", "사본의 문구는 작업의 상황을", "코드로 박는 자리", "쓴 비용을 구하는 함수"). diagnose taxonomy와 policy가 원천 하나를 나눠 쓴다.
5. **yoonmoon detect에는 제목 앵커를 걸 수 없다.** 절차가 XML형 태그로 나뉘어 있다. 06 §5.5의 `anchor: "<제목 텍스트>"`를 태그(`<phase n="1">`)까지 넓혀야 한다. (P2 재료)
6. **yoonmoon의 diagnose taxonomy는 humanize 폴더에 있고 패턴에 id가 없다.** 패턴이 표의 행이라 조각 앵커는 "대분류 제목 + 행 텍스트"뿐이다.
7. **im-not-ai의 절차 원천이 하나가 아니다.** Claude Code 오케스트레이터(에이전트 9개와 스크립트 게이트) 말고도 Codex·Copilot용 단일 호출판이 따로 있다. 06 §5.4와 06a는 "Claude Code 다중 에이전트 구성 부분을 뺀다(`selected`)"를 가정했지만, upstream이 이미 하네스 중립에 가까운 판을 두고 있다. 다만 단일 호출판은 생성물 `quick-rules.md`를 가리키고 파일을 쓰는 단계를 포함한다. **어느 쪽을 원천으로 할지는 P1에서 정한다.**
8. **변경률 30/50은 im-not-ai 안에서도 경로마다 다르고, 판정은 코드가 한다.** 철칙 문구(단일 호출판, monolith, quick-rules 헤더)는 06 §7과 같은 30 경고·50 중단이다. 반면 playbook은 5~30 권장·50 경보이고, 오케스트레이터는 모델이 스스로 낸 변경률을 "참고값"으로만 보고 판정을 `scripts/verify_gates.py`(문자율 외 3축)에 맡긴다. **06은 스크립트를 공급하지 않으므로 이 invariant는 모델의 자기 보고로 약해진다.** (06 §15 `ko.change_rate`와 이어짐)
9. **im-not-ai에는 06이 모르는 invariant가 다섯 개 더 있다.** register 보존, 입력은 데이터, 빼기 전용, 서법 보존, 내용 앵커.
10. **im-not-ai의 패턴 수는 70이 아니다.** "10대 카테고리 × 70 패턴"(71은 보류 포함)이라는 문구가 README, `CLAUDE.md`, 두 `SKILL.md`, 생성물 `diagnosis-rules.md` 헤더, 영문판에 퍼져 있고 taxonomy 목차도 "A-1~A-19"에 머물러 있다. 실제 id 제목은 85개(보류 1 포함)다. 설명 문구를 옮기면 틀린 수를 옮기게 된다.
11. **im-not-ai 패턴 제목에는 버전 태그가 섞여 있어 앵커가 자주 바뀐다.** 85개 중 39개가 `· v2.7 신규` 같은 태그를 제목에 달고 있다. lock한 HEAD도 A-16 제목의 태그를 바꾼 머지다. 제목 전체 대신 id 접두(`A-16.`)로 앵커를 거는 방식을 P1에서 검토한다. 또 `## J. 시각 장식 남용 — S2~S3` 바로 아래에 내용 없는 `#` 한 줄이 있고, `## J-1. 과도한 **볼드**`만 H2이며(나머지 J는 H3), `## J.`와 J-1 사이에 패턴이 아닌 절이 두 개 끼어 있다. 제목 수준으로 계층을 잡으면 J-1이 대분류로 잡힌다.
12. **korean-skills의 제목처럼 보이는 줄 일부는 코드블록 안에 있다.** (크로스체크 결과 참조)

### 끝나는 조건

- [x] `upstream/lock.yaml`에 4종이 커밋·라이선스와 함께 있다
- [x] 파일 지도가 이 문서에 있다
- 멈추는 조건: 해당 없음 (4종 모두 MIT)

### 06 반영 검토 후보

사용자와 정할 것. 이 문서는 06을 고치지 않았다.

| # | 06 위치 | 내용 | 근거 |
|---|---|---|---|
| a | §5.3, §6 `blocks` | `subagent-propagation`을 선택 블록에서 빼고 coding 변형 본문으로 본다. 블록 목록을 README 실물 7종으로 바꾼다 | 위 1, 2 |
| b | §5.5 | 앵커를 제목 텍스트에서 "제목, XML형 태그, id 접두, 표 행"으로 넓힌다. 코드블록 안 제목은 앵커로 치지 않는다 | 위 5, 6, 11, 12 |
| c | §7 `ko-rewrite` invariant | 변경률 invariant가 모델 자기 보고라는 한계를 적는다. upstream의 추가 invariant 다섯 개를 받을지 정한다 | 위 8, 9 |
| e | §5.3, 01a 인용 | yoonmoon "10대" → 11대 | 위 4 |

### P1에 넘기는 것

- im-not-ai `procedure.rewrite`의 원천: 오케스트레이터에서 골라낼지, 단일 호출판을 쓸지. 단일 호출판을 쓰면 `quick-rules.md`(생성물)와 원본 taxonomy 중 무엇을 참조로 둘지도 함께 정한다
- taxonomy 조각 앵커: 버전 태그가 섞인 제목 전체로 걸지, id 접두로 걸지
- 30/50 invariant 문구의 출처: 철칙(30/50)과 playbook(5~30/50) 중 어느 쪽인가
