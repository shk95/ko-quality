# 03a. 결정 기록

> 사이 문서. 03 엔진 → 04 설계 스펙으로 넘어가면서 내린 결정과 그 근거. 되돌아볼 지점을 표시한다.

## 하네스 중립 결정

에이전트 정의를 Claude Code 형식이 아니라 하네스 중립 템플릿으로 만든다. 중립의 기준을 하나로 고정했다.

> **코어와 스테이지, 에이전트 정의 어디에도 특정 하네스의 어휘가 등장하지 않고, 하네스 어휘는 adapter에서만 렌더링된다.**

이 기준에서 파생된 규약:

- 프롬프트는 도구 호출 문법을 쓰지 않고 `ko.gate` 같은 **capability 이름**만 언급한다. adapter가 실제 도구명으로 매핑한다.
- 템플릿 변수는 `{profile}`, `{intensity}`, `{findings}` 세 개로 제한한다.
- adapter는 파일 형식 변환, capability 매핑, 정책 주입 지점 배치, 선택적 hook 배선만 한다. 프롬프트 내용 수정, threshold 변경, 단계 추가는 금지한다. 이 제약을 문서가 아니라 테스트로 건다 — 모든 adapter 출력의 `policy_hash`가 동일해야 한다.

## taxonomy 분리와 category_map

rewrite(im-not-ai 71+ 패턴)와 diagnose(yoonmoon 10대 분류)는 한 컨텍스트에 동시에 올라가지 않는다. 이유: 겹치는 패턴의 이중 계산, 심각도 체계 충돌, 목록 자체가 만드는 priming과 과교정.

대신 **데이터로 잇는다.** reviewer의 finding은 중립 스키마 `{span, category, severity, evidence}`로 나오고, `core/category_map.yaml`이 yoonmoon 범주를 im-not-ai 범주로 매핑한다. editor는 매핑된 finding만 입력으로 받는다. upstream 하나가 분류를 바꾸면 이 파일만 고친다.

## hanspell의 위치

hanspell은 스테이지가 아니라 **capability** `ko.spell`이다. 두 스테이지가 다르게 쓴다.

- `grammar`(prompt 단계): 후보 생성기. hanspell이 후보를 주면 모델은 "진짜 오류인지"만 판단한다. 오탐(고유명사, 식별자)을 걸러내는 건 모델이 잘하고, 오류를 빠짐없이 찾는 건 도구가 잘한다. 기각 목록을 result에 남겨 allowlist 승격 재료로 쓴다.
- `gate`(tool 단계): 잔여 측정기. 판단하지 않고 세기만 하며 warning이다. grammar를 건너뛴 preset에서도 이 수치가 남아 "grammar를 넣으면 몇 건 줄었나"를 비교할 수 있다.

wrapper가 처리할 것: 텍스트 해시 캐시(같은 실행 안에서 두 단계가 같은 응답을 봄), `unavailable` 플래그(장애 시 예외 대신 계속 진행), 백엔드 선택(`hanspell | hunspell`).

## 14개 세부 결정

| # | 항목 | 결정 | 근거 |
|---|---|---|---|
| 1 | 형태소 분석기 | kiwipiepy | 설치 부담이 적음. katfishnet 계열 feature 계산에 필요 |
| 2 | 맞춤법 gate 등급 | warning, profile에서 fail 승격 가능 | 아래 별도 설명 |
| 3 | rewrite / diagnose upstream | im-not-ai / yoonmoon, category_map으로만 연결 | 아래 별도 설명 |
| 4 | 첫 profile | agent-reply | 아래 별도 설명 |
| 5 | 코어 언어 | Python | kiwipiepy, katfishnet, hanspell 바인딩이 전부 Python |
| 6 | report 저장 | 파일 산출물은 sidecar `x.md.quality.json`, 파일 없으면 응답 안에만 | agent-reply에는 파일이 없음 |
| 7 | selfcheck 반복·최종 실패 | N=2, 최종 실패 시 출력하되 report에 fail 표시 | agent-reply를 차단하면 사용자가 답을 못 받음. **되돌아볼 지점** |
| 8 | change_rate 단위 | 형태소 단위, 보존 대상은 분모에서 제외 | 문자 diff는 조사 하나에 과민, 문장 단위는 둔감 |
| 9 | 인간 baseline | 사용자 글 우선 | agent-reply의 threshold는 "사용자가 읽기 편한 한국어" 기준. **되돌아볼 지점** |
| 10 | policy 주입 검증 | writer가 policy_hash를 report에 echo | 하네스 중립이면 엔진이 주입을 직접 확인할 수 없음. **되돌아볼 지점** |
| 11 | eval 판정 모델 | profile별 고정, `judge.yaml` 명시 | 생성 모델과 달라야 자기참조 완화 |
| 12 | vendoring | 저장소에 복사 + `vendor.lock` | 설치 시 fetch는 재현성이 깨짐. 전부 MIT |
| 13 | 첫 eval 케이스 | 실제 세션 로그 20~30건 | 사용자가 제공해야 하는 재료 |
| 14 | 길이 상한 | policy-off 대비 증가율, 초기 +40% | fluent-korean이 토큰을 늘림. stage 0 측정 후 조정 |

### 2번: 맞춤법을 warning으로 두는 이유

hard fail은 "이 위반이 있으면 산출물을 내보내면 안 된다"는 뜻인데 맞춤법은 네 가지 이유로 이 조건을 못 채운다.

- **재현성이 없다.** hanspell은 다음·네이버·부산대 웹 서비스를 호출한다. 서비스 규칙이 바뀌면 같은 텍스트에 다른 결과가 나오고, 장애나 rate limit이면 텍스트 품질과 무관하게 파이프라인이 멈춘다. CI·오프라인에서 안 돈다. 텍스트를 외부로 보낸다.
- **오탐이 구조적이다.** 고유명사, 기술 용어, 코드 식별자, 외래어, 신조어를 오류로 잡는다. agent-reply에는 파일 경로와 명령어가 섞여 더 심하다. ignore 목록 관리가 gate보다 비싸진다.
- **위반의 비용이 비대칭이다.** hard fail 예산은 의미를 보호하는 invariant(숫자·고유명사 보존, 변경률 상한)에 써야 한다. 맞춤법 오류는 고치기 싸고 의미를 바꾸는 일이 드물다. 같은 fail 등급에 두면 오케스트레이터가 fail을 구분 못 해 결국 무시하게 된다.
- **결정론적 대안이 약하다.** hunspell 사전은 재현되지만 단어 단위라 띄어쓰기·문법 오류를 못 잡는다.

### 3번: rewrite upstream을 im-not-ai로

가져오는 것: 진단→윤문→finalize 절차, 명시적 invariant(의미 보존·탐지 span만 수정·장르 보존·변경률 30/50), 71+ 패턴 taxonomy. 앞의 둘은 `stages/rewrite/prompt.md`로, taxonomy는 `resources/`로. Claude Code용 다중 에이전트 구성은 가져오지 않는다 — 그 역할 분리는 엔진의 reviewer/editor가 담당한다.

다른 것이 아닌 이유: k-skill v2는 im-not-ai 방법론의 재구성이라 파생을 고르는 셈. korean-skills humanizer는 3단계가 한 에이전트 안에서 순차 실행되는 구조라 단계 분리 엔진과 결이 다르며, grammar-checker만 `grammar` upstream으로 쓴다. yoonmoon은 detect가 분리돼 있어 diagnose에 맞지만 10대 분류는 rewrite에 쓰기엔 거칠다.

추가 invariant: hjongc/humanizer-kr의 "낱말 하나만 보고 고치지 않고 신호가 쌓일 때 고친다"는 원칙을 rewrite prompt에 넣는다. 규칙 수가 많은 taxonomy의 과교정을 억제하는 가장 싼 장치다.

### 4번: 첫 profile을 agent-reply로

- **문제의 원점이다.** fluent-korean이 겨냥한 결함(조사·어미 탈락, 전보체, 비유 어휘)은 코딩 에이전트의 보고에서 나타나고, humanizer들이 다루는 블로그·보고서 레지스터와 다르다.
- **생성 방향을 먼저 검증하게 된다.** agent-reply에서는 rewrite를 거의 쓰지 않는다. 주 경로는 policy → selfcheck → gate이고, 이것이 검증이 가장 어려운 경로다.
- **다중 에이전트 누적 문제가 이 레지스터에 있다.** `subagent-propagation` 블록의 효과를 재려면 이 프로파일이어야 한다.
- **케이스 수집이 가장 쉽다.** 세션마다 보고가 쌓인다.
- **gate 항목이 formal-report와 거의 겹치지 않는다.** 두 번째 프로파일로 formal-report를 두면 "프로파일이 gate 구성을 실제로 바꾼다"도 확인된다.

## 되돌아볼 지점

14개 중 대부분은 실제로 선택지가 하나뿐이었다. 셋만 진짜 trade-off가 있어서, 권장대로 가되 수정을 반영하고 표시해둔다.

| # | trade-off | 반영한 수정 |
|---|---|---|
| 7 | 가용성 > 안전. agent-reply에는 맞지만 formal-report로 새어 나가면 fail인 문서가 사용자에게 도달 | profile마다 `on_final_fail`을 **명시하도록 스키마에서 강제**. 기본값 상속 금지 |
| 9 | 사용자 글로 baseline을 잡으면 일반화가 안 됨 | baseline을 profile의 **교체 가능한 자산**으로. "개인 baseline"과 "공개 말뭉치 baseline"이 같은 형식 |
| 10 | echo는 검증이 아니라 주장 기록. 진짜 검증은 gate 수치 A/B뿐 | 필드 이름을 `policy_hash`가 아니라 **`policy_hash_claimed`** 로 |

## 사용자가 제공해야 하는 재료

- 9번: 본인이 쓴 한국어 글 샘플(레지스터: 에이전트에게 하는 지시·보고에 가까운 것)
- 13번: 실제 세션에서 에이전트가 한 한국어 보고 20~30건, 가능하면 policy 켜고 끈 상태 각각

이 둘은 gate threshold와 eval에만 필요하고 골격 구현에는 필요 없다.
