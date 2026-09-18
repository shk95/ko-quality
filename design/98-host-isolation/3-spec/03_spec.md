# 03. Spec: host isolation

> Stage document, era 98. Implements the accepted proposals P-1 to P-5 of [`../2-exploration/02_exploration.md`](../2-exploration/02_exploration.md) (user, 2026-09-18).
> Measured input: [`hostscan-prototype.json`](../../../tests/runs/98-E/hostscan-prototype.json), [`sessionstart-notice.json`](../../../tests/runs/98-spec/sessionstart-notice.json).
> **Process for this era (user, 2026-09-18):** spec, plan, preflight and build run straight through; no independent verification during the build. All verification happens in `7-review`.

## 1. The rule (goal A)

`AGENTS.md` "Public repository" is replaced by a rule built on one test:

> **Would a different builder, on a different machine, with a different account, write the same text?** If not, the text carries host state, and host state is never committed: not in files, not in commit messages.

It carries the example table of exploration §1, and these ways of writing:

- Local data is named by role (`<scratch>`, `<local>`, `<build>`), never by path.
- A harness or account limitation: "not measured; cause not investigated". Deferred work: "deferred", not a date.
- Cost: token counts and API-equivalent cost, whatever the login.

It also carries two process points: when an era's `7-review` closes, and after a history rewrite, run `python3 -m hostguard status` and ask the user what to delete.

## 2. `hostguard/` (goals B and C)

A new top-level package, standard library only (joins check 6's boundary).

| File | Role |
|---|---|
| `hostguard/rules.py` | Deny list: host literals, fixed patterns, conditions |
| `hostguard/scan.py` | Scanning of text, staged files, a commit message, a commit range, a tree, a history |
| `hostguard/local.py` | The local root: `deny.local`, deletion candidates, `status`, `clean`, `notice` |
| `hostguard/redact.py` | `redact(text)`: host literals and fixed patterns replaced by placeholders, for writers of committed summaries |
| `hostguard/__main__.py` | CLI |
| `hostguard/hooks/pre-commit`, `commit-msg`, `pre-push` | Thin shell wrappers around the CLI |
| `hostguard/allow.tsv` | Committed allowlist |
| `hostguard/conditions.txt` | Committed list of model names that are test conditions |

### 2.1 Deny list

**Host literals**, read at every scan:

| Rule | Value | Match |
|---|---|---|
| `host:home` | home directory, absolute | substring |
| `host:user-in-path` | `/<user>/` | substring |
| `host:hostname` | short hostname, if 4+ characters | word boundary |
| `host:repo-path` | repository root, absolute **and** home-relative (`~/…`) | substring |
| `host:repo-path-hash` | sha256 of the absolute root, first 16 hex (the logger's `project`) | substring |
| `host:project-slug` | the Claude Code project-directory slug of the root | substring |
| `host:user-marketplace` | user-scope marketplaces not owned by this project | word boundary |
| `host:user-plugin` | user-scope plugins not owned by this project: `name@marketplace` always; the bare name only if it is not a plain lowercase word | word boundary |
| `host:model-setting` | model in `~/.claude/settings.json` and `~/.codex/config.toml`, unless listed in `conditions.txt` | word boundary |

**`deny.local`** (§2.3) adds every value a previous scan saw and any value the user wrote in by hand. Its rules are matched like the literal they came from.

**Fixed patterns**, case-sensitive:

| Rule | Pattern |
|---|---|
| `fixed:tmp-path` | `/private/tmp/`, `/private/var/`, `/var/folders/`, `/tmp/claude-<digits>` |
| `fixed:nix-path` | `/run/current-system/`, `/nix/store/` |
| `fixed:scratch-path` | a path segment ending in `scratchpad/`, unless the path starts with `...` or `<` |
| `fixed:uuid` | a canonical UUID |
| `fixed:plan-en` | `free plan`, `paid plan`, `Plus plan`, `Pro plan`, `usage limit`, `usage-limit`, `quota`, `rate-limited` |
| `fixed:plan-ko` | `무료 플랜`, `유료 플랜`, `요금제`, `사용 한도`, `계정 한도`, `사용량 한도` |

Excluded from scanning: `upstream/` (their sentences), binary files.

### 2.2 Allowlist

`hostguard/allow.tsv`, one exemption per line: `path<TAB>rule<TAB>line-sha256[:16]<TAB>reason`. It holds rule names and hashes, never a value. A changed line loses its exemption. `python3 -m hostguard allow <path> <line>` prints the line to add; adding it is a deliberate, committed act.

### 2.3 Local root

`$KO_QUALITY_WORK`, default `~/.ko-quality-work`:

```text
LOCAL-NOTES.md        index, per era; originals of anything removed from the public record
deny.local            accumulated deny list: rule<TAB>value per line
<era>/build/          raw build material
<era>/corpus/<batch>/ corpus homes
<era>/rewrites/<date>/ backups made before a history rewrite
<era>/REVIEWED        marker written by `hostguard mark-reviewed <era>` when that era's review closes
```

Every scan appends current host literals that `deny.local` does not yet hold. If the root does not exist, scans still run on the current host literals and `status` says the root is missing.

### 2.4 Deletion candidates: `status`, `clean`, `notice`

Nothing is deleted automatically. `status` lists, with a reason and a size:

| Candidate | Ready when |
|---|---|
| `<era>/build/` | `<era>/REVIEWED` exists |
| `<era>/rewrites/<date>/` | always listed; "delete once the rewritten history is confirmed" |
| Local git refs left by a rewrite (`backup*` branches, `refs/original/`) | always listed, same reason |
| `state/*.json` in the development log home (`KO_QUALITY_HOME` from the committed settings) | older than 7 days |

`clean <id>…` deletes exactly the named candidates, after printing what it will delete. `notice` prints nothing when no candidate is ready. Otherwise it prints one SessionStart JSON object with both channels: `systemMessage` (the UI) and `hookSpecificOutput.additionalContext` asking the model to tell the user once, in one line, how many candidates are ready and to run `python3 -m hostguard status` (the model channel is the measured one). `notice` always exits 0 and never raises.

### 2.5 Where the scan runs

| Place | Command | Scope |
|---|---|---|
| `pre-commit` | `python3 -m hostguard scan --staged` | staged blobs |
| `commit-msg` | `python3 -m hostguard scan --message <file>` | the message |
| `pre-push` | `python3 -m hostguard scan --push` (reads refs from stdin) | every commit in each pushed range: blobs and messages |
| `build/checks.py` check 7 | `hostguard.scan.history("HEAD")` | the tip tree and every commit reachable from `HEAD` |

A hit prints `path:line: rule` and a masked excerpt, and exits 1. Hooks are enabled once per clone with `git config core.hooksPath hostguard/hooks`, added to the root README's per-machine steps.

## 3. Sources (goal D)

- **`python3 -m corpus summary --progress <file> --out <file>`** writes the commit-safe session list: every progress row without `session_id`. The key-to-session map stays in the local progress file.
- **Canary reports:** the canary command writes its full report next to the progress file and a commit-safe copy through `redact`, `session_id` replaced by `<local>`.
- **`redact`** is used by these writers. The logger's own `mask()` is unchanged: it is shipped behaviour (09 §11).
- **`measure/prices.json`**: per model, USD per 1M tokens for input, cached input and output, with `source` (URL) and `retrieved` (date). Values are taken from the provider's official pricing page; a model the page does not list gets no entry. **`measure/cost.py`** `api_equivalent(model, input, cached_input, output)` returns USD or `None` without an entry. Claude Code's `total_cost_usd` is already API-equivalent and is used as reported.

## 4. The `project` identifier (goal E)

Unchanged (09 §12.1). Check 7's `host:repo-path-hash` keeps it out of the public record. **Condition handed to era 03:** if era 03 pools records from more than one machine, revisit `project`; a committed random id is the candidate.

## 5. Other documents

- `design/02-validation/3-spec/09_toolkit_spec.md`: forward pointers at §12.1 (P-5 condition), §13 (check 7), §18 (corpus summaries). Nothing else changes.
- `.claude/settings.json`: a SessionStart hook running `python3 -m hostguard notice`.
- `AGENTS.md`: §1's rule; `hostguard/` in the layout table; the two process points; this era's verification exception is not a rule and stays in this spec.
- Root `README.md` (Korean): per-machine steps for hooks and the local root.
- `corpus/README.md`: corpus homes under the local root.

## 6. Done conditions

1. Check 7 passes on the current history, with every exemption in `allow.tsv` carrying a reason.
2. Each fixed rule and each literal rule has a test case that it catches, and a test case of the false positive it must not catch (exploration §2), with test fixtures built at run time so the fixtures themselves carry no host value.
3. A commit with a planted host value is refused by `pre-commit`, a message with one by `commit-msg`, and a push of a commit carrying one by `pre-push`.
4. `status` lists the candidates of §2.4; `clean` deletes only named ones; `notice` is silent with no candidate and prints both channels with one.
5. `corpus summary` output has no `session_id`; `api_equivalent` computes from a price entry and returns `None` without one.
6. `build/checks.py` passes, check 6 covering `hostguard/`.
