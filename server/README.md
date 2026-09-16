# server

MCP 서버 자리입니다. 06에서는 **아무것도 싣지 않습니다.**

- 06 §10은 서버가 `instructions` 필드만 가진다고 했습니다. 실제로 지어 보니 그 필드로 나를 것이 없었습니다.
  - Claude Code: 정책은 출력 스타일과 에이전트 정의가 이미 나릅니다. tool 없는 서버를 실으면 같은 정책의 세 번째 사본이 됩니다(P7 결정).
  - Codex: 정책은 `AGENTS.md` 절이 본문 그대로 나릅니다. 서버 `instructions`는 문서상 "서버의 tools와 함께" 쓰이고, tool 없는 서버에서 닿는지는 문서에 없습니다(P6 결정 2).
- 검증 단계(06 §15)에서 `ko.gate`, `ko.features`, `ko.change_rate`, `ko.preserve` 같은 tool이 생기면 이 디렉터리에 서버가 들어오고, 그때 `instructions`를 함께 다시 봅니다.

근거는 `design/01-toolkit/6-build/P6_codex-build.md`, `P7_server-logger.md`에 있습니다.
