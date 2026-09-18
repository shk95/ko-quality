# 시대 99 — Codex 채널 재시험 (임시)

미뤄 둔 실측 하나만 담는 **임시 시대**입니다. 시대 01이 `master` 머지 때 받아들인 release-blocked 세 건(A1~A3)과 재판단 대상 둘(C1, C4)이 여기 있습니다. 전부 Codex 쪽입니다.

**현재 위치:** 재시험 끝 (2026-09-16). 시대 02의 `3-spec` 중에 돌렸습니다. A1·A2·A3 해소(A1은 `multi_agent_v2` + 비ephemeral 조건), C1 원인 확인(경로 안내가 경로를 적은 단계와 19줄 떨어져 있었음, 단계 바로 아래로 옮기면 3/3), C4는 CLI 버전이 같아 사실상 재시험 아님. 결정 제안 R1~R4는 시대 02의 스펙(`09_toolkit_spec.md`)이 받습니다.

## 정식 시대와 다른 점

- **일곱 단계를 다 밟지 않습니다.** 새 설계를 열지 않고, 이미 정해진 다섯 항목을 관측해 판정만 합니다.
- **스펙을 낳지 않습니다.** 산출물은 판정 결과이고, 그 결과는 시대 02나 그다음 시대의 스펙 입력으로 들어갑니다.
- **번호 `99`는 임시라는 표시입니다.** 정식 시대 번호를 쓰지 않습니다. 끝나면 결과를 인계하고 이 디렉터리는 기록으로 남습니다.

## 문서 지도

| 파일 | 내용 | 상태 |
|---|---|---|
| [`1-concept/01_idea.md`](1-concept/01_idea.md) | 왜 따로 두는가, 확인할 다섯 항목, 미리 정해 둔 환경, 열린 질문, 전제 조건 | 작성됨 |
| [`02_retest.md`](02_retest.md) | 관측과 판정, 넘기는 결정 R1~R4. 기록은 [`tests/runs/99-retest/`](../../tests/runs/99-retest/codex-channels.json) | 작성됨 |

## 확인할 다섯 항목

| # | 항목 | 출처 |
|---|---|---|
| A1 | 이름 붙은 커스텀 에이전트 호출 (6회 중 1회 도달) | [`../01-toolkit/6-build/P6_codex-build.md`](../01-toolkit/6-build/P6_codex-build.md) |
| A2 | 서브에이전트 출력을 오케스트레이터와 분리해 포착 | 같은 문서 |
| A3 | Codex 로거 레코드와 hook 환경의 `CLAUDE_PLUGIN_ROOT` | [`../01-toolkit/6-build/P7_server-logger.md`](../01-toolkit/6-build/P7_server-logger.md) |
| C1 | `ko-rewrite` 경로 안내로 충분한지 | [`../01-toolkit/7-review/review.md`](../01-toolkit/7-review/review.md) §C |
| C4 | 매니페스트 위치 (루트 / `.codex-plugin/`) | 같은 문서 |

실행 절차는 P7 기록의 "Release-blocked" 절에 그대로 적혀 있습니다 — 임시 `CODEX_HOME`에 `auth.json` 심볼릭 링크, 스크래치 `KO_QUALITY_HOME`, `codex exec --dangerously-bypass-hook-trust`로 한 번은 평범하게, 한 번은 `korean-reviewer`에 위임.

## 언어

`1-concept/`는 한국어, 이후 문서는 영어입니다 (`AGENTS.md`). `README.md`는 한국어입니다.
