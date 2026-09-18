"""Scanning (era 98 spec §2.1, §2.2, §2.5). A hit is (path, line number, rule, masked excerpt); the host value itself
is never printed, so the output is safe to paste into a record or an agent's context."""
import hashlib
import re
import subprocess
from pathlib import Path

from hostguard import local, rules

ALLOW = rules.HERE / "allow.tsv"
MESSAGE_PATH = "<commit-message>"
ZERO = "0" * 40


def line_hash(line):
    return hashlib.sha256(line.rstrip("\r\n").encode("utf-8")).hexdigest()[:16]


def allowlist():
    out = set()
    if ALLOW.exists():
        for line in ALLOW.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                out.add((parts[0], parts[1], parts[2]))
    return out


class Scanner:
    def __init__(self, repo=rules.ROOT, record=True):
        self.repo = Path(repo)
        lits = rules.host_literals(self.repo)
        if record:
            local.remember(lits)
        self.patterns = rules.compiled(lits + local.remembered())
        self.allowed = allowlist()

    def text(self, text, path):
        hits = []
        for n, line in enumerate(text.splitlines(), 1):
            h = None
            for rule, rx in self.patterns:
                for m in rx.finditer(line):
                    if rules.placeholder(rule, m.group(0)):
                        continue
                    h = h or line_hash(line)
                    if (path, rule, h) in self.allowed:
                        break
                    excerpt = (line[max(0, m.start() - 30):m.start()] + f"<{rule}>" + line[m.end():m.end() + 30]).strip()
                    hits.append((path, n, rule, excerpt))
                    break
        return hits + self.across_lines(text, path, {r for _, _, r, _ in hits})

    def across_lines(self, text, path, found):
        """A host path or hash wrapped over a line break: substring rules only, on the text with line breaks and the
        indentation around them removed. Reported at line 0; not exemptable, since a wrapped host path is never meant."""
        if "\n" not in text:
            return []
        joined = re.sub(r"[ \t]*\r?\n[ \t>]*", "", text)
        out = []
        for rule, rx in self.patterns:
            if rule in rules.SUBSTRING_RULES and rule not in found:
                m = rx.search(joined)
                if m and not rx.search(text):
                    out.append((path, 0, rule, "(value wrapped across a line break)"))
        return out

    # ---- git sources -----------------------------------------------------------------------------------------
    def git(self, *a, input=None):
        return subprocess.run(["git", "-C", str(self.repo), *a], input=input, capture_output=True, check=True).stdout

    def blob(self, spec, path):
        data = self.git("cat-file", "blob", spec)
        try:
            return self.text(data.decode("utf-8"), path)
        except UnicodeDecodeError:
            return []

    def staged(self):
        names = self.git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").decode("utf-8").split("\0")
        hits = []
        for p in filter(None, names):
            if not p.startswith("upstream/"):
                hits += self.blob(f":{p}", p)
        return hits

    def message(self, text):
        body = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
        return self.text(body, MESSAGE_PATH)

    def commits(self, commits, seen=None):
        hits, seen = [], set() if seen is None else seen
        for c in commits:
            hits += [(f"{MESSAGE_PATH} {c[:7]}", n, r, e) for _, n, r, e in self.message(self.git("log", "-1", "--format=%B", c).decode("utf-8"))]
            # -m: a merge commit is diffed against each parent, so content that only its resolution introduced is seen
            out = self.git("diff-tree", "-r", "-m", "--root", "--no-commit-id", "-z", c).decode("utf-8").split("\0")
            it = iter(filter(None, out))
            for meta in it:
                path = next(it)
                sha = meta.split()[3]
                if sha == ZERO or path.startswith("upstream/") or (path, sha) in seen:
                    continue
                seen.add((path, sha))
                hits += self.blob(sha, path)
        return hits

    def history(self, ref="HEAD"):
        """The tip tree and every commit reachable from ref."""
        commits = self.git("rev-list", ref).decode().split()
        hits, seen = [], set()
        for line in self.git("ls-tree", "-r", ref).decode("utf-8").splitlines():
            meta, path = line.split("\t", 1)
            if meta.split()[1] == "blob" and not path.startswith("upstream/"):
                seen.add((path, meta.split()[2]))
                hits += self.blob(meta.split()[2], path)
        return hits + self.commits(commits, seen)

    def push(self, lines):
        """pre-push stdin: '<local ref> <local sha> <remote ref> <remote sha>' per line."""
        commits = []
        for line in lines:
            parts = line.split()
            if len(parts) != 4 or parts[1] == ZERO:
                continue
            rng = [parts[1], "--not", "--remotes"] if parts[3] == ZERO else [f"{parts[3]}..{parts[1]}"]
            commits += self.git("rev-list", *rng).decode().split()
        return self.commits(dict.fromkeys(commits))


def report(hits, out):
    hits = list(dict.fromkeys(hits))
    for path, n, rule, excerpt in hits:
        out.write(f"{path}:{n}: {rule}: {excerpt}\n")
    if hits:
        out.write(f"hostguard: {len(hits)} host-state hit(s). Remove them, or exempt a false positive with "
                  f"`python3 -m hostguard allow <path> <line> <reason>` (era 98 spec §2.2).\n")
    return 1 if hits else 0
