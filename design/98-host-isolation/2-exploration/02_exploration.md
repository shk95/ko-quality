# 02. Exploration: what host state is, how to stop it, where host data lives

> Stage document, era 98. Input: [`../1-concept/01_idea.md`](../1-concept/01_idea.md) (goals A–E and the open questions).
> Measurement: [`tests/runs/98-E/hostscan-prototype.json`](../../../tests/runs/98-E/hostscan-prototype.json).
> Each section ends with a proposed decision (**P-n**) for the user. Nothing here is decided until the user accepts it.

## 1. The boundary of "host state" (goal A, open question 1)

The concept's aim is that a record reads the same to anyone on any machine. That gives a test that sorts every case met in the two rewrites without a list of exceptions:

> **Would a different builder, on a different machine, with a different account, write the same text?** If not, the text carries host state.

| Case met in the rewrites | Same for another builder? | Verdict |
|---|---|---|
| Absolute or home-relative path to the repository, a scratch or temporary directory, a clone name | no | host state |
| Harness session and thread ids, fragments included | no | host state |
| A hash of any of the above (`project`) | no | host state |
| User-scope plugins and marketplaces, the user's model settings | no | host state |
| The account's plan, usage limit, reset date | no | host state |
| A private link that only the owner can open | no | host state |
| The repository's public identity (GitHub owner and name, `LICENSE`) | yes | allowed |
| Tool versions stated as a test condition (`codex-cli 0.154.0`) | yes: the condition is part of the record | allowed |
| A model named as a test condition by the plan or spec (`gpt-5.6-terra`) | yes | allowed |
| A model that is in the record only because it is in the user's own config | no | host state |
| Home directories the project defines (`~/.ko-quality`, `~/.ko-quality-dev`) | yes: the code defines them | allowed |
| Home directories chosen ad hoc for one run | no | host state; refer to them by role |

The last pair is the only judgment call, and the test settles it: a path is allowed when the code or spec names it, and not when a session chose it.

**How a limitation is written.** The rewrites settled this with the user: a harness or account limitation is "not measured; cause not investigated", deferred work is "deferred", and cost is token counts plus API-equivalent cost whatever the login.

**P-1.** Adopt the test above as the rule, with the table as its examples, in `AGENTS.md` "Public repository".

## 2. Check 7: a scan with a host-derived deny list (goal C, open questions 2–4)

A prototype scanner was run over the current history and over the local backups of the history before each rewrite ([record](../../../tests/runs/98-E/hostscan-prototype.json)).

**It is feasible and fast.** Every source the deny list needs can be read at scan time: user name, home, short hostname, the repository's absolute path and its hash, the Claude Code project-directory slug, user-scope plugins and marketplaces, the model in the Codex and Claude Code configs. The tip scans in under a second; the whole history of `dev` and `master` in 7.4 seconds.

**Precision on the current history: 0 true positives, 4 kinds of false positive.**

| False positive | Fix |
|---|---|
| Two user-scope plugin names are common English words and match inside unrelated words | Match host words on word boundaries; for names that are dictionary words, match only the `name@marketplace` form |
| `plus Tier` matched a plan rule case-insensitively | Vocabulary rules are case-sensitive |
| The era 98 concept names the vocabulary it bans | A committed allowlist (below) |
| An elided placeholder path `.../scratchpad/p9/...` | Treat `...`-elided paths as placeholders |

**Recall on the pre-rewrite history: most leaks caught, three kinds missed.**

| Missed | Why | Fix |
|---|---|---|
| The repository path, 58 times | Committed in the home-relative form `~/...`, which the logger's masking and the verifiers produce; the rule matched only the absolute form | Match both forms of every host path |
| A user-scope plugin, a user marketplace, the model setting | **Host drift**: all three had since been removed or changed, so a list read from the current configuration no longer held them | A **local accumulated deny list** (§3): every scan appends the current host values; removed values stay |
| A clone-name fragment, a reset date | Fragments and dates are not rules | Caught through their neighbours in the same file; a file-level hit is enough to stop a commit |

The drift finding is the main result: **a deny list read only from the current host cannot protect the history**, because the host changes and the history does not. The deny list has to remember.

**What a passing scan means (open question 2).** It proves that the text holds none of *this* host's values, present or past. On another contributor's machine it proves the same about that machine. It says nothing across machines, and it does not need to: each machine protects its own state. The fixed patterns (UUIDs in run records, temporary paths, plan vocabulary) are the same everywhere.

**Allowlist.** A committed file lists exemptions as (path, rule, sha256 of the line) with a reason. It never holds a host value, because it records rule names and hashes only. A changed line loses its exemption and is scanned again.

**Where it runs (open questions 3, 4).**

| Place | Scans | Blocks |
|---|---|---|
| `pre-commit` hook | staged files | the commit |
| `commit-msg` hook | the message | the commit |
| `pre-push` hook | every commit in the range being pushed | the push. Once pushed, history is public; this is the last gate |
| `build/checks.py` check 7 | the tip and the whole history of the current branch | the build step |

Hooks need `git config core.hooksPath <dir>` once per clone; this cannot be committed. It joins the README's existing per-machine steps. A clone without hooks is still covered by check 7 at every build step, and a leak found there has not been pushed yet if the push hook is set. Check 7 scanning the whole history costs seconds and catches anything a rewrite left behind.

**P-2.** Check 7 and three hooks as above. Deny list = host values read at scan time + the local accumulated list (§3), in both absolute and home-relative forms, host words on word boundaries. Fixed patterns case-sensitive. Committed allowlist by (path, rule, line hash, reason).

## 3. Local data (goal B, open question 6)

**Today.** Host data sits in about seven places: the real and development log homes (both defined by the spec), three corpus homes chosen per batch, the build's raw material, and the rewrite backups. The 90-day retention runs only when `measure run` is called on a home, and only over its text directories. Session state files (`state/`) are outside retention; one file whose session end was never recorded still holds a prompt. The local note that records where things are was created ad hoc inside one build's scratch copy.

**Proposal.** One local root, whose layout is committed and whose contents are not:

```text
~/.ko-quality-work/                 local root (the path is a project convention, like ~/.ko-quality)
├── LOCAL-NOTES.md                  index: what is where, per era; originals of anything removed from the public record
├── deny.local                      accumulated deny list read by check 7 and the hooks (§2)
└── <era>/
    ├── build/                      raw material of the build: stream logs, progress files, verification transcripts
    ├── corpus/<batch>/             corpus homes (replaces ad hoc --home choices)
    └── rewrites/<date>/            backups made before a history rewrite
```

The log homes `~/.ko-quality` and `~/.ko-quality-dev` stay where the spec puts them; they are the product's and the development session's homes, not build material.

**Retention.**

| Data | Rule | Why |
|---|---|---|
| Log and corpus text | 90 days, as now (09 §20) | unchanged |
| `<era>/build/` | kept until that era's review closes, then deleted | review needs the raw material; after it, the record is the committed summary |
| `<era>/rewrites/` | deleted when the owner confirms the rewritten history | a backup of what was removed must not outlive its purpose |
| `state/` files | the logger deletes files older than 7 days at `SessionStart` | a session that never ended leaves text behind today |
| `LOCAL-NOTES.md`, `deny.local` | kept | the deny list must remember past host values (§2) |

**P-3.** The local root and layout above as a committed convention (in `AGENTS.md` and the root README's per-machine steps). Era-based deletion of build material, owner-confirmed deletion of rewrite backups, a 7-day sweep of `state/`.

## 4. Sources that write host state (goal D)

| Source | Today | Proposal |
|---|---|---|
| Corpus summaries (`*-sessions.json`) | Built by the builder from the local progress file, `session_id` included | A `corpus summary` command writes the commit-safe summary: `key` and outcomes, no `session_id`. The key-to-session map stays in the local progress file |
| Canary reports | `corpus/generator.py` puts `session_id` into the report the builder commits | Same command; the report keeps session ids only in its local copy |
| Harness command logs (the era 01 Codex records) | Command strings committed as captured | One masking helper, shared with the logger's `mask()`, extended with the fixed patterns of §2; every committed run summary passes through it |
| Codex cost | Not reported by Codex, so written as 0 | A committed price table (model, input, cached input, output per 1M tokens, source URL, date). Cost is computed from token counts |

The price table's source is the official pricing page ([OpenAI API pricing](https://developers.openai.com/api/docs/pricing)). Third-party pages report `gpt-5.6-terra` at $2.00 input and $12.00 output per 1M tokens after a 2026-07-30 price cut ([Layer3 Labs](https://www.layer3labs.io/guides/gpt-5-6-pricing), [pricepertoken](https://pricepertoken.com/pricing-page/model/openai-gpt-5.6-terra)); the build reads the official page. At those rates era 02's P2 Codex run (83,703 input, 318 output tokens) would be about $0.17. The P2 record is not changed: it stays "not computed", as the rewrite left it.

**P-4.** A `corpus summary` command, one shared masking helper, and a committed price table read from the official page.

## 5. The `project` identifier (goal E, open question 5)

The concept listed `project` (a hash of the repository's absolute path) as host-bound. Reading its purpose changes the picture.

- 09 §21.1 gives it one job: to show, **inside a local log**, which records came from this repository, so they can be excluded from a sample (09 §21.3).
- Nothing in `measure/` reads it. The exclusion 09 §21.3 relies on also works by location (a separate home).
- A local log never leaves the host. Inside one host, a path hash identifies a project correctly.

The harm in the rewrites was **committing** the value, not having it. Check 7's repo-path-hash rule now blocks that. Replacing it with a repository-intrinsic value (a committed random id, or the first commit's hash) would make `project` agree across clones, which no plan uses; the first commit's hash would also change at every rewrite, as it just did. The cost is a spec change to 09 §12.1 and a migration of existing local logs.

**P-5.** Keep `project` as it is. Goal E is closed as "not host-bound where it lives". Check 7 keeps it out of the public record.

## 6. What this leaves for the spec

| Goal | Proposal | Spec would state |
|---|---|---|
| A | P-1 | The rule text for `AGENTS.md`, with the test and the table |
| B | P-3 | The local root, layout, retention, per-machine steps |
| C | P-2 | Check 7, hooks, deny list sources and forms, allowlist format |
| D | P-4 | `corpus summary`, the masking helper, the price table |
| E | P-5 | Nothing; a forward note in the spec that 09 §12.1 stands |

Order for the build, unchanged from the concept: C first, then A and B, then D.
