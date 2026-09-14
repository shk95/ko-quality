# 01a. 조사에서 알게 된 것

> 사이 문서. 01 아이디어 → 02 스택으로 넘어가면서 조사한 내용과 그로부터 내린 판단.

## 생태계의 구조

가설대로 두 갈래로 갈렸다.

| 갈래 | 개입 시점 | 대표 |
|---|---|---|
| 생성 시점 개입 (generation-time) | 시스템 프롬프트 / output-style | fluent-korean, stop-slop-ko 생성 모드 |
| 생성 후 개입 (post-generation) | skill로 산출물을 다시 씀 | im-not-ai, korean-skills, k-skill, yoonmoon 등 |

생성 시점 개입은 fluent-korean 외에 stop-slop-ko가 유일하게 "생성 모드"를 같이 갖고 있었다. 나머지는 전부 후처리다. fluent-korean README도 번역체 교정·AI 표현 최소화·맞춤법은 im-not-ai, korean-skills, k-skill을 참조하라고 안내하며 스스로 역할 범위를 긋고 있다.

## 프로젝트 목록

주목 순서. 상단이 스택에 직접 들어가는 것.

| 프로젝트 | 성격 | 스택에서의 역할 |
|---|---|---|
| snflkd/fluent-korean | output-style, 생성 시점 규율 | L0 policy 핵심 |
| limleesol/stop-slop-ko | slop 제거, 생성+교정 모드, evals 보유 | L0 보조 규칙, L4 eval 포맷 |
| epoko77-ai/im-not-ai | 71+ 패턴 taxonomy, route 사전 채점, 변경률 gate | L1 rewrite upstream |
| DaleSeo/korean-skills | humanizer / grammar-checker / style-guide, KatFishNet 근거 | L1 grammar upstream |
| amondnet/yoonmoon | humanize + detect 분리, 10대 분류, 연구 매핑 | L2 diagnose upstream |
| JangHyun-bin/korean-report-skills | 115 치환 규칙 lint.py, 어미 자동 수정 | L3 gate 규칙 |
| Shinwoo-Park/katfishnet | ACL 2025 탐지기 코드 (Python) | L3 정량 feature |
| VoidLight00/son-writer-skill | fail-closed 결정론 gates | L3 설계 원형 |
| TaewoooPark/personal-humanizer-maker | 개인 스타일 → skill 컴파일 | 선택 계층 (voice) |
| CreatoonForge/korean-writing-reviewer | evaluate / improve 모드 분리 | L2 참고 |
| hjongc/humanizer-kr | 20패턴, 신호가 쌓일 때만 수정 | L1 invariant 참고 |
| NomaDamas/k-skill korean-humanizer | im-not-ai 방법론 기반 재구성 | 참고 |
| chann/skills human-friendly-writing | skills-lock, evals, Claude/Codex 이중 인터페이스 | 패키징 참고 |
| blader/humanizer, jooray/humanizer | 영어권 원류 | 기준점 |
| Kir93/scrooge-mode | 한국어 압축 register + 토큰 benchmark | 측정 방법 참고 |
| J-nowcow/awesome-korean-agent-skills | 자동 운영 디렉터리 | 지속 감시 |
| 9beach/hanspell, spellcheck-ko | 맞춤법 (외부 API / hunspell 오프라인) | L3 warning |

## 결정적으로 알게 된 것

### fluent-korean 관리자의 실제 운용 방식

README에 관리자 본인의 세팅이 나온다. output-style을 기본으로 쓰고, 주요 산출물에서 문체가 안 지켜지면 skill처럼 재적용하며, 하네스에서는 결과물 도출 전에 적대적 검증을 수행하도록 했다. 이것이 사실상 "공식 권장 스택"이고, 이후 L0 → L1 재적용 → L3 검증 구조의 뼈대가 됐다.

### fluent-korean이 인정하는 한계

지시가 다양할수록, 작업이 길수록, priming을 유발하는 텍스트가 많을수록 효과가 약해진다고 명시하고, 그럴 때 지침 수정보다 하네스 최적화를 권한다. 생략된 성분을 복원하므로 토큰이 늘어난다는 점도 밝힌다. 즉 정책 텍스트만으로는 부족하다는 것을 만든 사람이 먼저 인정하고 있다.

### 프롬프트 층의 효용을 실제로 재본 것은 stop-slop-ko뿐

2026-07 벤치마크에서 skill 적용/미적용을 분리 실행해 파이썬 어설션 69개와 블라인드 A/B로 채점했다. 규칙 준수는 적용 100% / 미적용 94.2%였지만 블라인드 품질은 5:5였고, 차이는 양비론 골격·무출처 권위 호소·재료에 없는 수치 생성 세 패턴에서만 났다. 자기참조 채점(Claude가 Claude를 채점)이라는 한계도 스스로 적어두었다.

이 결과의 함의: **잘 프롬프트된 모델 위에 규칙을 더 얹어도 한계 효용은 작다.** 스택을 쌓기 전에 baseline을 재야 하고, 규칙은 전체가 아니라 실제 차이가 난 항목만 가져와야 한다.

### im-not-ai가 참조 아키텍처가 됐다

k-skill v2가 im-not-ai 방법론을 중심으로 재구성했다고 밝히고, yoonmoon도 im-not-ai 구조에서 영감을 받았다고 밝힌다. 후처리 계열의 진단→윤문→finalize 절차와 변경률 30/50 invariant는 이 프로젝트에서 퍼진 것이다. rewrite upstream을 고를 때 파생이 아니라 원류를 고를 근거가 됐다.

### 수정과 진단을 분리한 프로젝트가 나타났다

yoonmoon은 humanize(윤문)와 detect(탐지)를 별도 skill로 두고, detect는 글을 고치지 않고 AI 가능성·신뢰도·근거만 보고한다. korean-writing-reviewer는 evaluate / improve / evaluate-and-improve 모드를 둔다. "고치는 모델이 자기 결과를 괜찮다고 하는" 순환을 끊는 구조가 이미 생태계에 있다.

### 결정론적으로 잴 수 있는 것이 있다

- katfishnet 코드: 붙임 명사·보조 용언 주변 띄어쓰기 비율, POS n-gram 다양성, 쉼표 빈도·위치. 여러 skill이 이 논문을 근거로만 인용하는데 코드 자체를 돌리면 LLM 없이 수치가 나온다.
- korean-report-skills lint.py: 줄·열 단위로 위반을 출력하고 `--fix`로 어미만 자동 수정.
- hanspell: 다음·네이버·부산대 웹 서비스 의존. 오프라인은 hunspell 사전(spellcheck-ko)뿐.

### Claude Code output-style의 동작

시스템 프롬프트의 일부로 세션 시작 시 한 번 읽히고, `/clear`나 새 세션 뒤에 적용되며, 대화 중에 지침을 준수하도록 상기시키는 알림을 트리거한다. 여기에 긴 규칙을 넣으면 매 세션 토큰이 늘고 priming 희석도 커진다.

## 여기서 내린 판단

1. **rewrite taxonomy는 하나만 쓴다.** humanizer들의 패턴 목록이 서로 달라 동시에 올리면 priming이 희석되고 과교정이 겹친다.
2. **LLM 판정과 결정론 판정을 분리한다.** 확실히 잡히는 것(변경률, 금칙어, 숫자 보존, 어미 일관성)은 스크립트로 내리고 LLM에는 문체 판단만 남긴다.
3. **stop-slop-ko를 fluent-korean 바로 다음에 읽는다.** 같은 생성 시점 층에서 평가를 해본 유일한 비교군이다.
4. **im-not-ai를 rewrite의 기준으로, yoonmoon을 diagnose의 기준으로 본다.**
5. **scrooge-mode는 결합 대상이 아니라 측정 방법이다.** fluent-korean이 토큰을 늘리므로 같은 방식으로 전후를 재면 비용 대비 효과가 수치로 남는다.

## 정정한 것

붙여받은 1차 조사 문서에는 dotoricode/korean-humanizer가 소규모로 서술돼 있었는데, 현재는 12카테고리 / 100+ 패턴으로 커져 있다. monologg/humanizer-kr과 hjongc/humanizer-kr은 이름이 같지만 다른 프로젝트다.
