# measure

오프라인 측정 도구입니다(설계 09 §15). 로거가 남긴 레코드를 읽고, 제외 패스를 한 번 거친 뒤, 파생 레코드를 씁니다. **세션 안에서 돌지 않고, 계산한 값은 어떤 모델에도 닿지 않습니다.**

## 무엇을 하나

```text
$KO_QUALITY_HOME
├── logs/<yyyy-mm>.jsonl          로거가 씀. 여기서는 읽기만
├── annotations/<yyyy-mm>.jsonl   코퍼스 생성기가 씀. session_id로 붙임
└── derived/<yyyy-mm>.jsonl       이 도구만 씀. record_id로 붙음
```

1. **보존 기한 먼저.** 실행할 때마다 텍스트가 든 월별 파일(`logs/`, `judge/`, `grader/`, `exports/`)중 그 달의 마지막 날이 90일보다 오래된 것을 지우고, 지운 목록을 보고합니다. 되돌릴 수 없습니다. `derived/`와 `annotations/`는 지우지 않습니다(09 §20).
2. **제외 패스**(`exclusion.py`, 09 §15.2). 코드, URL·경로·식별자, 출처 있는 직접 인용, 숫자·날짜·단위·통화, 수식·화학식, 법조문, 영문 약어, 고유명사를 줄 단위로 걸러 내고, 제목·목록·표 행은 따로 표시합니다. 버전은 `exclusion_version`으로 기록됩니다.
3. **파생 필드.** `instruction_lang`, `artifact_lang`(제외 뒤 한글 비율), `usable`(제외 뒤 한국어 어절 20개 이상. 걸러 내는 조건으로 쓰지 않는 표시일 뿐입니다).
4. **측정값**(`measurements/`). 측정마다 층(`policy`, `skill`)과 단계(Tier)를 밝히고, 숫자와 비율만 냅니다. upstream의 기준값(`문단 3회+` 등)은 `data/phrase_battery.json`에 자료로만 두고 적용하지 않습니다. Tier 1과 Tier 2는 P6에서 들어옵니다.

같은 입력으로 다시 돌리면 같은 파생 레코드가 나옵니다. 로그가 기한으로 지워져도 파생 레코드는 남습니다.

## 실행

```sh
python3 -m measure run --home ~/.ko-quality-corpus --report report.json
python3 -m measure exclusion-cases          # tests/exclusion-cases의 구역별 놓친 수
python3 -m measure cases                    # tests/measure-cases의 맞는 사례·틀린 사례
python3 tests/measure_runner_test.py        # 보존 기한과 재실행 동일성
```

## 가상 환경

Tier 0은 표준 라이브러리만 씁니다. Tier 1이 쓰는 형태소 분석기(`kiwipiepy`, LGPL-3.0)는 **이 디렉터리에서만** 쓰고, 시스템 Python에 설치하지 않습니다. 로거·빌드·배포물은 이것을 가져오지 않으며 빌드 검사 6이 지킵니다.

```sh
python3 -m venv measure/.venv
measure/.venv/bin/pip install -r measure/requirements.txt
measure/.venv/bin/python -m measure run --home <홈>
```

`measure/.venv/`는 커밋하지 않습니다.
