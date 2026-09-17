# 09. Toolkit spec: ko-quality with the validation stage

> Stage document. **Implementation target** for era 02. It replaces [`06_toolkit_spec.md`](../../01-toolkit/3-spec/06_toolkit_spec.md) and is self-contained: a reader does not need 06 to build from it.
>
> **What changed from 06, and why.** Three kinds of input.
> - **B1–B8**: what era 01's build overturned ([`review.md`](../../01-toolkit/7-review/review.md) §B).
> - **B9**: one unforced plugin instead of one forced plugin per profile ([`02_scope.md`](../2-exploration/02_scope.md)). Decided with the user on 2026-09-16.
> - **E2–E7**: the validation stage's measurement, judge, approximations, eval, gate, and scope decisions ([`2-exploration/README.md`](../2-exploration/README.md)).
>
> Each section names its sources in a closing **Basis** line. Section numbers are 09's own. §23 maps 06's sections to 09's.
>
> **Status: draft, written in four bundles and reviewed with the user bundle by bundle. Verified 2026-09-17** by an independent `mid` run over the whole document. It found one unexplained reversal of an E5 handoff (§17), one dropped E4 detail (§11.2 scan cap), and one unassigned field value (§11.3). All three are fixed, and no measured fact was wrong. Supporting probes made during this stage are in `tests/runs/02-spec/`. **Closure check 2026-09-17** ([`09a`](09a_findings_spec_close.md) §1): five gaps found and fixed (G1–G5), re-verified.
> - **Bundle 1** (§1–§10, §13): supply and distribution. **Reviewed (S1 decided).**
> - **Bundle 2** (§11–§12, §14): hooks, logger, and the record. **Reviewed (S2 decided).**
> - **Bundle 3** (§15–§18): measurement, judge, eval, and corpus. **Reviewed (S3 decided).**
> - **Bundle 4** (§19–§23): gate semantics, log data, self-application, decision status, and the section map. **Reviewed (2026-09-17, [`09a`](09a_findings_spec_close.md) §2).**

## 1. Purpose and premises

**Purpose.** Bundle the existing Korean-quality upstreams into one install unit that agents on Claude Code and Codex actually use, **and build the instrument that tells whether it helps.** Era 01 built the first half. Era 02 builds the second, on a temporary corpus.

**Premises.**
- Upstreams work as installed and do what they say. **Whether they help is not assumed.** It is what §15–§18 measure.
- **Upstream sentences are trusted, so they are not edited.** Structure is ours (§5).
- Values an upstream reports about itself, such as change rate and grade, are kept as reported and never promoted to measurements (§14).
- The logger never judges and never blocks. A gate, if one exists, is a separate executable (§19).

**Scope.**
- Supply layer, assembly, and per-harness builds, carried from 06 with B1–B9.
- Logger revisions that make the record usable as a control-group corpus (§11–§12).
- The measurement runner, the judge-validation procedure, the eval runner split, and the offline corpus generator (§15–§18).
- Gate semantics, **designed and not opened** (§19).
- Rules for log text and for this repository's own use of the toolkit (§20–§21).

**Out of scope.**
- `gate:` in profiles, and `watch:` → `gate:` promotion. Era 03.
- Off-rotation in real sessions, `outcome`, and the control-group ethics question. Era 03.
- Codex channel retests. **Era 99 reported on 2026-09-16** (§2.2). Its proposals R1–R4 are taken up in §8, §11, §13 and decision status.
- stop-slop-ko as a policy provider (E7-a). Parked.
- MCP tools. None is needed by anything above (§10).

**The product promise changes in one word.** 06 §1 promised a tool "used once installed". Under B9 it is **used once installed and selected**: the user picks a profile once per project, and the choice persists (§9). This is the cost of B9, accepted on 2026-09-16.

**Basis:** 06 §1; B9; E1; E7.

## 2. Established facts

This spec rests on the facts below. **Each carries its evidence: a run record (measured) or documentation (documented).** Documentation is not behaviour. Era 02 found six cases where they differed (2-exploration README).

### 2.1 Claude Code (2.1.270–2.1.273)

| Fact | Evidence |
|---|---|
| Plugin components: `skills/`, `agents/`, `output-styles/`, `hooks/hooks.json`, `.mcp.json`, `settings.json`, and others. Manifest `.claude-plugin/plugin.json` | documented; P5 |
| **Output styles do not reach subagents.** A subagent runs on its own system prompt | documented; P3 measured |
| A **forced** style (`force-for-plugin: true`) applies without selection and **beats a local `outputStyle`**. Of two forced styles, the first loaded wins | P3, P5; E7 review measured |
| **An unforced style applies only when selected.** A plugin can carry several, selectable and switchable mid-session with `/output-style`, effective from the next turn | 02-E1 measured |
| A plugin style resolves only as **`<plugin.json name>:<style>`**. The bare name and the marketplace entry name do not resolve | 02-E1, 02-E7 measured |
| A style selection is stored in **`<project>/.claude/settings.local.json`**. A local selection **beats** one in the committed `.claude/settings.json` | 02-E1; E7 review measured |
| `claude plugin install --scope local` writes `enabledPlugins` to `settings.local.json` and **limits visibility to that project**. `--scope project` writes it to the committed `settings.json` | 02-E7; E7 review measured |
| A marketplace is recorded in **user** `~/.claude/settings.json` with an absolute path. A relative `directory` marketplace declared in project settings was not loaded headlessly | 02-E7; E7 review measured |
| **Project settings are read only from the launch directory**, not by walking up to a parent or git root | E7 review measured |
| `env` in project settings (local or committed) reaches plugin hooks. **Values are passed literally**: `~` and `$HOME` are not expanded | 02-E7; E7 review measured |
| Plugin agents are namespaced `<plugin.json name>:<agent>` and **coexist** with a project agent of the same bare name. `SubagentStop.agent_type` is exactly the invoked name | P3; E7 review measured |
| Hook payloads carry `session_id`, `cwd` and `prompt_id`. **No payload carries the selected output style or `model`.** No payload carries token usage | P7; 02-E4; 02-E6; [`hook-payloads.json`](../../../tests/runs/02-spec/hook-payloads.json) measured |
| Tool events fired **inside a subagent** carry `agent_id` and `agent_type` under the parent's `session_id`. `SubagentStart` exists | `hook-payloads.json` measured |
| **A subagent report can travel through a `SubagentHandback` tool call.** Its `PostToolUse` input holds the report. `SubagentStop.last_assistant_message` is then a stub, and the orchestrator receives the report as a `UserPromptSubmit` beginning `<agent-message from=`. The `Agent` tool's `PostToolUse` input holds the delegation prompt | `hook-payloads.json` measured, 2.1.273, once. Era 01 on 2.1.270 saw real text in `SubagentStop` |
| A `Stop` hook that returns `decision: block` sends the model back with `reason` as an instruction. **After 8 consecutive blocks the turn ends with an empty result** (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) | 02-E6 measured |
| Removing a plugin leaves traces: an empty `extraKnownMarketplaces` and an orphaned cache marked `.orphaned_at` | P5 measured (B6) |
| `claude plugin eval` graders: `regex` (presence only; negation only by lookahead; JavaScript `RegExp`), `tool_order`, `tool_used`, `file_exists`, `llm`, `baseline`. No code grader. `--runs` is generations, not judgments. Ablation compares plugin on with plugin off | 02-E5 validator; E3 |

### 2.2 Codex (0.154.0)

Carried from 06 §2.2 and **corrected by era 99's retest** ([`02_retest.md`](../../99-codex-retest/02_retest.md), 2026-09-16, same CLI version as era 01).

| Fact | Evidence |
|---|---|
| Plugin: root `plugin.json` + `skills/` (no `$schema` needed). Installed OpenAI plugins use `.codex-plugin/plugin.json`. Hooks bundle under `extensions.com.openai.hooks` and run only after the user trusts them | P6; era 99 (C4 not meaningfully retested) |
| Main-thread policy: a marked section in global or project `AGENTS.md` reaches the main reply | P6; era 99 measured |
| **Custom agents (`.codex/agents/*.toml`) are reached only with `multi_agent_v2` and a persisted thread.** Default `multi_agent` offers no spawn tool in `codex exec`. `--ephemeral` makes a v2 spawn fail with "no thread with id". With v2 and no `--ephemeral`: 3/3 | era 99 measured (A1). Interactive sessions and project-scope agents not tested |
| Inside a spawned custom agent, its `developer_instructions` govern. The `AGENTS.md` section's canary instruction did not appear in the subagent's own message | era 99 measured |
| Plugin hooks get **both `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT`**, so one `hooks.json` serves both harnesses | era 99 measured (A3) |
| Hook payloads: `SessionStart` has `model`. `Stop` has `last_assistant_message`, `stop_hook_active`, `turn_id`. **`SubagentStop` has `agent_id`, `agent_type`, `agent_transcript_path` and the subagent's own `last_assistant_message`.** `PostToolUse` inside a subagent carries `agent_id`/`agent_type` and shares the parent `session_id` | era 99 measured (A2) |
| A skill that points to a renamed reference is found only after a failed read: 3/3 runs tried upstream's `references/quick-rules.md` first | P6; era 99 measured (C1) |
| MCP client issues only `tools/list` and `tools/call` | documented |

### 2.3 Agent Plugins 1.0

Carried from 06 §2.4. Components are Agent Skills and MCP servers only. Claude Code does not participate.

**Basis:** 06 §2; B5, B6, B7; 02-E1, 02-E4, 02-E5, 02-E6, 02-E7 run records; E7 review.

## 3. Layers

Carried from 06 §3, with the MCP row corrected.

| Layer | What | Why there |
|---|---|---|
| **Supply** | Upstream sentences normalized to role formats | Their sentences, our format |
| **Skill** | Procedure instructions + references | Native in both harnesses |
| **Per-harness render** | Policy injection, agent definitions, hook wiring | Format and location differ per harness |
| **Out of the session** | Logger, measurement runner, judge runs, corpus generator | Measurement must not run inside the session it measures (05a) |

06 put `gate`, `features`, and `change_rate` in an MCP layer. E6 moved the gate to a `Stop` hook, and E5 moved measurement offline. **No MCP layer remains** (§10).

**Basis:** 06 §3; E5 §3; E6.

## 4. Directories

```text
ko-quality/
├── design/
├── upstream/                    # theirs
│   ├── lock.yaml
│   ├── interface/               # role schemas (P4): common, policy, procedure, taxonomy, reference
│   ├── extractors/              # per-vendor extractors
│   ├── normalized/{policy,procedure,taxonomy,reference}/   # committed; the only upstream content downstream reads
│   └── .cache/                  # never committed
├── assemble/                    # ours: profiles, presets, agents, skill templates, install docs
├── logger/                      # hook logger (§11)
├── measure/                     # NEW: offline measurement runner and judge runs (§15, §16)
├── corpus/                      # NEW: corpus generator and prompt set, no records (§18)
├── gate/                        # NEW, empty this era: reserved for a gate executable (§19)
├── build/                       # supply + assemble → dist; checks
├── tests/                       # cases, evals, run summaries, provenance check
└── dist/                        # generated
    ├── claude-code/             # ONE plugin (B9) + marketplace
    └── agent-plugin/<profile>/  # one per profile (Codex has no output styles)
```

- `server/` is removed. It held only a README saying nothing is shipped (§10).
- **Records never live in the tree.** The corpus lives under a `KO_QUALITY_HOME` outside it (§18, §20).
- `measure/`, `corpus/`, and `gate/` are proposed names. `4-plan` may rename them. What is fixed is that they are three separate things: the gate must not share a file with the logger or the measurement runner (§19).

**Basis:** 06 §4; E1; E5 §3; E6; P7 decision 4.

## 5. Supply layer

Carried from 06 §5 as built. The changes are the fourth role and the anchor forms.

### 5.1–5.2 Why copy, and the flow

Unchanged from 06 §5.1–§5.2: one install, versions as facts, and composition requires the sentences in hand. `lock.yaml` → `.cache/<name>@<commit>/` → extractor → `normalized/<role>/…yaml` (committed) → `build/` → `dist/`.

### 5.3 Roles

| Role | Holds | Slot | Provider |
|---|---|---|---|
| `policy` | body, variants (coding / not-coding), optional blocks, upstream frontmatter as data | fragment composition possible | fluent-korean |
| `procedure` | steps, invariants, self-check, grades, options, output contract | one per slot | im-not-ai (rewrite), korean-skills (grammar), yoonmoon (diagnose) |
| `taxonomy` | categories, patterns, severities | one per slot | im-not-ai (rewrite), yoonmoon (diagnose) |
| **`reference`** | material a procedure reads that is neither procedure nor taxonomy. `kind: rubric \| research \| recipes \| derived` | per slot, one file per upstream file | yoonmoon (diagnose ×3), korean-skills (grammar ×2) |
| `ruleset` | deterministic rules | **deferred** (§17.4) | candidate `JangHyun-bin/korean-report-skills`, Apache-2.0 with NOTICE (checked 2026-09-16) |

- The `policy` normalization unit is upstream's distribution unit: two variant files plus README's seven optional blocks.
- `reference` was settled in P4 (flow D5). The schema is `upstream/interface/reference.schema.yaml`.

### 5.4 Transform grades

Unchanged: `verbatim` (default), `selected`, `adapted` (only when unavoidable, with the original kept and counted). Era 01 shipped **0 `adapted`**.

### 5.5 Provenance and anchors

Every fragment carries `upstream`, `commit`, `path`, `anchor`, `content_hash` (sha256 of the stored text), and `transform`. `adapted` fragments also carry `original`.

**Anchor rules (B8).**
1. Lines inside a code fence are never headings, and a fenced block is kept whole as one block.
2. An anchor is unique in its file. When a form is not unique, the enclosing position is added. **A repeated anchor gets ` > N`** for its second and later occurrences.
3. Re-extraction reports "anchor not found" and "hash differs" as different failures. Both stop the build.

The anchor forms are the list in `upstream/interface/common.schema.yaml` `anchor.forms`, and that file is normative. Positional forms held over 10 upstream commits in P4's update test.

### 5.6 Lock

Unchanged in shape. Four upstreams, all MIT, checked 2026-09-14. **Adding a provider requires a licence check before extraction.** For the `ruleset` candidate that check is done (Apache-2.0, §17.4). Adoption is deferred for cost, not licence.

**Basis:** 06 §5; B8; P4 decisions 6, 7, 9; E5; E7-a.

## 6. Profiles and presets

```yaml
# assemble/profiles/agent-reply.yaml
id: agent-reply
register: coding-terse replies to the user                     # restated (E4)
policy: policy/fluent-korean#coding
blocks: []
default_preset: standard
intensity: default
output_style:
  name: agent-reply
  description: "…"
```

```yaml
# assemble/profiles/formal-report.yaml
id: formal-report
register: 높임말 to the user, with the address term 사용자님      # restated (E4)
policy: policy/fluent-korean#not-coding
blocks: [honorific]
default_preset: full
intensity: conservative
output_style:
  name: formal-report
  description: "…"
```

**Three changes from 06 §6.**

1. **`register` is restated, not dropped (E4).** 06 said formal-report meant "documents delivered to the user". No mechanism can see that. One style applies to everything the model writes, and measurement is reply-only. What actually separates the profiles is a **conversational register**, and `register` now says so. The plugin and style descriptions follow it.
2. **`exempt` is removed (E7-a).** Its only values, `slop.cta_in_sns` and `slop.polite_email_ending`, were identifiers no upstream ever had. stop-slop-ko has no rule ids, and it applies its register exemptions itself, per block. If a register exemption is ever needed, its form comes from a measured false positive.
3. **`plugin:` and `output_style.force` leave the profile (B9).** There is one plugin, so its name and description live in the build configuration, not in each profile. No style is forced.

**Presets** are unchanged from as built:

```yaml
presets: {quick: [], standard: [policy], review: [diagnose], edit: [rewrite, grammar], full: [policy, rewrite, grammar, diagnose]}
steps:   {policy: null, rewrite: ko-rewrite, grammar: ko-grammar, diagnose: ko-diagnose}
```

`policy: null` is P5 decision 3. The policy is injected at build time, so a preset step has nothing to run. The order of a preset is advice to the model, not a guarantee (§14).

**Basis:** 06 §6; P5 decisions 1, 3; E4 (`register`); E7-a; B9.

## 7. Skills

`dist/…/skills/<name>/SKILL.md` is a build output that joins upstream procedure fragments with our template (`assemble/skills/<name>/`).

| Skill | Procedure | References |
|---|---|---|
| `ko-route` | none (ours) | profiles, presets |
| `ko-rewrite` | `procedure/rewrite` (im-not-ai) | `taxonomy-rewrite.md` |
| `ko-grammar` | `procedure/grammar` (korean-skills) | `reference/grammar/{rules,common-errors}` |
| `ko-diagnose` | `procedure/diagnose` (yoonmoon) | `taxonomy-diagnose.md`, `scoring-and-report.md`, `reference/diagnose/{lread-rubric,katfishnet-research,xdac-research}` |

**Writing rules (B1, B2).**
- **The SKILL.md body holds the procedure** (steps, invariants, self-check, grades, options) **and the calling convention.** It stays within 100 lines. When it does not fit, non-step material moves to `references/` first, and nothing is cut. As built: 27–97 lines.
- References live inside the skill directory, and the body points to them by path.
- **Each skill reads only its own references.** Two taxonomies can still share a context: a request that invokes both `ko-diagnose` and `ko-rewrite` loads both into the main thread. Context separation is a property of agents, not of skills (B2).
- A sidecar `SKILL.provenance.yaml` marks which spans are upstream's (P1 D3).
- `description` states when to use and when not to use the skill, briefly. Codex's skill list budget is 2% of context or 8,000 characters.
- `ko-rewrite`'s invariants are **all** of the chosen upstream source's rules, and none of ours.
- **A redirect for an upstream path sits directly under the upstream sentence that names the path**, not only in the header. Upstream step 1 names `references/quick-rules.md`, which this skill ships as `taxonomy-rewrite.md`. With the note only in the header, Codex read the missing path first in 3/3 runs. With one ours line under the step, it read the right file 3/3 (era 99, R3). The upstream sentence is unchanged, so `adapted` stays at 0.

**Basis:** 06 §7; B1, B2; P1, P2, P4 decision 8.

## 8. Agents

Rendered from neutral YAML in `assemble/agents/`: `korean-writer`, `korean-reviewer`, and `korean-editor`. `prompt.compose` supplies the policy, and `prompt.append` holds our sentences.

| Harness | Format |
|---|---|
| Claude Code | `agents/<name>.md` in the one plugin, invoked as `ko-quality:<name>` |
| Codex | `install/.codex/agents/<name>.toml` per profile dist. Reached only with `multi_agent_v2` and without `--ephemeral` (§2.2). **The install doc requires `[features] multi_agent_v2 = true`**, and the installer does not write it. This lifts era 01's A1 release-blocked mark for that configuration (R1, user 2026-09-16) |

### Agent–profile binding under B9: **decision S1 — option A** (user, 2026-09-16)

Era 01 rendered each agent once per plugin with that plugin's profile policy (P5 decision 2). **B9 leaves one plugin, so one set of agent names, and they need one policy.**

| Option | What it means |
|---|---|
| **A. Agents always carry the `agent-reply` policy** (recommended) | A subagent's reply goes to the orchestrator, not to the user. E4 restated `register` as the register of conversation with the user, and formal-report's honorific block is addressed to the user: "사용자를 '사용자님'이라고 호칭하고…". In a subagent that sentence is misdirected. So the profile governs the main thread, and agents stay constant whichever style is selected. It also keeps check 3 simple and keeps the subagent arm identical across profile arms |
| B. Agents per profile, name-suffixed (`korean-reviewer-formal`) | Doubles the agents, and the model chooses between near-identical descriptions. Carries a user-directed honorific into orchestrator-bound text |

**The consequence of A, stated:** under formal-report, a delegated report returns in agent-reply register, and the main thread restates it for the user in 높임말 with 사용자님. That is the right place for the register change.

**Basis:** 06 §8; P5 decision 2; E4; B9; E7-c (names, coexistence).

## 9. Policy injection

**Still the most important section.** Output styles do not reach subagents, so the policy is written into every agent definition, and that is not optional.

| Injection point | Claude Code | Codex |
|---|---|---|
| Main thread | `output-styles/agent-reply.md`, `output-styles/formal-report.md` in **one plugin, both unforced** (B9). The user selects `ko-quality:<profile>` | Marked section in global `AGENTS.md` (`--scope project` option) |
| Subagents | `agents/<name>.md` body starts with the policy (§8) | `developer_instructions` in `.codex/agents/*.toml` |
| MCP `instructions` | none (P7 decision 4) | none (P6 decision 2) |

**Composition rule (decision ③, as built in P3; B3).**

| Item | Rule |
|---|---|
| Optional blocks | Appended at the end of the body, in README order, one blank line before |
| Block ids | `beginner`, `honorific`, `plain-vocabulary`, `all-korean-output`, `style-sensitive`, `think-in-korean`, `proofreading` |
| Blocks per profile | agent-reply `[]`, formal-report `[honorific]` |
| Frontmatter | `name`, `description` are ours. `keep-coding-instructions` follows upstream: coding `true`, not-coding absent → false |
| `force-for-plugin` | **never set** (B9; 06 set it on agent-reply) |
| Subagent clause (`## 추가 사항`) | Only in the coding variant. Not added to formal-report |

**Selection and its persistence.** Installing selects nothing (02-E1 run A). The install doc tells the user to run `/output-style ko-quality:agent-reply` or `…:formal-report` once per project. The choice lands in that project's `settings.local.json` and persists across sessions. It also applies to every later session in that project, which is the point.

**What B9 buys, and why it was chosen.**
- **Arm B exists** (§18): plugin installed, style unselected. That arm isolates the main-thread policy from the skills and agents that ship with it. Under forcing it could not be constructed.
- One process can alternate profiles across turns, which halves the corpus.
- A profile is one style file (~2 KB), not another 440 KB plugin.

**What B9 costs.**
- Installing alone does nothing on the main thread (§1).
- `policy_on` and `injection_point` as the logger computes them become false positives by construction. The logger fix in §11 is a precondition of arm B, not a follow-up.
- A committed style selection loses to a local one (§2.1), which matters for self-application (§21).

**Basis:** 06 §9; B3; B9; P3; P6 decisions 1–2; P7 decision 4; 02-E1; E4 (`policy_on`).

## 10. MCP server

**None, and `server/` is removed.**

06 §10 reserved an MCP server for `instructions`, and later for `ko.gate`, `ko.features`, `ko.change_rate`, and `ko.preserve`. Every one of them found a better home:

| Was | Now | Why |
|---|---|---|
| `instructions` | not shipped | a third copy of the policy (P7 decision 4); no channel on Codex (P6 decision 2) |
| `ko.gate` | `Stop` hook executable (§19) | a tool the model must choose to call is advice, not a gate (E6) |
| `ko.features`, `ko.preserve` | offline measurement runner (§15) | measurement must not be visible to the model it measures (05a leak gate 3) |
| `ko.change_rate` | unspecified (§15) | no procedure exists (E4 item 8) |

An MCP tool that helps the model **write** (a spelling lookup, say) would be a product feature, not a measurement. If one is proposed, it enters as its own decision, and records produced while it is available are marked, because its output is visible to the model.

**Basis:** 06 §10; P6, P7; E4 item 8; E5; E6; 05a.

## 11. Hooks and the logger

The logger is still the minimal, out-of-harness recorder that 06 §11 specified. What changes is **what it is allowed to believe**. Era 01's logger wrote down what the build stamp implied. Era 02's logger writes down what the hook actually saw, and it leaves every other field empty, to be filled by someone who saw more.

### 11.1 Principles

- It runs outside the harness. The model does not know it exists.
- **It never judges and never blocks.** It prints nothing and always exits 0. A gate is a separate executable (§19).
- **Standard library only.** Era 01 had zero non-stdlib imports, and the logger runs on every turn of a user's session.
- It does not read transcripts. It assembles from hook payloads.
- It spends no tokens.
- **New: it records only what a hook payload establishes.** A field the hook cannot establish is written as `null`, never guessed from the stamp. Other writers fill it, and each writer keeps to its own file (§11.4).
- **New (decision S2, user 2026-09-16): values that need the exclusion pass are not computed in the hook.** These are `instruction_lang`, `artifact_lang` and `usable`. They move to the measurement runner (§15), where the one exclusion pass lives.

**Why S2.** E4 resolved `instruction_lang` and `artifact_lang` as consumers of E2's exclusion pass. E2 made that pass the first thing to build and validate, and it has twelve zones, some of which (proper nouns, product names) need more than a regex. Computing these fields in the hook would force one of two bad outcomes. Either there is a second, weaker exclusion pass in stdlib inside the logger, or the logger imports the analyser that the rest of the design keeps out of the session. With S2, the record carries the raw text, and the derived values come from one implementation, with a version, recomputable whenever the pass improves. **Cost:** a record alone no longer says whether it is usable. The derived store has to be joined, and a live consumer in era 03 would need the runner.

### 11.2 Assembly

State is kept per session, and **within a session per agent** (`agent_id`, or `main`). Both harnesses fire a subagent's tool events under the parent's `session_id`, with `agent_id` set. Era 01's per-session accumulation mixed a subagent's edits into the main thread's `task_type` (era 99 R2; [`hook-payloads.json`](../../../tests/runs/02-spec/hook-payloads.json)).

| Event | What the logger takes | Notes |
|---|---|---|
| `SessionStart` | `session_id`, `cwd`, `model` if present | `model` is present on Codex. **It is absent on Claude Code**, where no hook carries it |
| `UserPromptSubmit` | `prompt` → the turn's `task`, and the turn key (`prompt_id` on Claude Code, `turn_id` on Codex) | **A harness-injected prompt is not a task.** Claude Code delivers a subagent's hand-back to the orchestrator as a `UserPromptSubmit` whose prompt begins `<agent-message from=`. Such prompts are counted in `injected_prompts` and do not overwrite `task` |
| `PostToolUse`, main or per `agent_id` | edit tools and their `file_path`; skills invoked; tool errors; Hangul and Latin character counts of `tool_response` string leaves, **scanning at most a fixed number of characters per call** (the cap is set in `4-plan`), with truncated calls counted | Skills: the Claude Code `Skill` tool's input. On Codex, a shell read of `skills/<name>/SKILL.md` (`skills_method: path-read`) |
| `PostToolUse`, `Agent` tool (Claude Code) | `tool_input.prompt` keyed by the returned `agentId` | The delegation prompt. `coding.19` governs this text, and it is the sub-record's input |
| `PostToolUse`, `SubagentHandback` (Claude Code) | `tool_input.message` keyed by `agent_id` | **The subagent's actual report** where the harness routes it this way |
| `SubagentStop` | sub record: `agent_id`, `agent_type`, output | Output is the captured hand-back message if one exists for that `agent_id`, else `last_assistant_message`. On 2.1.273 the latter was a stub ("I sent my report to the agent that started me.") whenever hand-back was used. On Codex it is the real report (era 99) |
| `Stop` | main record | `last_assistant_message` |
| `SessionEnd` | delete session state | — |

### 11.3 `policy_on`, `injection_point`, `profile`: what a hook can establish

**Measured:** no Claude Code hook payload carries the selected output style or the model ([`hook-payloads.json`](../../../tests/runs/02-spec/hook-payloads.json)). A hook therefore cannot know whether the main-thread policy applied. Under B9 that is exactly the difference between arm B and arm C.

| Record | `plugin_present` | `policy_on` | `injection_point` | `profile` | `policy_method` |
|---|---|---|---|---|---|
| any, stamp found | `true` | — | — | — | — |
| sub, `agent_type` is a shipped agent (Claude Code: `ko-quality:` namespace; Codex: a name the installer wrote, per `ko_quality_codex.py status`) | — | `true` | `agent-definition` | `null`. Agents carry agent-reply policy under S1, but that is not the session's profile | `agent-type` |
| sub, any other `agent_type` | — | `false` | `none` | `null` | `agent-type` |
| main, Codex, a `ko-quality:begin profile=…` marker in the effective `AGENTS.md` (global, or project from `cwd` up to the repository root) | — | `true` | `agents-md` | the marker's profile | `agents-md-marker` |
| main, Codex, no marker | — | `false` | `none` | `null` | `agents-md-marker` |
| **main, Claude Code** | — | **`null`** | **`null`** | **`null`** | `null` |

- **`policy_on` keeps its name** (E4). The design's falsifiability argument is written around it. `plugin_present` is added beside it for what the stamp establishes.
- **Era 02 fills the Claude Code main-thread nulls from outside**: the corpus generator knows the arm it ran and annotates the session (§12.2).
- **Era 03 cannot**, and this is its blocker, now measured rather than suspected. Before era 03 samples real Claude Code sessions, it needs a way to know the effective style. The candidates are reading the settings chain from `cwd`, which is fragile, or a harness field. Neither exists in this spec.

### 11.4 Storage

```text
$KO_QUALITY_HOME  (expanduser applied; default ~/.ko-quality)
├── logs/<yyyy-mm>.jsonl          # logger only. Append-only
├── state/<session_id>.json       # logger only. Deleted at SessionEnd
├── annotations/<yyyy-mm>.jsonl   # corpus generator only (§18). Joined on session_id
└── derived/<yyyy-mm>.jsonl       # measurement runner only (§15). Joined on record id
```

- **One writer per file kind.** No program edits another's records. The logger's file stays append-only.
- **`logs/` is no longer split by profile.** Under B9 the hook does not know the profile (§11.3).
- **`expanduser`** on `KO_QUALITY_HOME`. Claude Code passes settings `env` values literally, so a committed `~/…` value only works if the logger expands it (§2.1, E7-d).
- Never inside a work tree. Retention and use rules are in §20.

### 11.5 Installation

| Harness | How |
|---|---|
| Claude Code | The plugin carries `hooks/hooks.json`. Command: `python3 "${CLAUDE_PLUGIN_ROOT}/logger/ko_quality_log.py" <Event>` |
| Codex | The plugin bundles the same `hooks.json` through `extensions.com.openai.hooks`. **Codex sets both `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT`**, so the command works unchanged (era 99 A3). The user must trust the hooks once |

The event list does not change. `PreToolUse` and `SubagentStart` exist and add nothing the logger needs: `PostToolUse` carries the tool input, and `SubagentStop` carries `agent_id`.

**Basis:** 06 §11; B7; E2 (exclusion pass, stdlib constraint); E4 items 2–7 and additions; E7-d; era 99 A2, A3, R2; [`hook-payloads.json`](../../../tests/runs/02-spec/hook-payloads.json).

## 12. The record, and what joins it

### 12.1 Log record (written by the logger)

```yaml
id: uuid4
ts: datetime
session_id: string                     # NEW — every payload has it; the join key (E4)
turn_key: string?                      # NEW — Claude Code prompt_id / Codex turn_id
project: string?                       # NEW — sha256 of the git root above cwd, else of cwd; first 16 hex (E7-d)
harness: claude-code | codex
harness_position: main-to-user | sub-to-orchestrator
agent_type: string?
agent_id: string?                      # NEW
plugin_present: bool                   # NEW — stamp found
build_id: string?                      # NEW — from the stamp (§13)
tool_version: string?                  # stamp version
upstream_versions: {name: commit}
policy_on: bool?                       # §11.3; null = not established by the hook
injection_point: output-style | agents-md | agent-definition | none | null
profile: string?                       # §11.3
policy_method: string?                 # agents-md-marker | agent-type | null
model: string?                         # null on Claude Code
task: string                           # masked; for sub records, the delegation prompt if captured
output: string                         # masked
injected_prompts: int                  # NEW — harness-injected UserPromptSubmit count this turn
skills_invoked: [string]               # NEW — replaces preset
skills_method: tool | path-read | null
task_type: coding | document | conversation      # Claude Code (E4 item 2)
         | coding | conversation                  # Codex: apply_patch paths unverified
task_type_method: rule | rule-nopath | rule-codex
tool_output_chars: {hangul: int, latin: int, truncated_calls: int}   # NEW — replaces context_en_ratio (E4 item 1); per-call scan capped
tool_errors: int
tokens: {output: int, method: estimate-v2}        # E4 item 6; never read by a threshold
masked: bool
# reserved, absent in era 02 (§19): gate_on, gate_fired, gate_retries, gate_fired_on
```

**Removed from 06 §11.3, and why.**

| Field | Why |
|---|---|
| `preset` | No hook source (B7). A preset's order is advice. What can be observed is which skills ran: `skills_invoked` |
| `instruction_lang`, `artifact_lang`, `usable` | Need the exclusion pass: derived store (S2) |
| `upstream_report` | Never filled in era 01. A skill's self-reported change rate stays inside `output`, where it was written, and is never promoted to a field (E4 item 8) |
| `expect` | Belongs to eval cases (§17), not to session records |
| `task_type_method: rule` alone | Split to show the fallback (E4 item 2) |

**Masking** gains phone numbers, 주민등록번호, card numbers, and the home directory in paths (E7-b). Names stay unmasked. The mask runs at capture, before anything is written.

### 12.2 Annotation record (written by the corpus generator, era 02)

```yaml
session_id: string                     # join key
corpus_prompt_id: string
arm: A | B | C                         # §18
profile_selected: agent-reply | formal-report | null
model: string                          # from the result document
tokens: {output: int, thinking: int, method: usage}   # thinking subtracted (E4 item 6)
sub_to_sub_present: bool
sub_to_sub_method: session-stats       # subagent_stats.spawned_by_subagents (E4 item 7)
generator_version: string
```

When an annotation exists, its values **override** the log record's nulls for analysis, and **never overwrite** the log file. Estimated and measured token counts are never pooled (E4 item 6).

### 12.3 Derived record (written by the measurement runner)

```yaml
record_id: uuid                        # log record id
exclusion_version: string
instruction_lang: ko | en | mixed      # on task after exclusion (E4 item 3)
artifact_lang: ko | en | mixed         # on output after exclusion (E4 item 4)
usable: bool                           # >= 20 Korean 어절 after exclusion — a flag, never a filter (E2)
features: {name: value}                # §15
```

**Basis:** 06 §11.3; B7; E2; E4; E6 (reserved gate fields); E7-b, E7-d; `tests/logger_test.py`, which asserts 06's keys and changes with this schema.

## 13. Build and distribution

```text
upstream/normalized/ ─┐
                      ├─ build/claude_code.py  ─→ dist/claude-code/            (one plugin, B9)
assemble/ ────────────┤
                      └─ build/agent_plugin.py ─→ dist/agent-plugin/<profile>/
```

**Claude Code layout (B4 as built, then B9).**

```text
dist/claude-code/
├── .claude-plugin/marketplace.json     # one entry: ko-quality → ./ko-quality
├── README.md                           # install, SELECT, remove
└── ko-quality/
    ├── .claude-plugin/plugin.json      # name: ko-quality
    ├── output-styles/{agent-reply,formal-report}.md   # unforced
    ├── agents/korean-{writer,reviewer,editor}.md      # agent-reply policy (S1-A)
    ├── skills/…                        # byte-identical to every other dist
    ├── hooks/hooks.json
    ├── logger/ko_quality_log.py
    ├── provenance/policy.yaml
    └── ko-quality.stamp.json
```

- The `ko-quality-formal` plugin is gone. A user who installed it in era 01 removes it. The install doc says so.
- No `$schema` in Codex `plugin.json`. No `mcp.json` or `.mcp.json` anywhere (B4).
- **Stamp (B4, extended).** Written per plugin root, without timestamps, so rebuilds are byte-identical. Fields: `tool`, `version`, `plugin`, `harness`, `upstream_versions`, and **`build_id`**, a hash over the normalized and assembled inputs. It is not a time, so byte-identical rebuilds are kept, and records made under different builds of our own assembly can be told apart (E7-d). **`profile` and `injection_point` leave the Claude Code stamp**: under B9 one plugin carries both profiles, so neither is a property of the installation (§11).
- Version: `0.2.0`. The layout change is breaking for installed users.

**Checks (required).**

1. **Provenance.** Re-extraction matches every `content_hash`, and every sidecar recomputes.
2. **Policy identical.** For each profile, the Claude Code output-style body equals the Codex `AGENTS.md` section body, with frontmatter, markers, and blank lines at the ends removed (P6 decision 8).
3. **Agents identical.** For each agent, the system prompt is the same string in every dist, and it starts with the agent-reply policy body (S1-A).
4. **Skills identical.** `skills/` is byte-identical across every dist.
5. **NEW: agent names.** No `.claude/agents/*.md` in this repository has a `name` that is in `assemble/agents/` (E7-c).
6. **NEW: dependency boundary.** No file under `logger/`, `build/`, `upstream/`, or `dist/` imports anything outside the standard library. Third-party imports are allowed only under `measure/` (S3).

**Behaviour check.** Checks 1–6 see only the build. Whether it takes effect is `claude plugin eval`'s job, for triggers and regressions (§17).

**Removal (B6).** Claude Code: `claude plugin uninstall`, then remove the marketplace. Two traces remain and are documented: an empty `extraKnownMarketplaces` and an orphaned cache under `~/.claude/plugins/cache/<marketplace>/`. **Also remove the style selection** from each project's `settings.local.json`, or the next session asks for a style that no longer exists. That line is new under B9 and not yet measured. Codex: the installer's `uninstall` restores `AGENTS.md` byte for byte (P6).

**Basis:** 06 §12; B4, B6; B9; P5, P6, P7; E7-c, E7-d.

## 14. Approximations, unknowns and structural limits

**This section is part of the spec.** 06 §13.1 said to revisit each approximation before a threshold is set. E4 did that, and this is the result.

### 14.1 Approximations — a value exists, and it is not exact

| Item | Disposition in 09 | Where | Evidence |
|---|---|---|---|
| `context_en_ratio` | Returns as `tool_output_chars` counts, string leaves only. A covariate for English exposure, not the model's English | §12.1 | reasoned |
| `task_type` | Three values on Claude Code, path-aware, source edit wins, `rule-nopath` fallback. Codex keeps two. A stratifying covariate, never an outcome | §12.1 | reasoned; subagent split measured |
| `instruction_lang` | Last user prompt only (injected prompts excluded), after the exclusion pass | §12.3 | E7 records |
| `artifact_lang` mixed | After the exclusion pass. **The contamination rate on code-plus-Korean output is measured on the corpus before any grader reads this field** | §12.3, §15 | E7 records |
| `output` purity / `usable` | Flag kept, **never a filter** for measurements whose defect shortens text. The rate at which quoted user input survives into graded text is measured on the corpus | §12.3, §15 | E2, E7 |
| `tokens.output` | Era 02: actual usage, thinking subtracted, from the generator. Hook: `estimate-v2` = 1.51 × Hangul + 0.34 × other, an order-of-magnitude label (held-out error 19%, 47% on path-heavy Korean). Never pooled with usage | §12.1–§12.2 | run-verified, 10 samples |
| `sub-to-sub` | Session-level `sub_to_sub_present` from `subagent_stats`, generator only. Per-record attribution stays absent. The ordering heuristic is **not adopted** | §12.2 | run-verified (session half) |
| Change rate | Self-report stays in `output`. `ko.preserve` is built (§15). **`ko.change_rate` has no procedure** and is an open obligation (§15) | §15 | E4 item 8 |
| Codex `instructions` | Channel stays closed | — | P6; era 99 did not reopen it |

### 14.2 Unknowns — with the point at which each is checked

| Item | Status | Checked when |
|---|---|---|
| Effective output style visible to any hook or harness field (Claude Code) | **Not available** in 2.1.273 payloads | **Before era 03 samples real sessions**: era 03's blocker |
| Whether Claude Code always routes a subagent report through `SubagentHandback` | Observed once on 2.1.273. Era 01 (2.1.270) saw real text in `SubagentStop` | First corpus batch: count sub records whose output is the stub |
| Codex `apply_patch` payload paths | Untested | When Codex `task_type` needs three values |
| Codex custom agents interactively, project-scope agents | Untested (era 99) | When a Codex arm is added |
| `PreToolUse(Write)` as a gate site | Asserted, not probed; different deny shape (E6) | The era that opens `gate:` |
| A blocking `Stop` hook under a marketplace install | Probed only with `--plugin-dir` (E6) | Same |
| Relative or `github` marketplace source declared in committed settings | Relative `directory` not loaded headlessly; interactive trust untested | `4-plan`, for self-application (§21) |
| `ruleset` provider licence | **Resolved**: Apache-2.0 with NOTICE, checked 2026-09-16 (§17.4) | — |
| Removal clears the style selection from `settings.local.json` (B9) | Not yet measured (§13) | 6-build, when the removal steps are written into `README.md` |
| Whether the extractor reads the rewrite taxonomy directly, so the 24 patterns upstream's generator drops (J-1 among them) enter `normalized/` | `normalized/taxonomy/rewrite.yaml` holds 61 of upstream's 85 (P1, E2). The battery is built from the 61 (§15.4) | `4-plan` |

### 14.3 Structural limits — not fixable here

- **A preset's order is advice.** `ko-route` tells the model the order, and nothing enforces it.
- **The subagent clause is still a clause.** Writing the policy into agent definitions covers one layer. A subagent that spawns another passes the policy on only if the model chooses to.
- **The hook cannot see the main-thread policy on Claude Code** (§11.3). Era 02 fills it in from the generator. Era 03 has no such source yet.
- **Reply length defeats document thresholds.** Upstream thresholds (`문단 3회+`, `4문장+ 연속`) cannot fire in a two-sentence reply, so per-record verdicts carry no variance. Measurements are emitted as raw counts and rates, and aggregated within a stratum (§15).
- **Tier 2 (input + output) exists only where the original was pasted into the prompt.** When the model reads the text from a file, the pair never enters the record. The corpus includes paste-in cases on purpose (§18).
- **Upstream's grade rule caps unchanged text at B.** ko-rewrite grants A only at a 10–25% change rate, so text that needed no change gets B, and the model explains that B is not a defect (P1). The rule is upstream's sentence and is not edited (§5). It reaches no measurement, because a grade is a self-report kept as reported (§1).
- **A record produced after a gate fires is a record of a taught model** (E6). No gate runs in era 02. The fields are reserved (§12.1).

**Basis:** 06 §13; P1; E2; E4; E6; E7; era 99; [`hook-payloads.json`](../../../tests/runs/02-spec/hook-payloads.json).

## 15. Measurement

The measurement runner is an offline program (`measure/`). It reads log records, applies one exclusion pass, computes measurements, and writes derived records (§12.3). **It never runs inside a session, and nothing it computes reaches a model** (05a leak gate 3).

### 15.1 Principles

- **A measurement is a number, not a verdict** (05a). A threshold is `watch:`'s business (§15.7), and a `watch:` value in era 02 is a candidate.
- **Emit raw counts and rates per 100 어절, and aggregate within a stratum.** Do not decide per record. Upstream thresholds assume documents (`문단 3회+`), and on a two-sentence reply they cannot fire, so per-record verdicts have no variance (E2).
- **A measurement is compared only within the layer that was toggled** (E2): `policy`, `skill`, or `agent`. Every measurement declares its layer and its tier.
- **`usable` is a flag, never a filter,** for any measurement whose defect shortens text. If a measurement needs a length floor, it states why, and the excluded count is reported with the result.
- **No false-positive rate, no `watch:` value.** A measurement whose false-positive rate has not been observed on correct Korean carries no threshold, however well upstream documented one.

### 15.2 The exclusion pass (built first, validated first)

One implementation, versioned (`exclusion_version`), shared by every tier and by `instruction_lang`/`artifact_lang`/`usable`. It works **on raw lines, before sentence splitting** (E2: the analyser's splitter merges bullets and table rows).

| Zone | Method | Tier |
|---|---|---|
| fenced code, inline code | markdown parse | 0 |
| URLs, paths, identifiers (`snake_case`, `camelCase`, dotted names) | regex | 0 |
| attributed direct quotation (a quote plus a speech marker) vs rhetorical quotation | regex with marker list | 0 |
| numbers, dates, units, currency | regex | 0 |
| markdown headings, list items, table rows | markdown parse; **kept as separate spans**, since some measurements want them | 0 |
| mathematical and chemical notation | regex | 0 |
| legal text | marker list (`제N조`, `항`, `호`) | 0 |
| industry abbreviations | Latin all-caps tokens | 0 |
| proper nouns, product and model names | `NNP`, plus a Latin-capitalised token list | 1 |

The **done-condition** for the pass: on a labelled set of correct and defective Korean replies that contain every zone, each zone's false-negative count is reported. The pass is not "complete" until it has been measured.

### 15.3 Tiers and dependencies

| Tier | Needs | Runs where |
|---|---|---|
| 0 | stdlib | `measure/` |
| 1 | morphological analyser | `measure/` only |
| 2 | input and output together (paste-in cases only) | `measure/` |

**Decision S3 — option A (user, 2026-09-16): the first third-party dependency.** Tier 1 needs `kiwipiepy` (0.23.2 verified in E2, LGPL-3.0). Era 01 took no third-party dependency at all.

| Option | Consequence |
|---|---|
| **A. Allow it in `measure/` only** (recommended) | Pinned in `measure/requirements.txt` and installed in a virtualenv, never into system Python. **Never imported** by `logger/`, `build/`, `upstream/`, or anything under `dist/`, and a build check enforces that. It is a dependency of our offline tool, not of the shipped plugin, so the LGPL does not reach the distribution. The logger and plugin keep era 01's stdlib-only property |
| B. Tier 0 and Tier 2 regex only; defer Tier 1 | No dependency. It loses `noun_ending_ratio` and `particle_absence_ratio`, the two measurements E2 found to separate correct from telegraphic Korean perfectly once fixed, and `coding.12`/`coding.14` go unmeasured |

### 15.4 The measurements

The list is organised by measurement, not by rule id. Each cites the rules it serves. Names from 04 §6 are kept.

**Tier 0**

| Measurement | Layer | Serves | Emits |
|---|---|---|---|
| `em_dash_count` | policy, skill | coding.17, J-3, diag 8.3 | count, per 100 어절 |
| `emoji_count` | skill | C-5, diag 8.2 | count |
| `bold_density`, `bullet_density`, `header_formula` | skill | diag 8.1/5.2/5.3, C-2/C-9/C-10 | ratio |
| `quote_emphasis_count` | skill | J-2, diag 8.4 | count |
| `phrase_battery`: one table, entries with scope (paragraph or document) | skill (and policy where a policy rule names the phrase) | ~47 rewrite entries (including **G-3, held by upstream as 실증 부족**), diag 1–4, 6, 7, 10. **Coverage gap: the rewrite entries come from the 61 patterns in `normalized/`; the 24 of upstream's 85 that its generator drops are not measured** (§14.2) | **count per entry**; upstream thresholds are stored as data, not applied |
| `english_ratio`: Latin share of prose after exclusion, **on the output** | policy | coding.08, diag 10.2 | ratio |
| `english_gloss_repeat` | skill | B-1, diag 10.1/10.3 | count |
| `sentence_len_var`: mean, stdev, CV, max | skill | E-1, diag 5.4/9.2 | ratio |
| `paragraph_initial_repeat` | skill | C-7, diag 4.2/9.3 | ratio |
| `comma_rate`: overall, plus after connective endings | skill | C-11, diag 4.1, grammar | ratio, count |
| `spelling_denylist`: 되요, 됬, 왠 outside 왠지, `!!!` | skill | grammar | count |
| `quote_balance` | skill | grammar | bool |
| `allomorph_errors`: 을/를, 이/가, 은/는, 와/과, -ㅂ니다/습니다, -ㄹ까요 by 받침 | skill | grammar | count. **Scope: ㄹ-irregular stems and numerals or acronyms whose 받침 follows pronunciation are out of scope, and the count excludes them** (E3) |
| `honorific_address`: `사용자님` present | policy (formal-report) | honorific block | bool |

**Tier 1** (S3-A)

| Measurement | Layer | Serves | Emits | Recipe notes |
|---|---|---|---|---|
| `noun_ending_ratio` | policy | coding.12, diag 11.3 | ratio | **Pop trailing `SF/SP/SS/SE/SO/SW` before testing for `EF`.** Headings and list items are excluded (the rule exempts them) |
| `particle_absence_ratio` | policy | coding.14, diag 11.2 | ratio | **Skip `XSN`/`XSM` when looking ahead, and drop 체언 followed by `XSV`/`XSA` from the denominator** |
| `speech_level` | policy | coding.09, honorific, E-7, grammar | label distribution | Tags matched **by prefix** (`VV-I`, `VV-R` exist). **Never a judge reference** (E3) |
| `noun_run_length` | policy | coding.15 | mean, max | **Strict: consecutive `NN*` tokens with nothing between.** Bridging is not measured (E2 left it open; strict is the conservative reading) |
| `genitive_ui_ratio` | policy | coding.11b, diag 11.6 | ratio | false positive on fixed expressions: predicted, not yet measured |
| `ending_monotony` | skill | E-2, diag 9.1 | ratio | — |
| `pos_ngram_diversity` | skill | diag 9.4 | ratio | — |
| `adnominal_chain_depth` | skill | A-18, diag 1.8 | count | — |
| `suffix_jeok_density` | skill | diag 7.2, F-4/F-5 | ratio | — |
| `spacing_errors` | skill | grammar | count | — |

**Tier 2** (paste-in cases only)

| Measurement | Emits |
|---|---|
| `ko.preserve`: `number_unit_date`, `quote`, `code_url_path`, `proper_noun` (Tier 1), `register` (Tier 1) | `{violations[]}` per kind. A kind passes at zero violations |
| `ko.change_rate` | **Not specified. Deferred** (§15.5) |

**Capture-dependent**

| Measurement | Source |
|---|---|
| `delegation_prompt_*`: the policy-layer Tier 0 and Tier 1 measurements applied to the delegation prompt | coding.19; the sub record's `task` (§11.2) |

### 15.5 `ko.change_rate`: deferred, stated as a debt

04 §6 defines it as `before, after, preserve_spans → ratio`, at morpheme level, with preserved spans excluded. No unit, distance, or alignment procedure exists anywhere (E4 item 8). **Nothing in era 02 consumes it:** the gate is closed, and the rewrite skill's self-report stays inside `output`. It is deferred to the era that opens `gate:`, which is where 04 put `max_change_rate`. `ko.preserve`, its necessary input, is built now.

### 15.6 What the runner must report with every result

The `exclusion_version` and measurement code version. The arm and stratum counts. The number of records excluded by any floor, and why. For a Tier 1 measurement, the analyser version.

### 15.7 `watch:` candidates

```yaml
# assemble/profiles/<profile>.yaml — era 02 writes candidates only
watch:
  <measurement>: {max: float} | {min: float} | {min: float, max: float}
  _meta: {source: "corpus <batch id>", arm: C, exclusion_version: "…", status: candidate}
```

A candidate is written only for a measurement that has (1) an observed false-positive rate on correct Korean, and (2) a non-zero **B − C difference** on the corpus (§18). Nothing reads `watch:` at runtime in era 02. Promotion to `gate:` is era 03, under 05a's three conditions.

**Basis:** 04 §6; 05a; E2 (tiers, recipes, exclusion pass, layers, usable, reply length); E3 (reference scope); E4 items 3–5, 8; kiwipiepy licence (PyPI metadata, 2026-09-16).

## 16. Judges

**No `llm` grader produces a recorded value in era 02** (E3). This section fixes the procedure, so that the era that wants a judge does not have to invent one.

### 16.1 The bar

A judge between the true difference and the reported one scales it by `Se + Sp − 1`. The effect this toolkit chases is small, so **each error direction's 95% upper bound must be below 10%**. That keeps at least 80% of the difference. Intervals are Wilson, and the method is always stated.

**The formula assumes the error rate is the same in both arms.** The arms differ by design (policy-on text is more polished), so error rates are measured **per arm**. A differential error can manufacture a difference, and no pooled bound rules that out.

### 16.2 Procedure

| Tier | Question | Reference | n | Outcome |
|---|---|---|---|---|
| **A: disqualify** | Does the judge contradict a deterministic clause of its own rubric? | the rubric | from 1 | a unanimous contradiction disqualifies; a split one triggers a rerun |
| **B: screen** | Does it agree with a reference measurement? | the four below, on a **constructed, label-balanced** set | 60–70 replies per direction, per arm (2 errors need n ≥ 69) | every upper bound < 10% |
| **C: qualify** | Does it agree with a person, on rules with no mechanical reference? | human labels | budget-bound | the only licence for `llm`-class rules |

**Reference measurements** (a disagreement must be the judge's fault): `honorific_address`, `spelling_denylist`, `quote_balance` (once the exclusion pass is validated), and `allomorph_errors` (with §15.4's scope). Not `em_dash_count` and not `speech_level`.

**The unit of n** is one graded reply with known ground truth, for one rule, in one direction. **Cost:** about $0.117 per generate-and-judge sample, so about $15 per rule for both directions on a constructed set. Double that for per-arm error rates.

### 16.3 What era 02 runs

- **Tier A with a stronger judge model** (`claude plugin eval --judge-model`, above the Haiku default) on the two policy cases C3 used. It costs almost nothing, and it is the experiment C3 never ran. Because a case cannot select a style (§17.2), it runs on a **scratch copy with the style forced**. The experiment is about the judge, not about the shipped layout. The verdict is recorded against the (judge model, rubric wording, tool version) triple and not generalised.
- **Every judge run record keeps** the judged text, the verdict, the judge's stated reason, and the judge model (E3). Without these the run validates nothing. That is why C3's most-quoted claim cannot be reproduced.
- Any `llm` verdict produced is an **annotation no threshold reads**, tagged so it can be discarded wholesale.

**Basis:** E3 (`04_judge.md`); review §C3; 05a.

## 17. Eval and the two runners

### 17.1 Two runners, because one cannot do both jobs

| Runner | Job | Graders | Arms |
|---|---|---|---|
| `claude plugin eval` | **triggers and skill regressions**: does the skill fire, does the plugin load | `tool_used`; `regex` with `arm: both` under `--ablation with-without` | A vs B only: plugin off vs on, and **no style can be selected** (§17.2) |
| `measure/` (ours) | **measurement and policy regression**: ratios, Tier 1, Tier 2, three arms | §15 | A, B, C |

A regex-expressible rule **whose subject is a skill or an agent** runs through the tool's ablation and is **not** duplicated offline. A main-thread policy rule cannot, even when it is a regex (§17.2). A ratio cannot be expressed in the tool, and neither can a morpheme or a pair.

### 17.2 Changes to the existing suite (`tests/evals/claude-code/`)

**Measured: a case cannot select an output style** ([`eval-style-selection.json`](../../../tests/runs/02-spec/eval-style-selection.json)). The frontmatter has no settings key. `env` accepts only `EVAL_*` keys. Runs use a temporary home, and plugin `settings.json` cannot set a style. So under B9 the tool's plugin-on arm is **arm B**: installed, no style.

- **The two policy cases leave the tool, and this reverses one E5 handoff.** E5 kept the em dash as an in-tool `regex` grader, because a false positive that fires in both arms cancels in the delta. That reasoning still holds, but under B9 the tool's two arms are A and B, and **neither arm applies the main-thread style**. An em-dash delta between them would measure nothing about the policy. So the em-dash and `사용자님` checks move to `measure/`, as arm B-vs-C comparisons (§18), where the sentence-ending half (`noun_ending_ratio`) already had to go. Their `llm` graders are retired, not kept as annotations: they would grade replies with no policy applied.
- **The tool keeps the four trigger cases** (`tool_used`) under `--ablation with-without`. Its A-vs-B delta is exactly the skills' contribution, which is what a trigger case tests.
- A future regression grader that belongs in the tool must be one whose subject is a skill or an agent, not the main-thread policy.
- Judge model ≠ generating model, and human labels on a subset (04 §13.3, carried).

### 17.3 Case format for `measure/`

`tests/cases/*.yaml` stays a human checklist and is not converted (nothing parses it). New cases, under `tests/measure-cases/`:

```yaml
id: string
profile: agent-reply | formal-report
arm: A | B | C | any
layer: policy | skill | agent
input: string              # or task: string; paste-in cases carry the original in input
expect:
  <measurement>: {max: float} | {min: float} | {min: float, max: float} | {equals: value}
  preserve: [number_unit_date | quote | code_url_path | proper_noun | register]   # passes at zero violations
```

Dropped from 04 §13.1: `gate_pass` and `max_change_rate` (no gate, no procedure), and `trigger` (the tool's job). **A field nothing reads is not kept.** That is how `tests/cases`' `expect` became decorative.

### 17.4 `ruleset`: deferred, with the blocker cleared

`JangHyun-bin/korean-report-skills` is **Apache-2.0 with a NOTICE file** (checked 2026-09-16, HEAD `05ce76d`). It is not MIT, unlike the four locked upstreams, so adopting it means carrying its NOTICE and marking changes, which is compatible. **Adoption stays deferred** (E5). Revisit it once the exclusion pass and Tier 0 exist and the remaining battery's implementation cost is known. The comparison then is 115 implemented substitution rules against the rules not yet written.

**Basis:** E5 (`06_ruleset_and_eval.md`); E3; 02-E5 validator record; GitHub API (licence).

## 18. The corpus

Era 02's material is **real records with a synthetic prompt distribution** (E1). Era 03 swaps the distribution, not the schema, the code, or the graders.

### 18.1 Arms

| Arm | Plugin | Style selected | Isolates |
|---|---|---|---|
| A | not installed | — | floor |
| B | installed | **none** | skills and agents without the main-thread policy (B9 makes this constructible) |
| C | installed | `ko-quality:<profile>` | everything |

**B − C is the policy's own effect** on the main thread. A − B is the skills' and agents' effect. The gate is off in every arm, and the gate dimension (`policy × gate`, E6) belongs to the era that opens `gate:`.

Sub-agent records are the same in B and C (S1-A), so **the agent layer is compared A against B/C**, not B against C.

### 18.2 The generator

- **Plain headless `claude -p`**, through the **shipped logger**, with `KO_QUALITY_HOME` pointed at a corpus home outside `~/.ko-quality` and outside the tree.
- **`--output-format json`, or `stream-json` for multi-turn.** From the result it writes the annotation record (§12.2): the arm, the profile, the model, actual token usage with thinking subtracted, and `subagent_stats`.
- **Profiles alternate within one session** with `/output-style` over `--input-format stream-json` (02-E1). One process yields both profiles' turns, which halves the corpus. The first turn after a switch is annotated as such.
- **The style selection is written to the corpus project's `settings.local.json`** and reset between sessions, so no arm inherits another's selection (§2.1: the selection persists per project).
- **An arm is verified, not assumed.** Each batch carries a canary run per arm, a copy of the plugin with a marker line, and the batch is rejected if a marker appears in the wrong arm. This is the device P3 and 02-E1 used.
- `claude plugin eval` is not the generator (E1).

### 18.3 The prompt set

Written by us, with coverage stated and gaps admitted (02_scope).

| Stratum | Why it must be there |
|---|---|
| conversation: short Korean questions | ordinary replies; the `usable` floor and reply-length effects |
| coding reply: explain or review code, no edits | `coding.06`/`coding.07` pressure; Latin identifiers in Korean prose |
| coding with edits | `task_type: coding`; artifacts outside the reply |
| document: write Korean prose to a `.md` file | `task_type: document`; the reply-only measurement limit |
| **paste-in rewrite** | Tier 2 exists only here |
| delegation to a shipped agent | agent layer; `coding.19`; the hand-back capture (§11.2) |
| **deliberately correct Korean**, and **deliberately defective Korean** | false-positive rates for every measurement (§15.1) |
| English prompts | `instruction_lang` covariate; the policy must not force translation (`coding.06`) |

**What the set does not cover** is recorded with each batch, and a stratum missing from the set is a measurement that cannot fire.

### 18.4 Batches

1. **Pilot:** a few prompts per stratum, all three arms, both profiles. Its purpose is to measure the exclusion pass, false-positive rates, the hand-back rate, and each measurement's variance, **not** to estimate the effect.
2. **Size from the pilot.** The number of sessions per arm is computed from the pilot's observed variance for the measurements that have `watch:` candidates. It is not fixed in this spec, because no variance has been observed yet.
3. Every batch has an id. Records, annotations and derived values carry it, and batches are never pooled across different plugin `build_id`s.

**Cost reference:** about $0.12 per headless run (C3, E1).

**Basis:** E1 (`02_scope.md`); 02-E1; E2 (arms, layers); E4 (generator-supplied fields); E6 (gate dimension); S1.

## 19. Gate semantics (designed, not opened)

`gate:` is not opened in era 02. This section is here so that the era that opens it inherits decisions, not guesses. Nothing below is built now, except that `gate/` is reserved and the record reserves its fields.

### 19.1 Where a gate can live

| Site | Enforces | Status |
|---|---|---|
| **`Stop` hook, as its own executable** | the reply | **Works, measured** with `--plugin-dir` (E6). Unmeasured under a marketplace install |
| `PreToolUse(Write)` | a file write | Asserted, not probed. Its deny is `hookSpecificOutput.permissionDecision`, not `Stop`'s top-level `decision` |
| MCP tool | nothing | A tool the model must choose to call is advice. None ships (§10) |
| The logger | — | **Forbidden.** Wiring a gate into it would be one `print` statement. That is why the gate must be a separate file |

### 19.2 What a firing gate does

- `on_final_fail: block | emit_with_flag` survives from 04. `block` is implementable on replies.
- **The harness imposes a third behaviour.** After 8 consecutive blocks (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) the turn ends with an **empty result**. A gate therefore keeps its own retry counter, using `stop_hook_active`, and chooses `emit_with_flag` before the harness chooses for it.
- **Blocking leaks, whether or not it explains.** A diagnostic `reason` teaches the model the metric (05a leak gate 3). A blank or absent `reason` still tells it that it was rejected, and it said so to the user in 2 of 3 measured modes. `systemMessage` is documented as user-only and unprobed.
- **A gate that keeps firing becomes visible.** By the fourth retry, the model was explaining the hook to the user (E6).

### 19.3 How gated records are read

- **Four arms, not two modes:** `policy {off, on} × gate {off, on}`. `policy on, gate off` is era 02's question. `policy on, gate on` is the product's delivered quality. They never share an arm.
- **In a gated arm, the measurement the gate fired on is not read**, because it is tautological. **The measurements it did not watch are read**, because a forced correction displaces defects there (upstream's own `삭제 과교정 금지`, D-9, D-10).
- Records carry `gate_on`, `gate_fired`, `gate_retries`, and `gate_fired_on` (reserved in §12.1). Gated and ungated records are never pooled.

**Basis:** 04 §4.4, §8; 05a; E6 (`07_gate.md`, `02-E6` record).

## 20. Log text: use and retention

A record holds the user's prompt and the reply **verbatim**, masked only for the patterns in §12.1. Era 02's corpus is synthetic, but era 02 builds the storage that era 03's real text will land in. These rules bind from the first real record, including this repository's own sessions (§21).

| Rule | Detail |
|---|---|
| **Real text is never committed** | Not as a record, an eval case, a fixture, or a quote in a design document. Cases are written, not harvested. If a real record motivates a case, the case is rewritten to show the same defect |
| **Every copy stays under `KO_QUALITY_HOME`** | Judge and grader copies, derived records, and exports included. One place to delete |
| **No real text goes to an `llm` grader in era 02** | Sending real text to a model provider for grading is a decision era 03 makes with the user, and records |
| **Text expires after 90 days** (E7-b, user) | `task` and `output` in `logs/`, and every copy of them. Deletion is by **whole monthly file**, once the file's last day is more than 90 days old, so text lives 90–~120 days. Derived values do not expire, which is why they live in `derived/` and never only in `logs/` (§11.4) |
| **Retention is enforced by a program, not a habit** | The measurement runner (or a sibling command) deletes expired monthly files, and reports what it deleted, at the start of every run. **Deletion is automatic and irreversible, accepted** (user, 2026-09-17) |
| **Masking is best-effort and labelled so** | `masked: false` means none of the patterns matched, not that the text is clean. Names are never masked |

**Basis:** E7-b; AGENTS.md (public repository); 06 §11.4.

## 21. Self-application

**Decided with the user, 2026-09-16: this repository runs the toolkit on itself, with `agent-reply`, as the repository default.** The purpose is to observe `coding.06` (the policy does not ask for translation) and `coding.07` (code-adjacent text follows the project's convention) under real pressure: an English codebase with Korean conversation.

### 21.1 What makes it safe to switch on

**Everything below is in place before the default is switched on.** Where in the build that happens is `4-plan`'s decision (§22.2).

| Requirement | Mechanism | Evidence |
|---|---|---|
| Records never reach the real home | Committed `.claude/settings.json` sets `env.KO_QUALITY_HOME: "~/.ko-quality-dev"`, and the logger expands `~` (§11.4) | settings `env` reaches plugin hooks, literally (§2.1) |
| A leak is detectable afterwards | `project` in every record: a hash of the git root above `cwd` (§12.1) | Settings are read only from the launch directory. A session started in a subdirectory gets **no** isolation and **no** plugin, and only the marker catches it |
| Records from different builds are not mixed | `build_id` in the stamp (§13) | The plugin under test is the plugin being built |
| Development agents do not confuse delegation | Build check 5 (§13) | Agents coexist by name (§2.1) |

### 21.2 What can be committed, and what each machine does once

| Setting | Committed `.claude/settings.json` | Per machine, once |
|---|---|---|
| `KO_QUALITY_HOME` | yes | — |
| `enabledPlugins: {"ko-quality@<marketplace>": true}` | yes (`--scope project` writes it there) | — |
| The marketplace | **no**: it is recorded in user settings with an absolute path, and a relative path in project settings was not loaded headlessly | `claude plugin marketplace add <repo>/dist/claude-code` |
| `outputStyle: "ko-quality:agent-reply"` | yes, as the default | **Remove any local `outputStyle`** (this repository's `settings.local.json` holds `Concise`), because a local selection beats the committed one |

The per-machine steps go in the repository's Korean `README.md`. **Whether a `github` marketplace source removes the marketplace step is `4-plan`'s question** (§14.2).

### 21.3 What it costs, accepted

- `Concise`, the style this repository was developed under, is given up.
- Every development session writes real text. §20 applies in full, including the 90 days.
- **05a's third leak gate, one level up:** the developer knows what is measured and writes the sessions being recorded. That is acceptable only because **records from this repository never enter a sample.** They are excluded by `project`, and by location as a second guard.
- The toolkit's own design documents are written under the policy they describe, in English. If `coding.06` fails, it fails visibly here first. That is the point.

**Basis:** E7-d; E7 review ([`committed-settings-and-agent-names.json`](../../../tests/runs/02-E7/committed-settings-and-agent-names.json)); [`settings-env-isolation.json`](../../../tests/runs/02-E7/settings-env-isolation.json); B9.

## 22. Decision status

**Updated through 5-preflight. Frozen at 6-build** (design README).

### 22.1 Decided

| Decision | Where | Source |
|---|---|---|
| One unforced Claude Code plugin carrying both profiles (B9) | §9, §13 | user 2026-09-16 |
| Agents always carry the agent-reply policy (S1) | §8 | user 2026-09-16 |
| Exclusion-dependent fields are derived offline, not in the hook (S2) | §11.1, §12.3 | user 2026-09-16 |
| `kiwipiepy` allowed in `measure/` only, with a build check (S3) | §15.3, §13 | user 2026-09-16 |
| stop-slop-ko not in era 02; `exempt` removed | §1, §6 | E7-a, user |
| 90-day text retention, by monthly file, deleted automatically by the runner | §20 | E7-b, user; automatic deletion user 2026-09-17 |
| Self-application as repository default, behind isolation | §21 | E7-d, user |
| Codex agents need `multi_agent_v2`, no `--ephemeral`; A1 lifted for that configuration | §2.2, §8 | era 99 R1, user |
| ko-rewrite redirect placed under upstream step 1 | §7 | era 99 R3 |
| `register` restated; `policy_on` kept and fixed; `plugin_present` added | §6, §11.3 | E4 |
| No MCP server | §10 | P6, P7, E5, E6 |
| No `llm` grader value recorded in era 02; judge bar and procedure fixed | §16 | E3 |
| Two runners; policy cases leave `claude plugin eval`, including the em-dash regex E5 kept there | §17 | E5; eval-style-selection probe |
| `ruleset` deferred (Apache-2.0 noted) | §17.4 | E5 |
| `ko.change_rate` deferred to the gate era | §15.5 | E4 item 8 |
| Gate: a separate `Stop` executable; four arms; not opened; `gate/` and the four record fields reserved now | §19, §12.1 | E6; reservation user 2026-09-17 |

### 22.2 Open

| Decision | Leaning | Settled in |
|---|---|---|
| Directory names `measure/`, `corpus/`, `gate/` | as written | 4-plan |
| Per-call scan cap for `tool_output_chars` | — | 4-plan (§11.2) |
| Extractor reads the rewrite taxonomy directly (61 → 85 patterns) | — | 4-plan (§14.2) |
| Sessions per arm | from pilot variance | 6-build, after the pilot (§18.4) |
| `github` marketplace source for self-application | — | 4-plan (§21.2) |
| Build step at which self-application is switched on | right after the step that builds the logger's isolation (`~` expansion, `project`) and `build_id` | 4-plan (§21.1) |
| Whether subagent reports always use hand-back on Claude Code | count in pilot | 6-build (§14.2) |
| Effective output style observable live on Claude Code | — | **era 03 blocker** (§11.3) |
| Codex `task_type` third value | — | when a Codex arm is added: not in era 02, whose corpus is `claude -p` only (§18.2); no era is assigned yet |
| `ruleset` adoption | revisit once the exclusion pass and Tier 0 exist (§17.4) | 6-build record → review |

## 23. Map from 06

| 06 | 09 |
|---|---|
| §1 purpose | §1 (validation added; "installed **and selected**") |
| §2 facts | §2 (measured vs documented; Codex corrected by era 99) |
| §3 layers | §3 (MCP layer removed) |
| §4 directories | §4 (`measure/`, `corpus/`, `gate/`; `server/` removed) |
| §5 supply | §5 (`reference` role, anchor forms B8) |
| §6 profiles, presets | §6 (`register` restated, `exempt` removed) |
| §7 skills | §7 (B1, B2, redirect placement) |
| §8 agents | §8 (S1) |
| §9 policy injection | §9 (decision ③ as built, B9) |
| §10 MCP | §10 (none) |
| §11 hooks, logger | §11 (what a hook can establish) |
| §11.3 record | §12 (record, annotation, derived) |
| §12 build | §13 (one plugin, `build_id`, checks 5–6, removal) |
| §13 approximations | §14 |
| §14 prototype plan | **not carried**: planning is `4-plan`'s document from this era on |
| §15 road to validation | §15–§19 |
| §16 decision status | §22 |
| — | §20 log text, §21 self-application |
