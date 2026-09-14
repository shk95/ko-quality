"""TOML subset for Codex agent files (.codex/agents/*.toml) written by build/agent_plugin.py (stdlib only; Python 3.9 has no tomllib).

Writes and reads flat tables of string keys: `key = "basic string"` and `key = '''multi-line literal'''`.
A multi-line literal string cannot contain three single quotes; the writer refuses such text."""
import json
import re


def dumps(table):
    out = []
    for key, value in table.items():
        if "\n" in value:
            if "'''" in value:
                raise ValueError(f"{key}: text contains ''' and cannot be a TOML multi-line literal string")
            out.append(f"{key} = '''\n{value}'''")
        else:
            out.append(f"{key} = {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(out) + "\n"


def loads(text):
    table, i = {}, 0
    lines = text.split("\n")
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\w+) = '''$", line)
        if m:
            j = i + 1
            buf = []
            while not lines[j].endswith("'''"):
                buf.append(lines[j]); j += 1
            last = lines[j][:-3]
            value = "\n".join(buf + ([last] if last else [])) + ("" if last else "\n")
            table[m.group(1)] = value
            i = j + 1
            continue
        m = re.match(r'^(\w+) = (".*")$', line)
        if m:
            table[m.group(1)] = json.loads(m.group(2))
        i += 1
    return table
