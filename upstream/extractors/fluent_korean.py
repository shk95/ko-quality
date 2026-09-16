"""fluent-korean → policy/fluent-korean (flow.md D4). Variants as blocks; README selection blocks as fenced content (P3)."""
import re

from .markdown import parse, split_frontmatter
from .normalized import excluded_lines, fragment_lines, q
from .source import AnchorNotFound, read

NAME = "fluent-korean"
VARIANTS = [("coding", "plugins/fluent-korean/output-styles/fluent-korean.md"),
            ("not-coding", "plugins/fluent-korean/output-styles/fluent-korean-not-coding.md")]
README = "README.md"
SECTION = "## 세부 동작 - 저는 Claude가 이랬으면 좋겠어요."
BLOCK_IDS = ["beginner", "honorific", "plain-vocabulary", "all-korean-output", "style-sensitive", "think-in-korean", "proofreading"]
HDR = "# Temporary format (P1 shape + data section, P3 — flow.md). Schema is derived in P4. Text values are exact upstream bytes."
BLOCK_NOTE = "fenced block content only; the 2-space list indentation removed"


def readme_blocks(text):
    rl = text.split("\n")
    if SECTION not in rl:
        raise AnchorNotFound(f"{README}: {SECTION} not found")
    s0 = rl.index(SECTION)
    s1 = next((k for k in range(s0 + 1, len(rl)) if rl[k].startswith("## ")), len(rl))
    blocks, k = [], s0
    while k < s1:
        m = re.match(r"^- (\*\*.+?\*\*)", rl[k])
        if m:
            o = next(x for x in range(k + 1, s1) if rl[x].strip() == "```")
            c = next(x for x in range(o + 1, s1) if rl[x].strip() == "```")
            content = [x[2:] if x.startswith("  ") else x for x in rl[o + 1:c]]
            blocks.append((m.group(1), "\n".join(content)))
            k = c
        k += 1
    return blocks


def extract(commit):
    frags, data, failures = [], {}, []
    for vid, path in VARIANTS:
        text = read(NAME, path, commit)
        fm, _ = split_frontmatter(text)
        data[vid] = dict(path=path, frontmatter=fm)
        for n, b in enumerate(parse(text, top="(intro)"), 1):
            frags.append(dict(id=f"{vid}.{n:02d}", kind=b["kind"], blanks=b["blanks"], text=b["text"], path=path,
                              anchor=b["anchor"], transform="verbatim"))
    blocks = readme_blocks(read(NAME, README, commit))
    if len(blocks) != len(BLOCK_IDS):
        failures.append(("blocks", f"{README}: expected {len(BLOCK_IDS)} selection blocks, found {len(blocks)}"))
    for bid, (label, text) in zip(BLOCK_IDS, blocks):
        frags.append(dict(id=f"block.{bid}", kind="block", text=text, path=README,
                          anchor=f"{SECTION} > bold label {label} > code block", transform="selected", note=BLOCK_NOTE))
    out = [HDR, "role: policy", "name: fluent-korean", "data:"]
    for vid, d in data.items():
        out += [f"  {vid}:", f"    path: {d['path']}", "    frontmatter:"]
        out += [f"      {k}: {q(v)}" for k, v in d["frontmatter"].items()]
    out.append("  blocks: [" + ", ".join(BLOCK_IDS) + "]")
    out.append("fragments:")
    for f in frags:
        out += fragment_lines(f, NAME, commit)
    out += excluded_lines([(README, SECTION + " > bold question and explanation text", "instructions to the human installer, not policy text"),
                           (README, "all other sections", "installation and notes (06b P0 map: not supplied)")])
    return {"policy/fluent-korean.yaml": "\n".join(out) + "\n"}, failures
