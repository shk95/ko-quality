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
> **Status: draft, written in four bundles and reviewed with the user bundle by bundle.**
> - **Bundle 1** (§1–§10, §13): supply and distribution. **Written.**
> - **Bundle 2** (§11–§12, §14): hooks, logger, and the record.
> - **Bundle 3** (§15–§18): measurement, judge, eval, and corpus.
> - **Bundle 4** (§19–§23): gate semantics, log data, self-application, decision status, and the section map.

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
| Hook payloads carry `session_id` and `cwd`. `Stop`/`SubagentStop` carry `last_assistant_message`. **`model` is absent from headless `SessionStart`**. No hook payload carries token usage, except the `Agent` tool's `PostToolUse` | P7; 02-E4; 02-E6 |
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
| `ruleset` | deterministic rules | **open** (§17) | candidate `JangHyun-bin/korean-report-skills`, licence unchecked |

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

Unchanged in shape. Four upstreams, all MIT, checked 2026-09-14. **Adding a provider requires a licence check before extraction.** This is the unconditional blocker for `ruleset` (§17).

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

**Behaviour check.** Checks 1–5 see only the build. Whether it takes effect is `claude plugin eval`'s job, for triggers and regressions (§17).

**Removal (B6).** Claude Code: `claude plugin uninstall`, then remove the marketplace. Two traces remain and are documented: an empty `extraKnownMarketplaces` and an orphaned cache under `~/.claude/plugins/cache/<marketplace>/`. **Also remove the style selection** from each project's `settings.local.json`, or the next session asks for a style that no longer exists. That line is new under B9 and not yet measured. Codex: the installer's `uninstall` restores `AGENTS.md` byte for byte (P6).

**Basis:** 06 §12; B4, B6; B9; P5, P6, P7; E7-c, E7-d.
