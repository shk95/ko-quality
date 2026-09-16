# P3 — fluent-korean → `policy`

2026-09-14. Branch `dev`. Upstream fluent-korean at `ce8683f0` (lock). Flow: `5-preflight/flow.md` §3 P3.

## Result

The policy reaches both places 06 §9 needs. A forced output style put its marker line on the main reply, and the agent definition put its marker line on the subagent's reply. The subagent in turn ran the `ko-diagnose` skill. Selecting `formal-report` as the output style does not take effect while `agent-reply` is forced: the selection is accepted under either name, and the agent-reply marker still appears. Body text in `dist/` is byte-identical to the normalized fragments (56 spans), with 0 `adapted`.

| Artifact | Path |
|---|---|
| Normalized policy (temporary YAML) | `upstream/normalized/policy/fluent-korean.yaml` — variants `coding`, `not-coding` (36 fragments) + blocks 1–7 (7 fragments); frontmatter kept as data |
| Output styles | `dist/claude-code/output-styles/agent-reply.md` (forced), `formal-report.md` (unforced) |
| Agent | `dist/claude-code/agents/korean-reviewer.md` |
| Provenance | `dist/claude-code/provenance/policy.yaml` → `tests/check_provenance.py dist/claude-code/provenance/policy.yaml`: `56 upstream spans checked, 0 errors` |
| Runs | `tests/runs/P3/policy-channel.json` |

## Decision ③ — policy composition, as built

| Item | Built | Evidence |
|---|---|---|
| Block position | Appended at the end of the body, README order, one blank line before | README: "블록 내의 텍스트를 지침 끝에 추가" |
| Block ids | `beginner`, `honorific`, `plain-vocabulary`, `all-korean-output`, `style-sensitive`, `think-in-korean`, `proofreading` (README bullets 1–7) | anchored by bold label |
| Blocks per profile | agent-reply `[]`; formal-report `[honorific]` | 06 §6 |
| `'사용자님'` | Literal, `verbatim` | — |
| Frontmatter | `name`, `description` ours; `keep-coding-instructions` as upstream (coding `true`, not-coding absent → false); upstream values kept as data in the normalized file | — |
| `force-for-plugin` | agent-reply only | canary-main: agent-reply marker on the main reply |
| Subagent clause (`## 추가 사항`) in formal-report | Not added | coding body carries it into agent-reply and korean-reviewer |
| Policy in the subagent | korean-reviewer body = agent-reply policy text + ours §8 append | canary-subagent: agent marker ×5 in the subagent's output; `subagent_type: ko-quality:korean-reviewer` |
| formal-report reachability | **Not reachable while agent-reply is forced.** `--settings '{"outputStyle":"formal-report"}'` and `"ko-quality:formal-report"` are both accepted (stream `init.output_style` echoes them), and both replies carry the agent-reply marker; formal-report marker 0 | canary-formal-name, canary-formal-namespaced. Carried to P5 (flow D4: decision ②, fallback agent-only) |

## Runs

Claude Code 2.1.270, `claude-opus-5[1m]`, headless, user settings excluded, empty cwd. Six runs, $1.98. The canary runs used a throwaway copy of `dist/claude-code` with one marker line appended to each of the three files. The policy runs used `dist/` unchanged.

| Case | Plugin | Setting | Markers seen (style / formal / agent) | Notes |
|---|---|---|---|---|
| canary-main | copy | — | 2 / 0 / 0 | `init.output_style` says `default`, yet the forced style applied: the field reports the setting, not the style in effect |
| canary-subagent | copy | — | 2 / 0 / 5 | Main delegated to `ko-quality:korean-reviewer`; the subagent invoked `ko-quality:ko-diagnose` and read its references; main relayed the answer and added its own marker |
| canary-formal-name | copy | `outputStyle: formal-report` | 2 / 0 / 0 | agent-reply wins |
| canary-formal-namespaced | copy | `outputStyle: ko-quality:formal-report` | 2 / 0 / 0 | agent-reply wins |
| policy-main | dist | — | — | Report on git rebase vs merge: complete sentences in prose, 0 em-dashes; noun-phrase endings only in headings and table cells (allowed by 문장 단위 2) |
| policy-subagent | dist | — | — | Review relayed; 0 em-dashes. The reply ends with the absolute paths of the reference files it read |

## Checks (flow.md §3 P3)

| Check | Result |
|---|---|
| Policy reaches the main thread (06 §2.1 constraint) | Yes (canary-main) |
| Policy reaches the subagent through its definition | Yes (canary-subagent) |
| Body text in `dist/` byte-identical to normalized fragments | Yes: `agent-reply.md` body identical to upstream `fluent-korean.md` body; `formal-report.md` body = `fluent-korean-not-coding.md` body + honorific block; checker 56/0 |
| `adapted` = 0 | Yes (43 fragments: 36 `verbatim`, 7 `selected`) |

## Differs from spec

- **Proposed 06 revision for 7-review (decision ③).** §9 "합성 규칙은 P3에서 확정한다" can become the table above. §6 `blocks: [honorific]` id is now fixed. §9 should also state the measured consequence of forcing one style: the second profile's output style cannot be selected while the plugin is enabled, so the second profile needs another vehicle (P5).
- korean-reviewer already carries the §8 `append` (ours), not only the policy text flow P3 step 3 named. Without a role line the agent would have none.
- Provenance for output styles and the agent lives in one plugin-level file (`provenance/policy.yaml`), not in a sidecar next to each file as D3 describes for skills. `output-styles/` and `agents/` are directories Claude Code scans for definitions; a non-Markdown file there was not tested and was not needed.

## Spec did not know

- **`init.output_style` in `stream-json` is not the style in effect.** It echoes the configured setting (`default`, or whatever `--settings` passed) even when a forced plugin style is applied. P5's `claude plugin eval` and P7's logger (`injection_point`) cannot use it as evidence of policy.
- **A plugin agent can run a plugin skill.** korean-reviewer invoked `ko-diagnose` and read its references with `tools: Read, Grep, Glob, Skill`. §8's "`preset: review`" can be carried by the skill instead of copying the procedure into the agent (P5 material).
- **The subagent leaked install paths.** policy-subagent's relayed reply lists the absolute paths of the reference files read. Not a policy question; recorded for P5 (install doc) and P7 (masking).
- Both style names are accepted in `outputStyle` (`formal-report` and `ko-quality:formal-report`).

## Temporary format friction (P4 material)

- **Frontmatter is data, not fragments.** The P1 shape had only `fragments`; a `data:` section was added for each variant's original frontmatter.
- **Blocks are fenced text inside a nested list.** The paste target is the fence content minus the two-space list indentation, so a block is `selected` and matches upstream line by line, never as one substring.
- **Two variants, stored twice.** The variants differ in three places (06b P0), yet every fragment is stored per variant (18 shared pairs). A shared base with differences would be smaller but is a unit upstream never shipped (06b decision a).
- **Blank-line counts.** P2 recorded "blank before: yes/no"; byte-identical bodies needed the count (upstream uses two blank lines between sections).
- **Composition has no home in the YAML.** Which blocks go where, and in which order, lives in the render script; `assemble/profiles/*.yaml` takes it in P5.

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | D4 as preflight decided | Applied | medium-high (canaries) | flow D4 |
| 2 | minor | Block ids from README meaning / numeric | Meaningful ids | high | 06 §6 already names `honorific`, `think-in-korean` |
| 3 | minor | Plugin-level provenance file / sidecar per output-style and agent file | Plugin-level | medium | keeps definition directories free of non-Markdown files |
| 4 | minor | korean-reviewer with §8 append now / policy text only until P5 | With append | medium | agent needs a role to be testable |
| 5 | minor | Canary test on a throwaway copy / canary in `dist/` then revert | Copy | high | `dist/` never carries test text |
| 6 | minor | Test formal-report selection with both name forms / one | Both | high | naming of plugin styles undocumented |

## Subagent runs

Exploration cap: 0 of 4 used.

| # | Tier | Purpose | Tokens | Result |
|---|---|---|---|---|
| V | mid (Sonnet 5) | Verification of the done-condition (outside the cap) | 118.0k | Both clauses and all three checks **met**. Reproduced both channels with its own markers on a throwaway copy (`subagent_type: ko-quality:korean-reviewer` seen in the stream). Diffed rendered bodies against upstream directly. Noted the committed summary abbreviated the delegation call; `delegations` (tool, `subagent_type`) added to `tests/runs/P3/policy-channel.json` |

## Release-blocked

None. Every done-condition clause was verified met. formal-report reachability is not a P3 release-blocked condition; it carries to P5 (flow D4).
