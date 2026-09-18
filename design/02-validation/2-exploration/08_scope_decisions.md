# 08. E7 — scope decisions

> Stage document. `2-exploration`, agenda item E7 (see [`02_scope.md`](02_scope.md)).
> Sources: 06 §6 and §16.2; concept open questions 5–6 ([`../1-concept/01_idea.md`](../1-concept/01_idea.md)); stop-slop-ko at commit `43313c9` (2026-07-30); `logger/ko_quality_log.py`; two run records, [`agent-scope-and-visibility.json`](../../../tests/runs/02-E7/agent-scope-and-visibility.json) (made before this document) and [`settings-env-isolation.json`](../../../tests/runs/02-E7/settings-env-isolation.json).
>
> Each section ends with a disposition. E7-a, the retention period in E7-b, and E7-d were decided with the user on 2026-09-16. Where the user chose differently from the proposal, both are recorded.

E7 has four items. Two are about what enters the toolkit, and two are about where this repository stands relative to it.

| # | Item | Short answer |
|---|---|---|
| E7-a | stop-slop-ko as a `policy` fragment provider, with `exempt` restored | **Not in era 02.** `exempt` has nothing to restore and is removed |
| E7-b | What log text may be used for evaluation, and for how long | Era 02 does not touch real text. The rules are written now, because era 02 builds the storage. **Text expires after 90 days** |
| E7-c | Where agent definitions live | Settled by measurement, plus one naming rule |
| E7-d | Whether this repository runs the toolkit on itself | **Yes, as the repository default.** That makes isolation mandatory, and the isolation that works today is only per machine |

## E7-a. stop-slop-ko, and why `exempt` cannot be restored

### What the upstream is

The upstream was read at HEAD rather than recalled from 01a.

| | |
|---|---|
| Repository | `limleesol/stop-slop-ko`, commit `43313c9619d1152b110c19bf1ef9ef7341eff3b8` (2026-07-30) |
| License | MIT (root `LICENSE`) |
| Shape | One skill. `SKILL.md` is 30.8 KB, about five times the entire rendered policy (6.3 KB). It has a correction mode, a generation mode, a pre-output checklist, and an appendix on correctness |
| Evidence | `evals/benchmark/RESULTS.md` (0.11.0): 10 new cases. Mechanical assertions scored with 69/69 against without 65/69, and a blind A/B judge split 5:5 |

**Where its measured value is.** The four assertion failures in the without condition come down to three patterns: **the 양비론 skeleton** ("물론 ~하지만"), **appeal to unnamed authority** ("전문가들은"), and **inventing a figure the input did not contain** (the fourth failure was an assertion design error that upstream withdrew). Upstream draws the same conclusion: the skill's value is not a general lift but blocking these residual failures.

**None of the three is in the current policy.** A search of both rendered output styles for 양비, 권위, 출처, 지어, 수치, 균형, 물론 finds nothing. The correction taxonomies come close in four places. im-not-ai has I-7 (무주체 판정), a "날조 금지" note on D-11's fix, and **G-3**, a balance lexicon ("양쪽 모두/장점도 있지만/균형" 4회+) that upstream itself marks **실증 부족 — hold** (03_features §G-3). yoonmoon's diagnose taxonomy has **균형 강박** ("장점과 단점이 모두 존재한다 / 한편으로는~다른 한편으로는"). All four belong to the `ko-rewrite`/`ko-diagnose` correction procedures, not to generation-time policy. So a fragment would add something the main thread does not currently receive. That is a testable hypothesis, not a duplicate.

**Its losses are also measured.** Two of the with condition's five blind losses were overcorrection: an em dash deleted inside the threshold, and a scope sentence deleted. Upstream's own discussion of the em dash rule is the same "fixing one pattern manufactures another" point that E6 took from im-not-ai.

### `exempt` referred to identifiers that never existed

06a ③ emptied `exempt` because `[slop.cta_in_sns, slop.polite_email_ending]` pointed at a provider that was not in the list. The implied remedy, "adopt the provider and the references resolve", does not work.

- **stop-slop-ko has no rule identifiers.** Its rules are numbered headings and prose. `slop.cta_in_sns` and `slop.polite_email_ending` were first written in 04 §8.1 on `agent-reply`, moved to `formal-report` in 05, and emptied from there by 06a. They belong to no upstream.
- **Its exemptions are already inside its rules**, and they are conditional on register. "면제: 마케팅 카피·SNS 레지스터의 행동 유도 문구 … 는 정상이다" sits under 독자 참여 요청. "면제: 이메일·공지의 정중한 어미는 유지한다" sits under 과잉 경어 구조. The model applies them per block at run time ("판정 단위는 블록이다"). A profile-level key would duplicate a decision that upstream makes, and makes better, because it sees the block.
- **Neither profile has those registers.** `agent-reply` covers coding replies and `formal-report` covers 하십시오체 reports. An exemption for SNS calls to action or email endings would never apply to either.
- **The three sections worth taking carry no exemptions at all.** 양비론 and 막연한 권위 have none, and the no-fabrication rule is declared global ("모든 규칙보다 우선").

So `exempt` is not waiting on a decision. It is a key with no referent under any decision.

### The fragment's shape under 06's rules

- 06 §5.3 makes upstream's distribution unit the normalization unit. For stop-slop-ko that unit is one `SKILL.md`, so the whole file is normalized, with anchors on its headings.
- The profile then selects three blocks: 철칙 2 (no fabrication), 양비론·균형 반사, and 막연한 권위 호소. Selection is structure, which is ours. No sentence changes, so `adapted` stays at 0.
- The generation-mode bullets are a fourth candidate. They restate the other rules in imperative form, so including them doubles the text without adding a pattern.
- **철칙 2 is not a heading.** It is the second numbered item under `## 철칙: 지우되 만들지 마라`, which also holds 정보 보존, 삭제 시험 and 규칙 적용 범위. Heading-level anchors cannot select it alone, so either the anchor format gains a list-item level or the whole 철칙 block comes along.
- The rendered policy is 6.3 KB today. The three blocks are 1.8 KB with 철칙 2 cut at item level, and 2.9 KB with the whole 철칙 block. That is 28–45% more system-prompt text on every turn. E4 settled `tokens.output` only, so this input-side cost is not priced by anything yet.

### Disposition

**Proposed:** add stop-slop-ko to the lock with role `policy`, and measure it as one more corpus arm (C against C+slop).

**Decided with the user, 2026-09-16: stop-slop-ko does not enter era 02.** No lock entry, no normalization, no corpus arm. The corpus stays at arms A/B/C, and era 02's instrument is built and validated without a second policy provider varying under it. The facts above stay on record for whichever era picks the question up. The shape analysis still applies then: normalize the whole file, select three blocks, `adapted` 0.

What still follows in era 02:

1. **Drop `exempt` from the profile schema** (06 §6) rather than keep an empty key. Emptying it waited on this decision. It is now known that no decision gives the key a referent. This is a 06 §6 revision candidate alongside B9. If a register exemption is ever needed, the reason will be a measured false positive, and its form should come from that case.
2. **Side input for E5, reading only:** `evals/benchmark/check.py` and `cases.json` use `must_absent`/`must_present` regexes, a length floor, and an allow-list of numbers for fabrication. That is a worked example for E5's **offline measurement runner**, from the only upstream that measured itself. It is not a template for `claude plugin eval`: there, `must_absent` exists only as a negative lookahead, and a length floor or a number allow-list cannot be expressed at all (E5 §3). Reading it creates no dependency and needs no lock entry.
3. **Parked for era 03 or later:** stop-slop-ko as a measured arm. When it is picked up, the measurement plan was: E2's list does not name 양비론 or unnamed authority. Both fit its `phrase_battery` measurement as new phrase entries, which is how upstream's own `check.py` asserts them. Invented figures are already covered by the input+output tier: `number_unit_date_preservation` diffs the numbers in the output against those in the input. The arm costs about $0.12 per run (E1).

**What this leaves unanswered.** The question stays open, as it has been since 01a: does the policy lack something stop-slop-ko measured as missing? Nothing in era 02 tests it. The current policy contains none of the three patterns, so a measured gap exists on record without being tested.

**A cheaper path for whoever picks it up.** For 양비론, the question is not only "add a second provider". im-not-ai already names the pattern (G-3) and holds it for lack of evidence, and stop-slop-ko's benchmark is exactly that evidence: one of its residual failures. G-3 is already a `phrase_battery` row in E2, so era 02's instrument will count it on arms A/B/C anyway. Its **on/off difference** is the measurement that could lift the hold, without a lock entry.

## E7-b. What log text may be used, and for how long

### What a record holds

Each record carries **`task`, the user's prompt verbatim, and `output`, the reply verbatim.** Both go through `mask()`, which has five patterns: `sk-` keys, `api_key`/`token`/`secret`/`password` assignments, GitHub tokens, AWS access key IDs, and email addresses.

**Things the mask does not catch:** phone numbers, 주민등록번호, card numbers, personal names, and absolute paths, which contain the account name. `masked: false` therefore means "none of five patterns matched", not "clean".

### Why this binds era 02 even though era 02's text is synthetic

Era 02's corpus is prompts we wrote, so no personal text exists yet. But era 02 builds the parts that will hold personal text in era 03:

- E3 requires **the judged text, the verdict's reason, and the judge model** to be stored together. That is a second copy of the text, outside the log file.
- An `llm` grader **sends the text to a model provider.** Whatever a session already sent, a grader sends again, later, for a different purpose.
- Eval cases (E5) live in `tests/`, which is committed to a **public** repository.

Era 03 would inherit whatever these do by default.

### Disposition

| Rule | Why |
|---|---|
| **No text from a real record is ever committed**, including as an eval case, a fixture, or a quote in a design document. Cases are written, not harvested. If a real record motivates a case, the case is rewritten to the same defect | AGENTS.md already forbids personal data in committed files. Cases are where the pull toward "just paste the one that failed" is strongest |
| **Grader and judge copies live under the same `KO_QUALITY_HOME` as the records they came from**, never in the tree | One place to delete |
| **Sending real text to an `llm` grader is an era 03 decision**, made with the user and recorded. Era 02's judge runs only on the synthetic corpus | Same provider, but a different purpose from what the user agreed to by starting a session |
| **Retention: text fields expire; derived values do not.** `task` and `output`, and their judge copies, are deleted after a fixed period. `features`, verdicts without text, and counts are kept | Measurement needs the numbers across eras. It needs the text only while a grader or a person is looking at it |
| **Mask coverage is a spec item**: add phone numbers, 주민등록번호, and card numbers, and replace the home directory in paths. Names stay unmasked, and 06 §11.4 says so | Cheap regexes. The false negatives are the ones that matter |

**Retention: 90 days, decided with the user, 2026-09-16.** The limit applies to `task`, `output`, and every judge or grader copy of them. The records are monthly files (`<yyyy-mm>.jsonl`), so the deletion unit is a whole month: a file is removed once its last day is more than 90 days old. That keeps text for up to about four months, never less than 90 days. Deleting records inside a file would mean rewriting an append-only log, which costs more than the few extra weeks. Removal cannot throw away the derived values, so derived values have to be written somewhere other than the monthly file before it expires. That is a storage-layout constraint for the spec.

The 90 days count from when the record was written, not from when era 03 opens. A record written today would expire before era 03 reads it. This does not affect era 02, whose corpus is synthetic and not subject to this rule.

## E7-c. Where agent definitions live

The facts are in [`02_scope.md`](02_scope.md) and the first E7 run record. Plugin agents are namespaced by `plugin.json`'s `name`, and `--scope local` limits visibility. **One of them is corrected here:** "project agents outrank plugin agents" does not hold.

### Coexistence, not precedence (measured in review, [`committed-settings-and-agent-names.json`](../../../tests/runs/02-E7/committed-settings-and-agent-names.json))

The first run showed that delegation to `korean-writer` reached the project definition. That was read as the project agent shadowing the plugin's. A second run separated the two readings:

- Both are available at once. The session listed `korean-writer` **and** `<plugin>:korean-writer` as distinct types.
- The bare name ran the project agent, and the namespaced name ran the plugin agent. Nothing was shadowed. The first run asked for the bare name, and the bare name belongs only to the project agent.
- **`SubagentStop`'s `agent_type` is exactly the name invoked**: `korean-writer` or `<plugin>:korean-writer`. The two are distinguishable in the payload.

So the mislabelled record in the first run (`injection_point: agent-definition` for a project agent with no policy) is **the logger's fault, not the harness's.** It derives the field from the build stamp's presence and ignores the `agent_type` it already records. A policy-carrying plugin agent is recognisable by its namespace prefix.

### Disposition

- **Shipped agents stay in the plugin.** Development agents, if any, go in this repository's `.claude/agents/`, committed.
- **The logger derives `injection_point` for sub-agent records from `agent_type`**: `agent-definition` only when the name carries the plugin's namespace, `none` otherwise. This joins E4's `policy_on`/`injection_point` fix.
- **Development agent names still should not reuse shipped names**, but as a readability rule, not a correctness one. A bare `korean-writer` next to `ko-quality:korean-writer` invites the model to pick the wrong one when a prompt says "the Korean writer". The build check stays cheap: fail if `.claude/agents/*.md` has a `name` that is in `assemble/agents/`.
- **Whether to write development agents at all** is not an exploration question. The frontmatter supports `model` and `effort`, so AGENTS.md's tier table could live in the files. That is a convenience for `4-plan`, not a scope decision.

## E7-d. Self-application

### The isolation 02_scope proposed works, measured

`02_scope.md` proposed allowing self-application with `KO_QUALITY_HOME` pointed elsewhere. Two runs tested whether a project can do that for itself ([`settings-env-isolation.json`](../../../tests/runs/02-E7/settings-env-isolation.json)):

- `env.KO_QUALITY_HOME` in a project's `.claude/settings.local.json` **reaches plugin hooks**. The shipped logger, loaded as a plugin, wrote its record into the redirected home, and `~/.ko-quality` was never created.

### But not in a form this repository can commit

| Where the setting goes | Problem |
|---|---|
| `.claude/settings.local.json` | Gitignored. Per machine. A fresh clone writes to the real home |
| `.claude/settings.json` (committed) | Reaches plugin hooks the same way (measured in review). But the value is passed **literally**: neither `~` nor `$HOME` is expanded by Claude Code, and the logger does not expand them either. An absolute path is machine-specific, which AGENTS.md forbids |

And when isolation is missing, **nothing in the record shows it.** The record has no project field. The `Stop` payload carries `cwd`, but the logger drops it. So the exclusion rule 02_scope proposed for era 03's sample definition ("records originating in this repository are excluded") **cannot be executed** as the record stands. It depends entirely on the setting having been present.

Two ways to close it, both small:

1. **`expanduser` in the logger**, plus a committed `.claude/settings.json` with `KO_QUALITY_HOME: ~/.ko-quality-dev`. Isolation becomes versioned.
2. **A project marker in the record**, for example a hash of `cwd`'s repository root, not the path itself (E7-b). Exclusion becomes checkable after the fact.

(1) prevents the leak, and (2) detects it. (1) is cheaper, **and (1) alone is not enough.** Project settings are discovered only in the **launch directory**. A session started in a subdirectory of the project does not read the project's `.claude/settings.json` or `settings.local.json`, with or without a git root (measured in review). So `cd logger && claude` loses isolation, the plugin enablement, and the style, silently. The `Stop` payload's `cwd` is that subdirectory. A marker computed from the git root of `cwd` still identifies the repository. A marker computed from `cwd` itself does not.

### The cost 02_scope did not list: the output style

This repository's `.claude/settings.local.json` currently selects the `Concise` output style. Measured in review:

- **Forced plugin style** (the current build): it applies even though `settings.local.json` says `Concise`. Installing the plugin replaces `Concise`.
- **Unforced (B9), selected in committed `settings.json`**: **`settings.local.json`'s `Concise` wins.** A committed style selection is a default that any local selection overrides.

Self-application is therefore not "add the toolkit". It means **giving up the style this repository is actually developed under**. Under B9 it also means removing the local selection on every machine, because the committed one does not override it.

### Which profile

`agent-reply` is the only candidate. `formal-report` would put every development reply in 하십시오체 addressed to 사용자님. That breaks AGENTS.md's language rule and is not a register anyone works in. `agent-reply`'s `coding.06` (the policy is not an instruction to translate) and `coding.07` (code-adjacent text follows the project's convention) are exactly what a repository whose code is in English and whose conversation is in Korean would put under pressure. That is 02_scope's reason to allow this at all.

### Disposition

**Proposed:** self-application with `agent-reply` only, opt-in per session, because of the output style cost.

**Decided with the user, 2026-09-16: `agent-reply` is the repository default.** Every development session in this repository runs under the toolkit, and `Concise` is given up. The volume of observation under `coding.06`/`coding.07` pressure is the point, and an opt-in that is rarely chosen would produce little.

A default raises the stakes on the items above, because what was an occasional leak becomes every session:

- **Isolation is a precondition, not a recommendation.** Every session in this repository writes records. So option (1), `expanduser` plus a committed `.claude/settings.json` that sets `KO_QUALITY_HOME`, has to be in place **before** the default is switched on, not alongside it. Option (2), the project marker, moves from candidate to spec item. With every session logging, a single unisolated machine would put a large block of meta-sessions into the real home, and without (2) nothing could separate them afterwards.
- **"Repository default" can only be partly committed.** Measured in review:
  - `claude plugin install --scope project` writes `enabledPlugins` to the **committed** `.claude/settings.json`. That part travels with a clone.
  - **The marketplace does not.** `plugin marketplace add` records it in the user's `~/.claude/settings.json` with an absolute path. A `directory` marketplace declared in the committed file with a relative path was accepted but **not loaded** in headless runs, in place or in a copy. The run does not separate "relative paths unsupported" from "headless mode does not trust the workspace". Interactive trust was not tested.
  - The style selection in the committed file loses to any local one (above).
  So each machine needs one setup step: add the marketplace, and remove a local style selection. That step goes in the repository's README, and its absence is the failure (2) exists to detect. Whether a `github` marketplace source avoids the step is `4-plan`'s question.
- **A session started below the root is not self-applied at all**, and it is not isolated either (above). It is the same failure, and (2) catches it the same way.
- **These records are real text.** They are this repository's conversations, not synthetic prompts. E7-b's rules apply to them in full, including the 90 days, even though they live in a separate home and never enter a sample.
- **The plugin under test is the plugin being built.** Rebuilding `dist/` changes what the development sessions run under. The build stamp already records `upstream_versions`, but not which build of our own assembly produced the session. Records across builds would silently mix. This is a stamp field for the spec: a build identifier.
- **05a's third leak gate, one level up, is accepted.** A developer who knows the measurements writes the sessions being recorded. That is tolerable only because these records never enter a sample, so exclusion is what makes the default acceptable.
- **Records from this repository never enter era 03's sample**, excluded by location from the first session and by marker once (2) exists.

## Handed to the spec

- **stop-slop-ko stays out of era 02.** No lock entry, no arm. It is parked for era 03 or later, with the measurement plan above (E7-a)
- **`exempt` is removed from 06 §6**, not restored. No decision about stop-slop-ko gives it a referent (E7-a)
- **Log text rules:** real text is never committed, copies stay under `KO_QUALITY_HOME`, no real text goes to an `llm` grader in era 02, `task`/`output` and their copies expire after **90 days** by whole monthly file, derived values are stored outside the files that expire, and the mask gains phone numbers, 주민등록번호, card numbers, and home-directory paths (E7-b)
- **Agent records:** `injection_point` for sub-agent records comes from `agent_type`'s namespace, not from the stamp. Development agents do not reuse shipped names, checked at build time as a readability rule (E7-c)
- **Self-application is the repository default** with `agent-reply` (E7-d). It brings in:
  - logger: `expanduser` on `KO_QUALITY_HOME`, and a **project marker** field (a hash, not the path)
  - a committed `.claude/settings.json` carrying the isolated home, `enabledPlugins`, and the style. It does not carry the marketplace, and it does not override a local style. That leaves a one-time setup step per machine. Settings are read only from the launch directory, so the marker is computed from the git root of `cwd`. A `github` marketplace source is `4-plan`'s question
  - build stamp: a **build identifier**, so records made under different builds of our own assembly are not mixed
  - ordering: isolation is in place before the default is switched on

## Subagent runs

| # | Tier | Purpose | Verdict |
|---|---|---|---|
| E7-v | `mid` (Sonnet 5) | Adversarial check of the decided text against stop-slop-ko, the logger, dist, and earlier stage documents | No claim wrong. Two corrections: the three-block size (철칙 2 is not heading-addressable, 1.8–2.9 KB rather than "about 2 KB"), and a missed match, im-not-ai G-3 held as 실증 부족 plus diagnose 균형 강박, which opens a cheaper route than a new provider. 92.8k tokens |
| E7-v2 | `mid` (Sonnet 5) | Live probes of the claims the author held with low confidence: committed settings, style precedence, agent names, subdirectory launch ([`committed-settings-and-agent-names.json`](../../../tests/runs/02-E7/committed-settings-and-agent-names.json)) | Overturned one claim: project agents coexist with plugin agents rather than shadowing them, and the mislabel is the logger's. Added three facts that change E7-d: the marketplace is not committable as tested, a local style beats a committed one, and settings are read only from the launch directory. Confirmed that env from the committed file reaches hooks and that `~` is not expanded. 105.2k tokens |

The author re-checked the remaining, document-sourced claims against their sources. That fixed the `exempt` history (04 put it on `agent-reply`, and 05 moved it to `formal-report`), the per-turn cost (input-side, which E4 did not price), the reach of `check.py` as an example (the offline runner, not `claude plugin eval`), and the scope of review §D (forced styles only).

**This document used two subagent runs**; the stage's running total is in [`README.md`](README.md).

Two live probes (settings `env` reaching hooks, and the shipped logger honouring it), cost not captured.
