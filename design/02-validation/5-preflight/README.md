# 5-preflight — 구현 흐름 정의

> 이 단계의 문서 지도와 현재 위치입니다. 문서 본문은 영어, 이 README는 한국어입니다 (`AGENTS.md`).

**진행:** 열림 (2026-09-17). [`flow.md`](flow.md)와 [`explorations.md`](explorations.md) 초안 작성됨. 사용자 답(`flow.md` §4 U1~U5)과 실측(X1~X6) 대기. 마지막 상호작용 단계입니다. 사용자가 preflight를 수락하면 빌드는 P1부터 끝까지 자율로 돕니다.

## 입력

- **계획:** [`../4-plan/10_plan.md`](../4-plan/10_plan.md) — 수락됨 (2026-09-17). 단계 P1~P9, 완료 조건, release-blocked 조건
- **스펙:** [`../3-spec/09_toolkit_spec.md`](../3-spec/09_toolkit_spec.md) — 이 단계까지 개정할 수 있고, 6-build에서 멈춥니다
- **시대 01 preflight가 놓친 것:** [`../../01-toolkit/7-review/review.md`](../../01-toolkit/7-review/review.md) §D
- **시대 01 preflight의 형태:** [`../../01-toolkit/5-preflight/flow.md`](../../01-toolkit/5-preflight/flow.md) (결정 표, 검증 run 형식, 단계별 흐름)

## 이 단계가 할 일 (`10_plan.md` §5)

| 항목 | 내용 |
|---|---|
| 실측 | `github` 마켓플레이스 소스를 커밋된 설정에서 읽는지(L4), P1·P8의 canary 방식이 현재 CLI에서 도는지, 이 기기에서 `kiwipiepy` virtualenv 설치 |
| 하네스 가용성 | 하네스별 가용성(P2 실제 세션, P8 배치). "하네스를 쓸 수 없음"을 release-blocked 조건과 대체 경로로 명시 |
| 비용 | pilot과 배치 비용 추정(실행당 약 $0.12), **상한은 사용자가 정함** (P9 release-blocked 조건) |
| 검정력 파라미터 | P8.4용 α, 검정력, 측정별 최소 관심 효과 |
| 빌드 중 사용자 작업 | P3에서 이 기기의 로컬 `outputStyle` 제거 |
| 미리 정할 빌드 선택 | P4 영역 세트 크기, P5 측정별 케이스 수, P8 pilot의 층별 프롬프트 수 |
| 검증 run 형식 | 단계마다 한 번, 독립 `mid` run. 시대 01 `flow.md` §2를 출발점으로 |

문서 구성과 깊이는 사용자와 정합니다.
