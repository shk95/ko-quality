# 4-plan — 계획

> 이 단계의 문서 지도와 현재 위치입니다. 문서 본문은 영어, 이 README는 한국어입니다 (`AGENTS.md`).

**진행:** 열림 (2026-09-17). [`10_plan.md`](10_plan.md) 초안 작성됨, 사용자 검토 전. 스펙 09의 사실 오류 하나를 찾았습니다(`10_plan.md` §2.1).

## 입력

진입 검토는 [`../3-spec/09a_findings_spec_close.md`](../3-spec/09a_findings_spec_close.md) §3에 있습니다.

- **구현 대상 스펙:** [`../3-spec/09_toolkit_spec.md`](../3-spec/09_toolkit_spec.md)
- **여기서 정할 결정 (09 §22.2):** 디렉터리 이름, `tool_output_chars` 스캔 상한, 추출기가 rewrite taxonomy를 직접 읽을지(61 → 85), `github` 마켓플레이스 소스, 자기 적용을 켜는 빌드 단계
- **빠진 패턴 id**는 `03_features.md`의 목록이 아니라 파일에서 직접 뽑습니다 (`09a` §1.5)
- **시대 01 preflight가 놓친 것:** [`review.md`](../../01-toolkit/7-review/review.md) §D. 5-preflight의 입력이지만 단계 경계에 영향을 줍니다

## 계획 문서의 형태 (사용자, 2026-09-17)

- `10_plan.md`(영어) 하나. 06 §14를 본뜨고 빌드 단계는 P1부터 새로 매깁니다
- 공통 규칙, 그리고 단계마다 범위(09의 절)·선행 단계·완료 조건(독립 검증 run이 확인할 수 있게)·release-blocked 조건·그 단계에서 정할 결정
- **깊이:** 단계, 의존 순서, 완료 조건까지. 파일 단위 실행 흐름은 5-preflight

순서의 출발점은 `09a` §3.3에 있습니다.
