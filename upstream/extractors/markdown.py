"""Block parser for upstream Markdown (flow.md D2): code-fence aware, heading-depth-agnostic,
XML-style tags, tables (header and separator rows kept apart), quotes, list items, paragraphs.

Anchor forms produced (context is the tag path, else the last heading, else `top`):
  <heading line>                                 heading
  <context> > paragraph N | quote N | item N     ordinal within context and kind
  <context> > item **label** | bold label **label**
  <context> > table header "<first cell>" | table separator | row "<first cell>"
  <any of the above> > N                         second and later occurrence of the same anchor in one file
  <tag path> > open | <tag path> > close         tag lines (text stored without indentation)
"""
import re

TAG_OPEN = re.compile(r"^\s*<([A-Za-z]+)((?:\s+\w+=\"[^\"]*\")*)\s*>\s*$")
TAG_CLOSE = re.compile(r"^\s*</([A-Za-z]+)>\s*$")
ITEM = re.compile(r"^(\d+\.|-) ")


def split_frontmatter(text):
    """Top-level `key: value` pairs only; a bare `key:` with indented children keeps its raw child lines as the value."""
    lines = text.split("\n")
    if lines and lines[0] == "---":
        end = lines.index("---", 1)
        fm, key = {}, None
        for l in lines[1:end]:
            if l.startswith((" ", "\t")) and key is not None:
                fm[key] = (fm[key] + "\n" + l) if fm[key] else l
            elif ": " in l:
                key, value = l.split(": ", 1); fm[key] = value
            elif l.endswith(":"):
                key = l[:-1]; fm[key] = ""
        return fm, lines[end + 1:]
    return {}, lines


def parse(text, top="(top)"):
    """Blocks: kind, text, anchor, ctx, blanks (blank lines before the block)."""
    _, lines = split_frontmatter(text)
    blocks, heads, tags, counters = [], [], [], {}
    i, blanks, fence = 0, 0, False

    def ctx():
        return "/".join(tags) if tags else (heads[-1] if heads else top)

    def add(kind, body, loc):
        c = ctx()
        counters[(c, kind)] = counters.get((c, kind), 0) + 1
        anchor = f"{c} > {loc if loc else kind + ' ' + str(counters[(c, kind)])}"
        blocks.append(dict(kind=kind, text=body, anchor=anchor, ctx=c, blanks=blanks))

    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            fence = not fence
        if not fence and not l.strip():
            blanks += 1; i += 1; continue
        m = TAG_OPEN.match(l)
        if m and not fence:
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(2)))
            seg = m.group(1).lower().replace("_", "") + (f"[n={attrs['n']}]" if "n" in attrs else "")
            tags.append(seg)
            blocks.append(dict(kind="tag", text=l.strip(), anchor=f"{'/'.join(tags)} > open", ctx=ctx(), blanks=blanks))
            blanks = 0; i += 1; continue
        m = TAG_CLOSE.match(l)
        if m and not fence:
            blocks.append(dict(kind="tag", text=l.strip(), anchor=f"{'/'.join(tags)} > close", ctx=ctx(), blanks=blanks))
            tags.pop()
            blanks = 0; i += 1; continue
        if not fence and re.match(r"^#{1,6} ", l):
            heads.append(l); add("heading", l, "heading"); blocks[-1]["anchor"] = l
            blanks = 0; i += 1; continue
        if not fence and l.startswith("|"):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            is_sep = all(re.fullmatch(r":?-+:?", c) for c in cells)
            prev_row = blocks and blocks[-1]["kind"] in ("row", "table-header", "table-sep") and not blanks
            if is_sep:
                add("table-sep", l, "table separator")
            elif not prev_row:
                add("table-header", l, f'table header "{cells[0]}"')
            else:
                add("row", l, f'row "{cells[0]}"')
            blanks = 0; i += 1; continue
        if not fence and l.startswith(">"):
            j = i
            while j < len(lines) and lines[j].startswith(">"):
                j += 1
            add("quote", "\n".join(lines[i:j]), None); blanks = 0; i = j; continue
        if not fence and ITEM.match(l):
            j = i + 1
            while (j < len(lines) and lines[j].startswith(" ") and lines[j].strip()
                   and not TAG_CLOSE.match(lines[j]) and not TAG_OPEN.match(lines[j])):
                j += 1
            label = re.match(r"^(?:\d+\.|-) (\*\*[^*]+\*\*)", l)
            add("item", "\n".join(lines[i:j]), f"item {label.group(1)}" if label else None)
            blanks = 0; i = j; continue
        # paragraph (a fenced block is kept whole as one paragraph)
        j = i + 1
        if fence:
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            j = min(j + 1, len(lines)); fence = False
        else:
            while (j < len(lines) and lines[j].strip() and not ITEM.match(lines[j])
                   and not lines[j].startswith(("|", ">", "#", "```"))
                   and not TAG_CLOSE.match(lines[j]) and not TAG_OPEN.match(lines[j])):
                j += 1
        label = re.match(r"^(\*\*[^*]+\*\*)", l)
        add("paragraph", "\n".join(lines[i:j]), f"bold label {label.group(1)}" if label else None)
        blanks = 0; i = j
    # 06 §5.5 rule 2: an anchor repeated in one file gets its occurrence number (" > 2", " > 3")
    seen = {}
    for blk in blocks:
        seen[blk["anchor"]] = seen.get(blk["anchor"], 0) + 1
        if seen[blk["anchor"]] > 1:
            blk["anchor"] = f"{blk['anchor']} > {seen[blk['anchor']]}"
    return blocks


def headings(lines):
    """(index, line) of heading lines outside code fences."""
    out, fence = [], False
    for i, l in enumerate(lines):
        if l.startswith("```"):
            fence = not fence; continue
        if not fence and re.match(r"^#{1,6} ", l):
            out.append((i, l))
    return out
