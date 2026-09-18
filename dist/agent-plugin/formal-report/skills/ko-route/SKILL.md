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

- Profile `agent-reply` (coding-terse replies to the user): its default preset is `standard`.
- Profile `formal-report` (높임말 to the user, with the address term 사용자님): its default preset is `full`.

## How to run a preset

1. Use the preset the user named. If none was named, use the default preset of the active profile above: the selected output style on Claude Code, or the `ko-quality:begin profile=…` section of `AGENTS.md` on Codex.
2. Run the listed skills in that order. When a skill changes the text (ko-rewrite, ko-grammar), give its result to the next skill. ko-diagnose never changes the text.
3. Reply with the final text if it changed, then each skill's report in order.

The order is what this toolkit recommends; it is not enforced.
