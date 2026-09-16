"""Parser for the YAML subset used in assemble/ (stdlib only; PyYAML is not in the toolchain).

Supports: comments, `key: scalar`, `key: [a, b]`, `key: "json string"`, `key: null|true|false`,
and nested maps by two-space indentation. Nothing else."""
import json


def _scalar(v):
    v = v.strip()
    if v == "" :
        return None
    if v.startswith('"'):
        return json.loads(v)
    if v.startswith("["):
        inner = v[1:-1].strip()
        return [] if not inner else [_scalar(x) for x in inner.split(",")]
    if v in ("null", "~"):
        return None
    if v in ("true", "false"):
        return v == "true"
    return v


def loads(text):
    root = {}
    stack = [(-1, root)]
    lines = [l for l in text.split("\n") if l.strip() and not l.lstrip().startswith("#")]
    for i, line in enumerate(lines):
        indent = len(line) - len(line.lstrip(" "))
        key, _, rest = line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        nxt_indent = len(nxt) - len(nxt.lstrip(" "))
        if rest.strip() == "" and nxt and nxt_indent > indent:
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = _scalar(rest.split(" #")[0] if not rest.strip().startswith('"') else rest)
    return root


def load(path):
    return loads(path.read_text(encoding="utf-8"))
