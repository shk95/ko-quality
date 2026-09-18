# ko-quality — agent context

Stateless rules for any agent working in this repository, whichever harness runs
it (Codex reads this file directly; Claude Code reads it through `CLAUDE.md`).
This file never holds state. Where the project is and what comes next lives in
`design/README.md`. Read that first, then the documents it points to.

## Layout

| Path | What it is |
|---|---|
| `design/` | Planning, the outside view. One directory per era, seven stage directories inside each, flowing one way. `design/README.md` explains the structure and holds the current position |
| `upstream/` | Their sentences. `lock.yaml` pins commits; `normalized/` is the only upstream content downstream reads; `.cache/` is never committed |
| `assemble/` | Ours. Profiles, presets, agent definitions, skill templates |
| `build/`, `dist/` | Generated. Never hand-edit `dist/` after the build step exists |
| `logger/` | The hook logger. Standard library only |
| `measure/` | Offline measurement runner and judge runs. The only place a third-party import is allowed (check 6) |
| `corpus/` | Corpus generator and prompt set. Records never live here |
| `gate/` | Reserved for a gate executable. README only in era 02 |
| `hostguard/` | Host isolation (era 98): the host-state scan behind check 7 and the git hooks, the local root's `status`/`clean`, `redact` for committed summaries. Standard library only |
| `tests/` | Test cases, run summaries, and the provenance recomputation check (`check_provenance.py`, called by `build/checks.py` as part of check 1). Raw run logs stay in the local root, outside the tree |

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
- A cost estimate in `preflight` comes from a measured probe of the configuration the build will run, not from a per-run reference cost (era 02 review, C).
- `build` does not revise the spec. Deviations, surprises, and choices the spec did not make are recorded in `6-build/`. Spec changes come out of `review` and open the next era.
- Nothing flows backward. A discovery that invalidates an earlier stage is recorded where it was found and handled in `review` or the next era. Earlier stage documents are records, not specs: do not edit them; add a forward pointer at most.

## Decisions during build

- The build never halts. If you feel the need to stop, re-check your confidence: what could you have missed? Look again, then decide and continue. Whatever would have been a reason to stop — a mechanism that does not work as specified, a done-condition you cannot reach, a license or legal doubt — is handled by taking the cheapest-to-reverse path and marking the record **release-blocked** with the reason. Whether `dev` merges to `master` is decided in review, not during the build.
- Minor decisions: take the recommended or conventional option.
- Major decisions: weigh two candidates — the choice that is best for the build's goal, and the choice that is cheapest to reverse. Prefer the best choice. Because the best choice usually costs more now, first find out whether that cost is worth paying: delegate the exploration to an independent subagent, judge from its report, then pick the one that is worth it.
- Attach a confidence level to every judgment. Low confidence means re-verify before acting, not proceed anyway.
- A major decision below medium-high confidence gets an exploration run before it is acted on, within the cap. `preflight` names the decisions it expects to need one (era 02 review, C).
- Each build step ends with a commit and a record in `6-build/`. A stage's done-condition is confirmed by an independent verification subagent, not by the builder's own claim.

## Subagents

Three tiers, named by role so the rules read the same in every harness.

| Tier | Use for | Claude Code | Codex |
|---|---|---|---|
| small | Mechanical work: file maps, counting, diffing, extraction checks | Haiku 4.5 | `gpt-5.6-luna` |
| mid | Exploration and verification: compare two options, check a claim against sources, verify a stage's done-condition | Sonnet 5 | `gpt-5.6-terra`, effort `high` |
| large | Escalation only (below) | Opus 5 | `gpt-5.6-sol`, effort `high` |
| docs | Documentation lookups about a harness (flags, file formats, documented behavior) | `claude-code-guide` agent | — |

- Default to `mid` for exploration and verification, `small` for mechanical work.
- `docs` answers what a harness documents, not what it does; a live run settles behavior. A `docs` run counts like `mid` against the cap (01-toolkit review, E).
- `large` is allowed only when: two `mid` reports disagree on a major decision (one `large` run breaks the tie instead of a third `mid` run); or the exploration must weigh four or more sources across vendors with judgment, such as deriving the schema in P4 or the record shape in P7. A `large` run counts as two runs against the cap. At most one per stage. These conditions are a starting point: review re-evaluates them after the first era from the recorded runs (did `large` reach a different conclusion than `mid`, and did it matter).
- **Cap: 4 exploration runs per build stage (P).** When the cap is reached, remaining decisions in that stage take the cheapest-to-reverse option and are recorded as such. One verification run per stage, for the stage's done-condition, is outside the cap.
- Verification subagents are independent: they receive the question and the sources, never your conclusion or leaning. Ask for both sides in one report: the cost of the best option, and where it breaks.
- A verification prompt says what is not expected to exist yet (the build record is written after verification), and limits deletion to the exact paths the subagent created, by full name, never by glob (era 02 review, C; era 98 review, E).
- Every run is recorded in the stage's build record: tier, purpose, tokens, verdict. The record is the measurement; no separate tooling.
- Never report a subagent's result before it arrives.

## Shell

- Long text never goes through an unquoted heredoc. Backticks and `$(...)` in the
  text are executed by the shell, and a half-written command hangs the step with
  nothing written (era 01, P4 and P5). Write long text with a file-writing tool,
  or from a script file, or through a quoted heredoc (`<<'EOF'`).

## Git

- `master` holds completed build stages. `dev` is the working branch. The merge to `master` is a review decision: every release-blocked mark in `6-build/` is resolved or accepted there.
- Branch off `dev` for review, fixes, and parallel work; merge back to `dev`. At the end of a build stage, `dev` merges to `master`.
- Commit messages in English, one step per commit. Before committing, check that the staged set (`git diff --cached --stat`) is the step the message names (era 02 review, C).

## Upstream text

- Upstream sentences are theirs: never edit them. Structure is ours.
- An unavoidable sentence change is marked `adapted`, keeps the original beside it, and is counted (spec 06 §5.4).
- Every fragment carries provenance: upstream, commit, path, anchor, content hash, transform grade.

## Public repository

The test for every committed file and every commit message: **would a different builder, on a different machine, with a different account, write the same text?** If not, the text carries host state, and host state is never committed. Privacy is part of it; the rest is that a record bound to one machine cannot be read or reproduced by anyone else.

| Host state (never committed) | Allowed |
|---|---|
| Absolute or home-relative paths to the repository, scratch or temporary directories, clone names | The repository's public identity (GitHub owner and name, `LICENSE`) |
| Harness session and thread ids, fragments included | Tool versions stated as a test condition |
| Values derived from any of these (the logger's `project` hash) | Models named as test conditions by a plan or spec (`hostguard/conditions.txt`) |
| User-scope plugins and marketplaces, the user's model settings | Home directories the code defines (`~/.ko-quality`, `~/.ko-quality-dev`, `~/.ko-quality-work`) |
| The account's plan, usage limit, reset date; private links only the owner can open | |

- Local data is named by role (`<scratch>`, `<local>`, `<build>`), never by path. Committed summaries are written through `hostguard.redact`; corpus session lists through `python3 -m corpus summary`.
- A harness or account limitation is written "not measured; cause not investigated". Deferred work is "deferred", never a date.
- Cost is token counts and API-equivalent cost (`measure/cost.py`), whatever the login.
- Enforcement: check 7 and the `pre-commit`, `commit-msg` and `pre-push` hooks (`git config core.hooksPath hostguard/hooks`, once per clone). A false positive is exempted in `hostguard/allow.tsv` with a reason; a real hit is removed. Never bypass a hook with `--no-verify`.
- Host data lives in the local root (`~/.ko-quality-work`, era 98 spec §2.3): build material, corpus homes, rewrite backups, `LOCAL-NOTES.md`, `deny.local`. Logs stay in their homes. `.claude/settings.local.json` and `upstream/.cache/` stay ignored.
- Nothing local is deleted automatically. When an era's `7-review` closes (`python3 -m hostguard mark-reviewed <era>`) and after a history rewrite, run `python3 -m hostguard status` and ask the user which candidates to delete.
