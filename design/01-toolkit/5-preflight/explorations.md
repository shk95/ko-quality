# Preflight explorations — raw material, not decisions

2026-09-14. Six independent mid-tier (Sonnet) subagents were given a question and the sources, never a leaning, and asked for both sides. Their reports are condensed here so that `flow.md` can decide from them. **Nothing below is decided** — the decisions are in `flow.md` §1. E1b and the Codex probe were added in the same session, before `flow.md` was written.

Work stopped here at the user's request: environment set up, exploration and build not started. Next session resumes at `flow.md`.

## Environment checks done

| Check | Result |
|---|---|
| Headless Claude Code with a local plugin | **Works.** `claude -p "…" --plugin-dir <dir> --max-turns 4 --output-format json` invoked a throwaway skill (`ko-ping`) and returned its fixed token. 3 turns, ≈$0.20. This is P1's test harness (Claude Code 2.1.270) |
| Headless Codex with a local plugin | **Run later in preflight — see "Codex probe" below.** Documented before the run: Documented path (from official docs and `codex plugin … --help`, codex-cli 0.154.0): register a local marketplace (`codex plugin marketplace add <dir>` with `.agents/plugins/marketplace.json` — shape below), `codex plugin add <plugin>@<marketplace>`, then `codex exec --json -C <dir> "$skill …"`; hooks need `--dangerously-bypass-hook-trust` for automation. Whether plugins, hooks, AGENTS.md and `.codex/agents/*.toml` load under `exec` the same as interactive is **not documented**. Remove with `codex plugin remove <plugin>@<marketplace>` |

Marketplace shape seen in Codex's bundled marketplace:

```json
{"name": "<marketplace>", "interface": {"displayName": "…"},
 "plugins": [{"name": "<plugin>", "source": {"source": "local", "path": "./plugins/<plugin>"},
              "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "…"}]}
```

## E1 — im-not-ai procedure source for `ko-rewrite` (06 §16.2)

Candidates: A orchestrator `skills/humanize-korean/SKILL.md` (331 lines), B single-call `codex/skills/humanize-korean/SKILL.md` (45), C `agents/humanize-monolith.md` (150).

| | verbatim | selected out | adapted |
|---|---|---|---|
| A | ~15 lines (content anchors, cautions) | ~300 lines of routing, `${SKILL_ROOT}` paths, Agent calls, scripts | 1 (`"자동 로드 금지. 프로젝트 CLAUDE.md 등…"` names a harness file) |
| B | bulk: 철칙 1–7, 절차 1–6, 등급 | title/intro naming three harnesses, secondary refs | 1 (`"④ 등급 B 이하면 정밀 검증은 Claude Code의 정밀 모드(3콜) 권장 안내"`) |
| C | 철칙 1–9 (fullest invariant block), steps 2–4 | `model: opus`, inter-agent params, team protocol, `/humanize-redo`, summary block | 2 (tool-call count in a heading; `input_path`/`quick_rules_path` framing) |

- Reference file: the running procedure (B, C) names only `quick-rules.md`; A's own notes say the full taxonomy is "maintainer-only, runtime calls do not read it". `quick-rules.md` is generated, but every line is a concatenation of `quick_pattern`/`quick_fix` fields hand-written inside `ai-tell-taxonomy.md`. Suggested: take quick-rules' *selection* (which ids, S1/S2, self-check list) but anchor the content to the taxonomy's hand-written entries by id.
- Invariants: 10 confirmed in P0. C carries 9 in one place (missing an explicit 서법 보존 line, which lives in `quick-rules.header.md`, and a declarative 내용 앵커, which A states). No single file has all 10.
- **Recommendation:** B as skeleton, C's nine invariants merged, the two missing ones from quick-rules header / A. Cheapest to reverse. Confidence medium.
- **Counter:** B has no version stamp and is a parallel fork; nothing shows it is kept invariant-complete when A/C change, so a later lock bump could silently inherit a stale subset.

## E2 — anchor form, tested against upstream git history (06 §5.5)

Method: compare HEAD with ~10 and ~30 commits back for each key file in the cached clones.

| File | Finding |
|---|---|
| im-not-ai `ai-tell-taxonomy.md` | 61 → 80 → 85 pattern headings over 30 commits. **No id ever removed or renumbered.** Full heading text changed on 8 of 61 (mostly `· v2.x` tag suffixes; A-16 and B-2 changed substance too). One heading changed *level* (`### J-1.` → `## J-1.`) with id and content intact. Ids unique at HEAD |
| yoonmoon `ai-tell-taxonomy.md` | 10 → 11 sections; all 10 original section titles byte-identical across history; table first cells identical across history (the header word `패턴` repeats per table and must be skipped) |
| yoonmoon `detect/SKILL.md` | **Rewritten wholesale** from `### Phase n` headings to `<phase n="…">` tags at one commit; later a camelCase rename (`scoring_rubric` → `scoringRubric`); `phase n="3"` removed, `n="1S"` added. No anchor form survives a rewrite of that kind |
| fluent-korean output-style files | H2 headings byte-identical across the entire history of both files |
| fluent-korean README blocks | 6 → 7 blocks; bold-question text drifted on 3 of 6 (spacing, arrow glyph, wording). Least stable form observed |
| Code-block trap | No heading-shaped lines inside fences in any of the six files today; the rule still matters for the scanner. Real trap instead: `## J-1. 과도한 **볼드**` sits at H2 among H3 siblings and contains inline bold |

Per-candidate: (b) id prefix, depth-agnostic — strongest for im-not-ai, survives every edit seen; (a) full heading text — flawless for yoonmoon sections and fluent-korean styles, breaks on im-not-ai tags and README blocks; (c) heading path — never needed for uniqueness in these files, keep as the fallback 06 §5.5 rule 2 requires; (d) tag path — yoonmoon SKILL.md only, survives the rename only with case/underscore normalization; (e) bold label — README only, volatile; (f) heading + first cell — yoonmoon tables, perfectly stable.

- **Recommendation:** per-file-type combination — (b) for im-not-ai patterns with (c) as fallback; (a) for yoonmoon sections and fluent-korean style files; (f) for yoonmoon table rows; (d) normalized for yoonmoon's tagged SKILL.md; (e) for README blocks, accepting periodic re-anchoring. Confidence medium-high.
- **Counter:** one form everywhere is simpler to scan and review; but no single form applies to most files, and the one that could would maximize false "anchor not found" on exactly the churning files.

## E3 — upstream/ours separation in rendered SKILL.md (06 §16.2)

Options: A inline HTML comment markers per fragment; B section split + `## Sources` block; C sidecar `SKILL.provenance.yaml`; D frontmatter `metadata.provenance`.

- HTML comments: documented as stripped for CLAUDE.md, **not** documented for skills in either harness; skills docs say every loaded line is a recurring token cost. Treat inline comments as costing tokens on every invocation.
- Frontmatter: Claude Code documents `metadata` as free-form and inert; the stricter Agent Skills validator allows exactly `name, description, license, compatibility, metadata, allowed-tools`. Codex requires `name`, `description`, says nothing about extra keys.
- Extra files in the skill directory are allowed and ignored by both harnesses; the body loads only on invocation in both.
- **Recommendation:** C (sidecar). Zero context cost, per-fragment hash checkable by the build. Confidence medium. B is the fallback if human readability of SKILL.md alone matters more.
- **Counter:** a hand edit to SKILL.md drifts silently from the sidecar; only the build's hash check (06 §12 check 1) catches it, and only if it runs before the commit lands.

## E4 — policy composition rules (06 §16 decision ③)

- Block position: README says three times to append at the end ("지침 끝에", "본문 말미에", "텍스트 말미에"). Nothing argues otherwise.
- Frontmatter `name`/`description` are metadata, not sentences: replacing them with ours is not an upstream text change. `force-for-plugin` is added. formal-report omits `keep-coding-instructions` (default false: drops Claude Code's built-in engineering instructions).
- `force-for-plugin`: docs state "first loaded wins" only across plugins; two styles in one plugin is undocumented. Only one should set it (agent-reply). `/output-style` is removed (v2.1.91); the user switches via `/config` or the `outputStyle` setting, but a forced style overrides that while the plugin is enabled — **so formal-report is unreachable as an output style without disabling the plugin.** Open point for `flow.md`.
- Politeness block: keep `'사용자님'` literal → verbatim, 0 adapted; it is an ordinary honorific.
- Subagent clause (`## 추가 사항`): exists only in the coding variant; pulling it into formal-report is a cross-file `selected`. Recommended to leave it out, respecting upstream's split. Counter: formal-report sessions also spawn subagents.
- Sizes: agent-reply body 6,119 B / 43 lines; formal-report body + politeness block 6,094 B / 40 lines.
- **Recommendation:** as above, adapted count 0 for both profiles. Confidence medium.

## E5 — role for materials that are neither procedure nor taxonomy (06 §7, §13.2)

| File | Lines | Kind | Required by the steps? |
|---|---|---|---|
| yoonmoon `detect/references/lread-rubric.md` | 67 | scoring rubric + rationale | yes (Phase 1–2 "판정 틀") |
| yoonmoon `humanize/references/katfishnet-research.md` | 57 | research rationale, maps to taxonomy categories | yes (Phase 1 quantitative signals) |
| yoonmoon `detect/references/xdac-research.md` | 59 | research rationale, short-text | conditional (Phase 1-S only) |
| im-not-ai `references/quick-rules.md` | 129 | generated projection of the taxonomy | yes (step 1 "룰북 로드") |
| im-not-ai `references/rewriting-playbook.md` | 212 | per-category rewrite recipes (procedural) | **no** — listed under `## 참고` only |

- Folding research notes into `taxonomy` breaks taxonomy isolation: they cross-reference taxonomy categories directly. Folding rubric/recipes into `procedure` breaks one-supplier-per-slot.
- Dropping non-required references keeps everything but the playbook (saves 212 lines) at the risk of weaker rewrites.
- Licensing: the research notes paraphrase papers with citations and statistics, not extended verbatim prose; low risk under yoonmoon's MIT. The LREAD PDF stays excluded.
- **Recommendation:** add a fourth role `reference` (per slot, provenance-tracked, rendered under `references/`). Confidence medium.
- **Counter:** one `reference` bucket conflates three kinds (rubric, generated derivative, cited research) and only relocates the mixing problem; the spec deferred new roles to P4 for a reason.

## E6 — Codex local plugin and headless run

Summarized in "Environment checks done" above. Additional facts: skills are invocable by `$name` and by description match (`allow_implicit_invocation`, default true); subagents are enabled by `agents.enabled` (default true) and are invoked by natural-language delegation, not by name; installed plugins live under `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`.

## What `flow.md` must still settle

- E1, E3, E4, E5 recommendations: accept, amend, or reject each, with the counter-argument answered.
- E2 anchor forms: accept the per-file-type combination or fix one form; either way the scanner must be heading-depth-agnostic and skip table header rows.
- The formal-report reachability problem (E4): second output style, or a different vehicle for the second profile.
- Whether to run the Codex headless probe before P1 or defer it to P6.

## E1b — is B stale? (follow-up to E1)

Question raised in preflight: B was last changed 2026-08-09; A and C changed after. One `mid` run compared the commits, the steps and the invariants.

- Commits touching A or C after 2026-08-09: 9. Content changes B lacks: two — C `60bef28` adds 내용 앵커 (anchor_ledger, 철칙 #1 extended, extract/protect/verify in steps 2–4); A `b48fa05` adds chatbot-residue input hygiene. The other seven are paths, versions, script wiring.
- Steps 1–3, detection order, rewrite order, grades and the 4-part response are near-identical in B and C. C-only: anchor_ledger steps, `residual_findings`, `over_polish_aborted`, previous-output handling, team protocol. B-only: file-path input, non-Korean early exit, `옵션`/`참고`.
- Invariants in each file's own text: B lacks 빼기 전용, 서법 보존, 내용 앵커, and states register one-directionally. C lacks only 서법 보존, which exists only in `quick-rules.header.md` (added 08-23).
- Estimates: B skeleton + grafts ≈60–65 body lines; C skeleton ≈95–115 lines with 12–18 `adapted`. The report counted 4 `adapted` for B; renumbering and removing whole harness-bound sentences are structure and `selected`, so the preflight count is 0.
- **Recommendation:** B skeleton, grafts from C / header / A. Confidence medium. **Counter:** B's staleness becomes ours on every lock bump; B must be re-diffed, not just re-pinned.
- Run: mid (Sonnet), ≈92k tokens.

## Codex probe (E6, run in preflight)

2026-09-14, codex-cli 0.154.0, model `gpt-5.6-luna`, `codex exec --ephemeral --json -s read-only`. A throwaway plugin (`.codex-plugin/plugin.json`, one skill with a `metadata` frontmatter key and a `SKILL.provenance.yaml` sidecar, a `SessionStart` hook via `extensions.com.openai.hooks`) was installed through a local marketplace, and a scratch git repo held a project `AGENTS.md` and `.codex/agents/kq-sub.toml`. Everything was uninstalled afterwards; `~/.codex/config.toml` was diffed back to its original.

| Check | Result | Tokens (in / out) |
|---|---|---|
| `codex plugin marketplace add <dir>` + `codex plugin add <plugin>@<mkt>` | Works. Installs to `~/.codex/plugins/cache/<mkt>/<plugin>/<version>/`; adds `[marketplaces.*]` and `[plugins.*]` to `config.toml`. `remove` leaves an empty `cache/<mkt>/` directory | — |
| Plugin skill under `exec` (`$kq-ping …`) | **Works.** The model read `SKILL.md` from the plugin cache with a shell command and returned the fixed token | 35k / 285 |
| `metadata` frontmatter key and sidecar file | Accepted, no warning | — |
| Project `AGENTS.md` under `exec` | **Loaded** | 17k / 11 |
| Project `AGENTS.md` reaching a spawned subagent | **Yes** — the subagent answered with the AGENTS.md token | — |
| Custom agent `.codex/agents/kq-sub.toml` | **Not reached.** `spawn_agent` exposed no agent-type parameter; a generic subagent was spawned. Same with the project marked trusted (`-c projects."<dir>".trust_level="trusted"`). Cause unknown: model, feature flag, or `exec` mode | 129k / 667, 129k / 1,246 |
| Plugin hook | **Not run.** `--dangerously-bypass-hook-trust` was blocked by Claude Code's auto-mode classifier; without it an untrusted hook does not run | — |
