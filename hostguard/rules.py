"""Deny list of era 98 spec §2.1: host literals read at scan time, the local accumulated list, fixed patterns.

Standard library only. Pattern sources are written so that this file does not match its own patterns.
"""
import getpass
import hashlib
import json
import re
import socket
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OWN_PLUGINS = {"ko-quality"}
OWN_MARKETPLACES = {"ko-quality", "claude-plugins-official"}
SUBSTRING_RULES = {"host:home", "host:user-in-path", "host:repo-path", "host:repo-path-hash", "host:project-slug"}
PLAIN_WORD = re.compile(r"[a-z]+")

FIXED = [
    ("fixed:tmp-path", re.compile(r"/private/(?:tmp|var)/|/var/fold[e]rs/|/tmp/claude-\d+")),
    ("fixed:nix-path", re.compile(r"/run/current[-]system/|/nix/st[o]re/")),
    ("fixed:scratch-path", re.compile(r"[^\s\"'`()\[\]]*scratch[p]ad/")),
    ("fixed:uuid", re.compile(r"(?<![0-9a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])")),
    ("fixed:plan-en", re.compile(r"\b(?:free|paid|Plus|Pro)\x20plan\b|\busage[\x20-]limit|\bquota\b|\brate-limited\b")),
    ("fixed:plan-ko", re.compile("(?:무료|유료)\\x20?플랜|요금[제]|(?:사용|계정|사용량)\\x20?한도")),
]


def placeholder(rule, text):
    """A match that is an elided or placeholder path, not a real one."""
    return rule == "fixed:scratch-path" and (text.startswith(("...", "<", "…")) or text.startswith("scratch" + "pad/"))


def conditions():
    p = HERE / "conditions.txt"
    if not p.exists():
        return set()
    return {l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}


def _json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def host_literals(repo=ROOT, home=None):
    """(rule, value) pairs read from this host now."""
    home = Path(home) if home else Path.home()
    repo = Path(repo).resolve()
    out = [("host:home", str(home))]
    user = getpass.getuser()
    if len(user) >= 3:
        out.append(("host:user-in-path", f"/{user}/"))
    host = socket.gethostname().split(".")[0]
    if len(host) >= 4 and host.lower() != "localhost":
        out.append(("host:hostname", host))
    out.append(("host:repo-path", str(repo)))
    try:
        out.append(("host:repo-path", "~/" + str(repo.relative_to(home))))
    except ValueError:
        pass
    out.append(("host:repo-path-hash", hashlib.sha256(str(repo).encode("utf-8")).hexdigest()[:16]))
    out.append(("host:project-slug", "-" + str(repo).strip("/").replace("/", "-")))
    km = _json(home / ".claude/plugins/known_marketplaces.json")
    if isinstance(km, dict):
        out += [("host:user-marketplace", m) for m in km if m not in OWN_MARKETPLACES]
    ip = _json(home / ".claude/plugins/installed_plugins.json")
    if isinstance(ip, dict):
        for key in ip.get("plugins", {}):
            name, _, market = key.partition("@")
            if name in OWN_PLUGINS:
                continue
            out.append(("host:user-plugin", key))
            if not PLAIN_WORD.fullmatch(name):
                out.append(("host:user-plugin", name))
    cond = conditions()
    models = []
    st = _json(home / ".claude/settings.json")
    if isinstance(st, dict) and isinstance(st.get("model"), str):
        models.append(st["model"])
    cx = home / ".codex/config.toml"
    if cx.exists():
        try:
            models += re.findall(r'^\s*model\s*=\s*"([^"]+)"', cx.read_text(encoding="utf-8"), re.M)
        except OSError:
            pass
    out += [("host:model-setting", m) for m in models if m not in cond and not PLAIN_WORD.fullmatch(m) and len(m) >= 4]
    return [(r, v) for r, v in out if v]


def matcher(rule, value):
    if rule in SUBSTRING_RULES:
        return re.compile(re.escape(value))
    return re.compile(r"(?<![\w-])" + re.escape(value) + r"(?![\w-])")


def compiled(literals):
    seen, out = set(), []
    for rule, value in literals:
        if (rule, value) in seen:
            continue
        seen.add((rule, value))
        out.append((rule, matcher(rule, value)))
    return out + FIXED
