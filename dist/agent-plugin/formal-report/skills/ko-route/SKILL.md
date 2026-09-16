---
name: ko-route
description: Runs a Korean writing-quality preset over a text — review (diagnose), edit (rewrite, then grammar) or full — in the order this toolkit defines. Use when the user names a preset or asks for a combined Korean quality pass. For a single task use ko-rewrite, ko-diagnose or ko-grammar directly.
metadata:
  provenance: SKILL.provenance.yaml
---

# ko-route

## Presets

- `quick`: nothing to run
- `standard`: nothing to run (the policy is already active)
- `review`: `ko-diagnose`
- `edit`: `ko-rewrite`, then `ko-grammar`
- `full`: `ko-rewrite`, then `ko-grammar`, then `ko-diagnose` (the policy is already active)

- Plugin `ko-quality` is profile `agent-reply` (에이전트가 사용자에게 하는 보고·설명); its default preset is `standard`.
- Plugin `ko-quality-formal` is profile `formal-report` (사용자에게 전달되는 문서); its default preset is `full`.

## How to run a preset

1. Use the preset the user named. If none was named, use the default preset of the installed profile above.
2. Run the listed skills in that order. When a skill changes the text (ko-rewrite, ko-grammar), give its result to the next skill. ko-diagnose never changes the text.
3. Reply with the final text if it changed, then each skill's report in order.

The order is what this toolkit recommends; it is not enforced (06 §13.3).
