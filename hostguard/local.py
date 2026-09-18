"""The local root (era 98 spec §2.3, §2.4). Nothing here deletes anything unless `clean` is given the candidate's id."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE_DAYS = 7
DENY_HEADER = "# hostguard accumulated deny list: rule<TAB>value. Local only; never commit.\n"


def root():
    return Path(os.path.expanduser(os.environ.get("KO_QUALITY_WORK") or "~/.ko-quality-work"))


# ---- accumulated deny list ---------------------------------------------------------------------------------------
def remembered():
    p = root() / "deny.local"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#") and "\t" in line:
            rule, value = line.split("\t", 1)
            if value:
                out.append((rule, value))
    return out


def remember(literals):
    """Append host literals not yet in deny.local. Does nothing when the local root does not exist."""
    r = root()
    if not r.is_dir():
        return
    p = r / "deny.local"
    have = set(remembered())
    new = [(a, b) for a, b in literals if (a, b) not in have]
    if new:
        with p.open("a", encoding="utf-8") as f:
            if p.stat().st_size == 0:
                f.write(DENY_HEADER)
            f.writelines(f"{a}\t{b}\n" for a, b in dict.fromkeys(new))


# ---- deletion candidates -----------------------------------------------------------------------------------------
def size(path):
    if path.is_file():
        return path.stat().st_size
    total = 0
    for dp, _, fs in os.walk(path):
        for f in fs:
            try:
                total += os.lstat(os.path.join(dp, f)).st_size
            except OSError:
                pass
    return total


def dev_home():
    try:
        env = json.loads((REPO / ".claude/settings.json").read_text(encoding="utf-8")).get("env", {})
    except (OSError, ValueError):
        env = {}
    v = env.get("KO_QUALITY_HOME")
    return Path(os.path.expanduser(v)) if v else None


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout


def candidates():
    """[(id, ready, reason, paths-or-refs, bytes)]"""
    out = []
    r = root()
    if r.is_dir():
        for era in sorted(p for p in r.iterdir() if p.is_dir() and not p.name.startswith(".")):
            b = era / "build"
            if b.is_dir():
                done = (era / "REVIEWED").exists()
                out.append((f"{era.name}/build", done,
                            "the era's review has closed" if done else "kept until the era's review closes (hostguard mark-reviewed)",
                            [b], size(b)))
            rw = era / "rewrites"
            if rw.is_dir():
                for d in sorted(p for p in rw.iterdir() if p.is_dir()):
                    out.append((f"{era.name}/rewrites/{d.name}", True, "backup made before a history rewrite; delete once the rewritten history is confirmed", [d], size(d)))
    refs = [l for l in git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/original").split()
            if l.startswith(("refs/heads/backup", "refs/original/"))]
    for ref in refs:
        out.append((f"ref:{ref[len('refs/'):]}", True, "local ref left by a history rewrite; delete once the rewritten history is confirmed", [ref], 0))
    h = dev_home()
    if h and (h / "state").is_dir():
        cutoff = time.time() - STATE_DAYS * 86400
        old = [p for p in (h / "state").glob("*.json") if p.stat().st_mtime < cutoff]
        if old:
            out.append(("state", True, f"{len(old)} session state file(s) older than {STATE_DAYS} days in the development log home; each may hold a prompt",
                        old, sum(p.stat().st_size for p in old)))
    return out


def human(n):
    for unit in ("B", "K", "M", "G"):
        if n < 1024 or unit == "G":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024


def status(out=sys.stdout):
    r = root()
    if not r.is_dir():
        out.write(f"local root missing: create it with `mkdir {r}` (era 98 spec §2.3)\n")
    cs = candidates()
    ready = [c for c in cs if c[1]]
    for cid, ok, reason, _, n in cs:
        out.write(f"{'READY  ' if ok else 'pending'} {cid:<40} {human(n) if n else '':>7}  {reason}\n")
    out.write(f"{len(ready)} ready. Delete with `python3 -m hostguard clean <id> ...`; nothing is deleted otherwise.\n")
    return 0


def clean(ids, out=sys.stdout):
    cs = {c[0]: c for c in candidates()}
    unknown = [i for i in ids if i not in cs]
    if unknown:
        out.write(f"unknown candidate(s): {', '.join(unknown)}. Run `python3 -m hostguard status`.\n")
        return 1
    notready = [i for i in ids if not cs[i][1]]
    if notready:
        out.write(f"not ready: {', '.join(notready)}\n")
        return 1
    for i in ids:
        for target in cs[i][3]:
            out.write(f"deleting {i}: {target if isinstance(target, str) else target.name}\n")
            if isinstance(target, str):
                subprocess.run(["git", "-C", str(REPO), "update-ref", "-d", target], check=True)
            elif target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
    return 0


def mark_reviewed(era, out=sys.stdout):
    d = root() / era
    d.mkdir(parents=True, exist_ok=True)
    (d / "REVIEWED").write_text(time.strftime("%Y-%m-%d") + "\n", encoding="utf-8")
    out.write(f"marked {era} reviewed; its build material is now a deletion candidate\n")
    return 0


def notice(out=sys.stdout):
    """SessionStart hook output. Silent with no ready candidate; never raises; always exit 0."""
    try:
        ready = [c for c in candidates() if c[1]]
        if not ready:
            return 0
        line = f"ko-quality: {len(ready)} local cleanup candidate(s). Review with `python3 -m hostguard status`."
        out.write(json.dumps({
            "systemMessage": line,
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"Tell the user once, in one short line, at a natural point: {line} Nothing is deleted without their say.",
            },
        }) + "\n")
    except Exception:
        pass
    return 0
