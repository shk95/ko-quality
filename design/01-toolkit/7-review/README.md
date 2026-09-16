# 7-review — 구현 후 리뷰

구현이 끝난 뒤 사용자와 함께 되돌아보는 단계입니다. 6-build의 기록을 읽고 다음을 정합니다.

- 6-build의 release-blocked 표시를 하나씩 풀거나 받아들일지. 이것이 master 머지의 조건이다
- 스펙 06 중 구현이 뒤집은 것과, 그것이 스펙 개정감인지 구현 오류인지
- preflight가 놓친 결정과 release를 막는 조건 — 다음 시대의 preflight에 넣을 것
- 서브에이전트 등급 규칙의 재평가. 6-build의 Subagent runs 표에서 large가 mid와 다른 결론을 냈는지, 그것이 결과를 바꿨는지 세어 `AGENTS.md`의 large 조건과 P당 상한(4)을 조정한다
- 다음 시대가 무엇인지. 06 §15가 예고한 검증 단계(gate·features·watch·eval)가 첫 후보다

리뷰의 산출물은 다음 시대의 1-concept 입력입니다. 이 시대의 문서는 여기서 닫힙니다.
