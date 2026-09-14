# ko-quality — agent context

Stateless rules for any agent working in this repository. This file never holds
state. Where the project is and what comes next lives in `design/README.md`.
Read that first, then the documents it points to.

## Layout

| Path | What it is |
|---|---|
| `design/` | Planning, the outside view. One directory per era, seven stage directories inside each, flowing one way. `design/README.md` explains the structure and holds the current position |
| `upstream/` | Their sentences. `lock.yaml` pins commits; `normalized/` is the only upstream content downstream reads; `.cache/` is never committed |
| `assemble/` | Ours. Profiles, presets, agent definitions, skill templates |
| `build/`, `dist/` | Generated. Never hand-edit `dist/` after the build step exists |
| `server/`, `logger/` | MCP server (instructions only for now) and the hook logger |

## Language

- English by default: code, commit messages, this file, anything agent-facing.
- `README.md` files are Korean.
- Design documents: `1-concept/` is Korean — the concept of a Korean-language project is kept in Korean. Stages 2–7, where the agent works with the user, are English. Era 01 predates this rule and stays Korean as a record.
- Korean is allowed inside English prose for terms of art of the Korean language (조사, 어미, 윤문, 번역투, 전보체) and for Korean proper nouns, when the English would be lossy. Not in source code: identifiers, file names, and keys stay ASCII.
- Conversation with the user may be Korean.

## Process: seven stages, one direction

```
concept → exploration → spec → plan → preflight → [build] → review
```

- Stages before `build` are interactive. The depth of `plan` and `preflight` is tuned with the user.
- `preflight` is the last interactive stage. It defines the expected flow of the build, resolves the decisions the build is known to face, and records the verification done ahead of time. Once the user accepts the preflight, the build runs autonomously to completion.
- `build` does not revise the spec. Deviations, surprises, and choices the spec did not make are recorded in `6-build/`. Spec changes come out of `review` and open the next era.
- Nothing flows backward. A discovery that invalidates an earlier stage is recorded where it was found and handled in `review` or the next era. Earlier stage documents are records, not specs: do not edit them; add a forward pointer at most.

## Decisions during build

- Do not stop to ask. If you feel the need to stop, first re-check your confidence: what could you have missed? Look again, then decide.
- Minor decisions: take the recommended or conventional option.
- Major decisions: weigh two candidates — the choice that is best for the build's goal, and the choice that is cheapest to reverse. Prefer the best choice. Because the best choice usually costs more now, first find out whether that cost is worth paying: delegate the exploration to an independent subagent, judge from its report, then pick the one that is worth it.
- Attach a confidence level to every judgment. Low confidence means re-verify before acting, not proceed anyway.
- Each build step ends with a commit and a record in `6-build/`.

## Subagents

- Prefer the lowest-cost model that can do the task; use stronger models only where judgment across many sources is required.
- Verification subagents are independent: they do not see your conclusion, only the question and the sources.
- Never report a subagent's result before it arrives.

## Git

- `master` holds completed build stages. `dev` is the working branch.
- Branch off `dev` for review, fixes, and parallel work; merge back to `dev`. At the end of a build stage, `dev` merges to `master`.
- Commit messages in English, one step per commit.

## Upstream text

- Upstream sentences are theirs: never edit them. Structure is ours.
- An unavoidable sentence change is marked `adapted`, keeps the original beside it, and is counted (spec 06 §5.4).
- Every fragment carries provenance: upstream, commit, path, anchor, content hash, transform grade.

## Public repository

- No personal data, secrets, or machine-specific paths in committed files.
- Logs live outside the tree (`~/.ko-quality/`).
- `.claude/settings.local.json` and `upstream/.cache/` stay ignored.
