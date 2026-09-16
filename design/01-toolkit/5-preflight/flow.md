# Build flow — era 01-toolkit, P1–P7

> Preflight document. 2026-09-14. **Accepted by the user 2026-09-14.** Defines how the autonomous build (6-build) runs spec 06 §14, answers the decisions that can be answered now, and lists what blocks release. Once the user accepts this file, the build starts at P1 on `dev` and does not stop.
>
> Read before every P: spec 06 §14, the P's section here, and the latest record in `6-build/`. Rules for judgment, subagents and git are in `AGENTS.md` and are not repeated here.

## 1. Decisions settled in preflight

Each row answers an exploration in `explorations.md`, including its counter-argument. Pre-decided answers are not reopened during the build. If build evidence shows a premise false, take the cheapest-to-reverse path, record the deviation with the evidence, and continue.

| # | Decision (06 §16.2) | Answer | Counter-argument and the answer to it | Conf. |
|---|---|---|---|---|
| D1 | im-not-ai procedure source (E1, E1b) | **Skeleton: B** `codex/skills/humanize-korean/SKILL.md` (steps, grades). **Invariants: C** `agents/humanize-monolith.md` 철칙 1–9 (C's bidirectional register wording), plus 서법 보존 from `quick-rules.header.md`. C-only steps that carry an invariant (anchor_ledger extract/protect/verify) come in from C as `selected`. A's chatbot-residue input-hygiene line comes in as `selected`. B's own 철칙 block, its `_workspace/{run_id}/final.md` step and its precision-mode hint are left out as `selected`. Target: 0 `adapted` | B is a stale fork (last touched 2026-08-09; C and A changed after). Answer: invariants are anchored to C and the header, which are maintained, so upstream changes there surface as hash failures. B's steps are re-diffed against C's on every lock bump (P4 update test, and in every later era) | medium |
| D2 | Anchor form (E2) | Per file type: im-not-ai patterns by **id prefix**, heading path as fallback. yoonmoon sections and fluent-korean style files by **full heading text**. yoonmoon table rows by **heading + first cell** (skip the repeated header row `패턴`). yoonmoon `detect/SKILL.md` by **tag path, case- and underscore-normalized**. fluent-korean README blocks by **bold label**, accepting re-anchoring. The scanner is heading-depth-agnostic and code-fence aware. P1–P3 use these by hand; P4 makes them schema | One form everywhere is simpler. Answer: no single form covers most files, and the one that could fails on exactly the churning files | medium-high |
| D3 | Upstream/ours separation in rendered SKILL.md (E3) | **Sidecar** `SKILL.provenance.yaml` next to each `SKILL.md`: one entry per span, with fragment id, provenance (06 §5.5), `owner: upstream | ours`. No markers inside SKILL.md. Codex accepts the sidecar and a `metadata` frontmatter key (probe, `explorations.md`) | A hand edit to SKILL.md drifts silently. Answer: `dist/` is never hand-edited once the build exists (P5 on). In P1–P3, where files are handmade, the verification run recomputes every span hash from the sidecar | medium |
| D4 | Policy composition, decision ③ (E4) | Blocks appended at the end of the body, in README order. `'사용자님'` kept literal (`verbatim`). Frontmatter `name`/`description` are ours; the original's `keep-coding-instructions` is kept (coding: `true`; not-coding: absent). `force-for-plugin: true` on **agent-reply only**. formal-report gets no subagent clause. Block ids fixed in P3 (§3 P3). **formal-report reachability:** P3 ships formal-report as an unforced style and records it as unreachable; **P5 resolves it through decision ② (build-time profile → one dist per profile, one forced style each)**; fallback: formal-report lives only in agent definitions. Both failing is release-blocked | formal-report sessions also spawn subagents. Answer: subagents get policy from their own definitions (06 §9); the clause only asks the main thread to check its Korean before delegating | medium |
| D5 | Role for non-procedure, non-taxonomy material (E5) | **Temporary role `reference` with a `kind` field** (`rubric`, `research`, `recipes`, `derived`), under `upstream/normalized/reference/<slot>/<name>.yaml`. P1: quick-rules' *selection* (which ids, S1/S2, self-check list) is rendered into `taxonomy.rewrite`, with content anchored to taxonomy entries by id; `rewriting-playbook.md` is **left out** (the steps do not require it) and weak rewrites are watched for. P2: yoonmoon's three go in with `kind`. P4 decides: one role, split by kind, or folded | One bucket mixes three kinds. Answer: `kind` keeps them apart until P4 has four vendors' worth of evidence | medium |
| D6 | Codex headless probe before P1 (E6) | **Done** (`explorations.md`, "Codex probe"). Plugin skill, sidecar and project `AGENTS.md` all work under `codex exec`. The custom agent `.codex/agents/*.toml` was **not reached**, and the hook test was not run. Both carry into P6 | — | — |
| D7 | Verification run format | §2 | — | — |

## 2. Verification run (one per P, outside the cap)

Tier `mid`. The verifier gets the question and the sources, never the builder's conclusion, the record's Decisions table, or its leaning.

```text
You are verifying whether a build stage met its done-condition. You did not build it.
Done-condition (verbatim from flow.md §3 P<n>): <text>
Checks listed for this stage: <list, verbatim>
Artifacts: <paths>. Run logs: <paths>. Commands to reproduce: <commands>.
For each clause of the done-condition and each check:
  verdict: met | not met | cannot tell
  evidence: file:line or log excerpt (quote it)
  how it could still be wrong: the strongest reason this verdict fails
Then: anything the stage produced that contradicts spec 06 or flow.md, with evidence.
Do not fix anything. Do not suggest designs.
```

The answer goes into the P record as-is. "not met" or "cannot tell" on a done-condition clause makes the stage release-blocked for that clause; the build continues.

## 3. Stages

Common to every P:
- **Record:** `6-build/P<n>_<name>.md` with the two tables from `6-build/README.md`, plus sections `Differs from spec`, `Spec did not know`, `Temporary format friction`, `Release-blocked`.
- **Commit:** one step per commit on `dev`; the record's last commit closes the P.
- **Claude Code test harness:** `claude -p "<prompt>" --plugin-dir dist/claude-code --output-format stream-json --verbose --max-turns 8`. Tool calls in the stream are the evidence for "the skill fired" and "which files were read". Logs go to `tests/runs/P<n>/` (committed; no personal paths). `tests/` is a new top-level directory not in `AGENTS.md`'s layout table; P1 adds its row there.
- **Codex test harness:** `codex exec --ephemeral --json -m <model> -C <workdir> "<prompt>"`. Load checks use `gpt-5.6-luna`; behavior checks use `gpt-5.6-terra`. Anything that writes global Codex state uses a temporary `CODEX_HOME` holding only a symlink to `auth.json`, deleted afterwards. The user's `~/.codex` is never edited.
- **Test inputs:** upstream fixtures where they exist (im-not-ai `tests/golden/fixtures/*/input.txt`, yoonmoon `skills/humanize/references/examples.md`), read from `upstream/.cache/`, cited by path in `tests/cases/*.yaml`. Our own samples only where upstream has none, marked `owner: ours`.

### P1 — im-not-ai → `ko-rewrite`

- **Inputs:** im-not-ai at the lock commit: B, C, `quick-rules.header.md`, A (hygiene line), `ai-tell-taxonomy.md`, `quick-rules.md` (for the selection only). D1, D2, D3, D5.
- **Steps:**
  1. Fragment map: every fragment D1 names, with anchor and transform. List the 10 invariants with anchors.
  2. Diff B's steps against C's; record each difference and what D1 does with it.
  3. Hand-extract `upstream/normalized/procedure/rewrite.yaml` and `taxonomy/rewrite.yaml` (temporary YAML, §5.5 provenance on every fragment). Hash = sha256 of the fragment's bytes between anchor boundaries, LF, trailing newline stripped (P4 may change it).
  4. `assemble/skills/ko-rewrite.md`: `description` (when to use and when not to) and the calling convention.
  5. By hand: `dist/claude-code/.claude-plugin/plugin.json`, `skills/ko-rewrite/{SKILL.md,SKILL.provenance.yaml}`, `references/taxonomy-rewrite.md`.
  6. Five headless runs: golden `01_register_downgrade`, `02_academic_structure`, a text with numbers/proper nouns/quotes, input containing an instruction (injection), a well-written human text (over-correction), plus one non-rewrite request (should not fire).
- **Checks:** skill fires on rewrite requests and not on the other; steps followed (grade, change-rate report, response shape per B); `references/` read only on rewrite runs; invariants hold (a `small` run diffs numbers, proper nouns, quotes between input and output); SKILL.md body ≤100 lines. Golden `checks.py` may be run as an observation, never as a pass condition (it is a gate, 06 §1).
- **Record (06 §14 P1):** `adapted` count and locations, anchors that held, YAML friction, line count, invariant list with anchors, over-correction observed or not, weak rewrites without the playbook.
- **Done when:** at least one real rewrite is carried out following the procedure, and the sidecar's hashes recompute.
- **Pre-decided:** D1, D2, D3, D5. **Criteria only:** over 100 lines → move non-step material to `references/` first, never cut an invariant; another harness-bound sentence found → `selected` out; skill does not auto-fire → revise `description` once, then invoke explicitly and record the trigger failure.
- **Release-blocked if:** fewer than 10 invariants reach SKILL.md; any `adapted` fragment has no `original`; done-condition not met.
- **Alternative:** if B's steps prove unusable, C's steps as `selected` (cost: length, see E1b).

### P2 — yoonmoon → `ko-diagnose`

- **Inputs:** `skills/detect/SKILL.md`, `skills/humanize/references/ai-tell-taxonomy.md`, `detect/references/{lread-rubric,xdac-research}.md`, `humanize/references/katfishnet-research.md`. P1's temporary YAML as-is.
- **Steps:**
  1. Use P1's YAML shape unchanged; every misfit goes to `Temporary format friction` (P4 material).
  2. `normalized/procedure/diagnose.yaml` (tag-path anchors), `taxonomy/diagnose.yaml` (section titles; rows by heading + first cell), `reference/diagnose/{lread-rubric,katfishnet-research,xdac-research}.yaml` (`kind`: rubric, research, research).
  3. `assemble/skills/ko-diagnose.md`; `dist/claude-code/skills/ko-diagnose/` with sidecar and `references/`.
  4. Links to files we do not supply (`../../translate-polish/...`) stay verbatim; record them.
  5. Four runs: a long AI-ish text, a human text, a short SNS text (xdac read expected), a request to fix the text (must diagnose only).
- **Checks:** output follows `<outputFormat>` (one-line verdict, evidence summary, signal table, suspect spans); no text modified; `ko-rewrite` and `ko-diagnose` never read each other's references (tool log + grep of both skill dirs); xdac read only on the short text.
- **Done when:** a diagnosis report comes out without modifying the text.
- **Pre-decided:** D2, D3, D5 `kind` values. **Criteria only:** a fragment fits neither procedure nor taxonomy nor reference → `reference` with a new `kind`, recorded.
- **Release-blocked if:** taxonomy isolation cannot hold without changing upstream sentences; done-condition not met.
- **Record also:** the 11th category's reuse of fluent-korean example sentences (06b P0 e), as verification-era material.

### P3 — fluent-korean → `policy`

- **Inputs:** `plugins/fluent-korean/output-styles/{fluent-korean,fluent-korean-not-coding}.md`, README `## 세부 동작` blocks 1–7. D4.
- **Steps:**
  1. `normalized/policy/fluent-korean.yaml`: variants `coding`, `not-coding` (intro paragraph + H2 sections), frontmatter as data, blocks 1–7 with ids `beginner`, `honorific`, `plain-vocabulary`, `all-korean-output`, `style-sensitive`, `think-in-korean`, `proofreading`.
  2. `dist/claude-code/output-styles/agent-reply.md` (coding body, forced) and `formal-report.md` (not-coding body + `honorific`, unforced).
  3. `agents/korean-reviewer.md` with the agent-reply policy text in its body (binding revisited in P5).
  4. **Channel test, in a throwaway copy outside `dist/`:** add a canary line to the style and to the agent body. Headless: (a) main reply shows the style canary; (b) delegation to `korean-reviewer` shows the agent canary; (c) with `outputStyle` set to formal-report, record which canary wins.
  5. Real policy runs (no canaries): one Korean report request in the main thread, one delegated review.
- **Checks:** policy reaches the main thread and the subagent (06 §2.1 constraint); body text in `dist/` is byte-identical to normalized fragments; `adapted` = 0.
- **Done when:** decision ③ is recorded in the P3 record with evidence, and the proposed 06 revision is listed under `Differs from spec` for 7-review.
- **Pre-decided:** D4, block ids. **Criteria only:** stop-slop-ko stays out (06 §16.2).
- **Release-blocked if:** the agent definition does not carry policy to the subagent; the forced style does not apply in the main thread.

### P4 — abstraction

- **Inputs:** P1–P3 normalized YAML and records.
- **Steps:**
  1. Derive `upstream/interface/{policy,procedure,taxonomy,reference}.schema.yaml`. Decide D5's final shape here. `large` is allowed for this derivation (`AGENTS.md`).
  2. `upstream/extractors/*.py`: anchor scanner (D2 forms, depth-agnostic, fence-aware, table header skip, tag normalization), hash, grade. Failures "anchor not found" and "hash differs" are distinct.
  3. Code output vs hand output: **diff 0**; every non-zero line explained and fixed on one side.
  4. **Abstraction test:** a fresh `mid` run gets only the schemas, the extractor conventions and korean-skills `grammar-checker/` files, and extracts `procedure/grammar.yaml`. It never sees P1–P3 YAML. Counts against the cap. Also decide the role of `references/{rules,common-errors}.md` (06 §7).
  5. **Update test:** bump im-not-ai in `lock.yaml` to its current upstream HEAD (if unchanged since the lock, move back ~10 commits and forward). Re-extract; the normalized diff must be readable. Re-diff B's steps against C's and the header's invariants (D1).
- **Checks:** 06 §12 check 1 runs over all four vendors.
- **Done when:** the fourth vendor is in and check 1 runs.
- **Pre-decided:** D2 as schema input. **Criteria only:** schema change needed for korean-skills → make it and record what and why (not blocking); hash rule change → re-hash all and record.
- **Release-blocked if:** diff ≠ 0 remains unexplained; check 1 cannot run.

### P5 — assemble and Claude Code build

- **Steps:** `assemble/` complete (profiles 2, `presets.yaml`, agents 3, skill templates 4); `build/claude_code.py` → `dist/claude-code/`; diff against P1–P3 hand artifacts; 06 §12 checks 2–4 within the Claude Code output; `claude plugin eval` on/off; removal procedure in the install doc.
- **Decisions, criteria only:**
  - **② runtime vs build-time profile:** leaning build-time. It must make both profiles reachable (D4): one dist per profile, one forced style each, and an install doc that stops both being enabled together. If that fails, formal-report becomes agent-only (D4 fallback).
  - **Agent–profile binding (§8):** follows ② — per-profile dist renders the same agent names with that profile's policy.
  - **`policy` as a preset step (§6):** cheapest is "none" (policy is already injected at build time); choose re-injection only if P3 runs showed policy fading in long outputs.
  - **`claude plugin eval` scope:** minimum is one on/off suite per skill trigger plus one policy prompt per profile.
- **Done when:** the Claude Code part of §14.3: installed, policy on main and subagent, `korean-reviewer` and `korean-editor` invoked, checks 2–4 pass for this dist.
- **Release-blocked if:** a profile is unreachable under both ② and the fallback; build output differs from hand output without explanation.

### P6 — Codex build

- **Inputs:** the probe results (D6).
- **Steps:** `build/agent_plugin.py` → `dist/agent-plugin/` + `install/`; `AGENTS.md` section insert/remove with markers, idempotent; MCP resources re-check; checks 2–4 across both dists.
- **Subagent route (probe: not reached):** try in order, each a load check: explicit agent type if `spawn_agent` exposes one under another model or `codex features list` flag; `$CODEX_HOME/agents/` instead of project `.codex/agents/`; `gpt-5.6-terra` and the default model. No route → policy reaches Codex subagents through `AGENTS.md` (probe: it does), and "`korean-reviewer` invoked in Codex" is release-blocked with the evidence.
- **Hook bundle:** `extensions.com.openai.hooks`, test requires `--dangerously-bypass-hook-trust` (§4). Not permitted → `install/.codex/hooks.json` path documented, and the hook part is release-blocked as untested.
- **Decisions, criteria only:**
  - **Main-thread injection point:** leaning global `AGENTS.md` section with markers (applies everywhere, like an enabled plugin; the probe showed project `AGENTS.md` reaches main and subagents). `developer_instructions` only if the global file cannot be used cleanly.
  - **`instructions` channel:** leaning none (`AGENTS.md` already carries the body); body `verbatim` second; summary (`adapted`) last.
  - **Manifest location:** root `plugin.json` per 06 §2.2; `.codex-plugin/plugin.json` (worked in the probe) if root fails.
- **Done when:** in Codex, policy applies to main and subagent and a skill is invoked.
- **Release-blocked if:** as above, and any check 2–4 failing across dists.

### P7 — server and minimal logger

- **Steps:** `server/` with `instructions` only (or nothing, following P6); build stamp; `logger/` assembling §11 records from both harnesses' hooks; masking; `~/.ko-quality/logs/`.
- **Decisions, criteria only:**
  - **Build stamp:** leaning `dist/<harness>/ko-quality.stamp.json` with profile, `upstream_versions` from the lock, build commit, built-at. Logger locates it through the hook's plugin-root environment; where a harness gives none, the installer writes the stamp path into the hook command.
  - **Server in the Claude Code dist:** cheapest is no (policy already arrives twice).
  - **`sub-to-sub`:** no method from hook input → drop the value (06 §13.1).
- **Done when:** `usable: true` records accumulate from both harnesses.
- **Release-blocked if:** Codex hooks cannot run in the test (P6) — then only the Claude Code side is verified.

## 4. Needed from the user before the build starts

**Answered 2026-09-14:** the user grants the permission rule. The hook bundle is tested in P6 as planned; if the rule turns out absent at P6, the fallback below applies.

- **Hook trust in automation.** `codex exec --dangerously-bypass-hook-trust` was blocked by Claude Code's auto-mode classifier in preflight. Without a permission rule for it (scoped to the temporary `CODEX_HOME` test), P6's hook bundle and P7's Codex logger are verified only as far as the install doc, and marked release-blocked.

## 5. Release-blocked conditions, collected

Merge `dev` → `master` is decided in 7-review; each mark there is resolved or accepted.

| Stage | Condition |
|---|---|
| any | Done-condition clause "not met" or "cannot tell" by the verification run |
| any | An `adapted` fragment without `original`; an upstream sentence changed without `adapted` |
| P1 | Fewer than 10 invariants in `ko-rewrite` |
| P2 | Taxonomy isolation needs an upstream sentence change |
| P3 | Policy does not reach the subagent through its definition, or the forced style does not apply |
| P4 | Unexplained hand/code diff; check 1 cannot run |
| P5 | A profile unreachable under ② and the agent-only fallback |
| P6 | No route to a Codex custom agent; hook bundle untested; checks 2–4 fail across dists |
| P7 | Codex logger records not produced |
