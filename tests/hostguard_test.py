#!/usr/bin/env python3
"""hostguard tests (era 98 spec §6, done conditions 2-4). Standard library only. Run: python3 tests/hostguard_test.py

Every fixture that carries a host value is built at run time from this host or from a temporary fake home, so this
file holds none (era 98 preflight F2). Planted values in git fixtures are committed only inside temporary repositories.
"""
import getpass
import hashlib
import socket
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TMP = Path(tempfile.mkdtemp(prefix="hostguard-test-"))
os.environ["KO_QUALITY_WORK"] = str(TMP / "work")

from hostguard import local, redact, rules, scan  # noqa: E402

failures = []


def check(name, cond):
    if not cond:
        failures.append(name)
    print(("ok   " if cond else "FAIL ") + name)


def rules_hit(scanner, text):
    return {r for _, _, r, _ in scanner.text(text, "fixture.md")}


def sep(*parts):
    """Join parts at run time so a fixed-pattern example never sits whole in this file."""
    return "".join(parts)


# ---- fake home: plugins, marketplaces, model settings ---------------------------------------------------------------
fake = TMP / "home"
(fake / ".claude/plugins").mkdir(parents=True)
(fake / ".codex").mkdir()
(fake / ".claude/plugins/known_marketplaces.json").write_text(json.dumps({"claude-plugins-official": {}, "ko-quality": {}, "my-market": {}}))
(fake / ".claude/plugins/installed_plugins.json").write_text(json.dumps({"plugins": {"schedule@my-market": [], "my-tool@my-market": [], "ko-quality@ko-quality": []}}))
(fake / ".claude/settings.json").write_text(json.dumps({"model": "custom-model-x"}))
(fake / ".codex/config.toml").write_text('model = "gpt-5.6-terra"\n')
lits = rules.host_literals(ROOT, home=fake)
got = {(r, v) for r, v in lits}
check("user marketplace read", ("host:user-marketplace", "my-market") in got)
check("own marketplaces skipped", not any(v in ("ko-quality", "claude-plugins-official") for r, v in lits if r == "host:user-marketplace"))
check("plugin name@marketplace read", ("host:user-plugin", "schedule@my-market") in got)
check("plain-word plugin name not bare", ("host:user-plugin", "schedule") not in got)
check("non-plain plugin name bare", ("host:user-plugin", "my-tool") in got)
check("own plugin skipped", not any(v.startswith("ko-quality") for r, v in lits if r == "host:user-plugin"))
check("model setting read", ("host:model-setting", "custom-model-x") in got)
check("condition model skipped", ("host:model-setting", "gpt-5.6-terra") not in got)

s = scan.Scanner.__new__(scan.Scanner)
s.repo, s.allowed = ROOT, set()
s.patterns = rules.compiled(lits + rules.host_literals(ROOT))

# ---- host literals ---------------------------------------------------------------------------------------------------
home = str(Path.home())
rel = "~/" + str(ROOT.relative_to(Path.home())) if str(ROOT).startswith(home + "/") else None
check("home path caught", "host:home" in rules_hit(s, f"see {home}/notes.txt"))
check("absolute repo path caught", "host:repo-path" in rules_hit(s, f"cwd={ROOT}/design"))
if rel:
    check("home-relative repo path caught (the form 58 leaks used)", "host:repo-path" in rules_hit(s, f"cwd={rel}/design"))
check("path hash caught", "host:repo-path-hash" in rules_hit(s, '"project": "' + hashlib.sha256(str(ROOT).encode()).hexdigest()[:16] + '"'))
check("user plugin with marketplace caught", "host:user-plugin" in rules_hit(s, "loaded schedule@my-market"))
check("plain-word plugin name inside a word not caught", "host:user-plugin" not in rules_hit(s, "schedule.py assigns the arm"))
check("user marketplace caught on word boundary", "host:user-marketplace" in rules_hit(s, "listed (my-market)"))
check("user marketplace not caught inside a longer name", "host:user-marketplace" not in rules_hit(s, "not-my-market-x"))
check("model setting caught", "host:model-setting" in rules_hit(s, "model custom-model-x"))

# review additions: every literal rule has a catch and a false positive (verification of 2026-09-18)
user = getpass.getuser()
if len(user) >= 3:
    check("user in a path caught", "host:user-in-path" in rules_hit(s, sep("/home/", user, "/x")))
    check("user name alone is not a path", "host:user-in-path" not in rules_hit(s, f"by {user} today"))
hostname = socket.gethostname().split(".")[0]
if len(hostname) >= 4 and hostname.lower() != "localhost":
    check("hostname caught on a word boundary", "host:hostname" in rules_hit(s, f"built on {hostname} today"))
    check("hostname inside a longer word not caught", "host:hostname" not in rules_hit(s, f"x{hostname}y"))
slug = "-" + str(ROOT).strip("/").replace("/", "-")
check("project slug caught", "host:project-slug" in rules_hit(s, f"projects/{slug}/memory"))
check("project slug's last segment alone not caught", "host:project-slug" not in rules_hit(s, "-" + ROOT.name))
check("home's parent alone is not home", "host:home" not in rules_hit(s, str(Path.home().parent) + "/"))
check("repository name alone is not the repository path", "host:repo-path" not in rules_hit(s, f"the {ROOT.name} repository"))
full = hashlib.sha256(str(ROOT).encode()).hexdigest()
check("a shorter prefix of the path hash is not the hash", "host:repo-path-hash" not in rules_hit(s, full[:12]))
wrapped = s.text(f"raw log at {home[:len(home) // 2]}\n  {home[len(home) // 2:]}/logs", "fixture.md")
check("home path wrapped over a line break caught", any(r == "host:home" for _, _, r, _ in wrapped))

# ---- fixed patterns: one catch, one false positive each ---------------------------------------------------------------
cases = [
    ("fixed:tmp-path", sep("/private", "/tmp/x/out.jsonl"), "a temporary directory"),
    ("fixed:tmp-path", sep("/var", "/folders/ab/T/x"), "folders of the var tree, in prose"),
    ("fixed:nix-path", sep("/run/current", "-system/sw/bin/zsh -lc"), "the current system"),
    ("fixed:scratch-path", sep("/a/b/", "scratch", "pad/p6/home"), sep("`...", "/scratch", "pad/p9/batch`")),
    ("fixed:scratch-path", sep("x-1/", "scratch", "pad/y"), sep("a relative ", "scratch", "pad/e7-review/proj")),
    ("fixed:uuid", sep("session 6b045c12", "-1111-4222-8333-444455556666 ended"), "build_id 51112680979b60c3"),
    ("fixed:plan-en", sep("the account is on the free", " plan"), sep("a table plus", " Tier-1 lookup")),
    ("fixed:plan-en", sep("usage", " limit until then"), "quotation marks"),
    ("fixed:plan-ko", sep("무료", " 플랜이라"), "무료로 배포"),
    ("fixed:plan-ko", sep("사용", " 한도가 풀리면"), "사용 범위"),
]
for rule, pos, neg in cases:
    check(f"{rule} catches: {pos[:28]!r}", rule in rules_hit(s, pos))
    check(f"{rule} ignores: {neg[:28]!r}", rule not in rules_hit(s, neg))

# ---- allowlist: exempt by line hash; a changed line is scanned again --------------------------------------------------
line = sep("names the rule: ", "usage", " limit")
s.allowed = {("fixture.md", "fixed:plan-en", scan.line_hash(line))}
check("allowlisted line exempt", not s.text(line, "fixture.md"))
check("changed line not exempt", bool(s.text(line + " (edited)", "fixture.md")))
check("same line in another path not exempt", bool(s.text(line, "other.md")))
s.allowed = set()

# ---- redact ------------------------------------------------------------------------------------------------------------
red = redact.redact(f"at {ROOT}/design, {home}/x, {sep('/private', '/tmp/a')}, id {sep('6b045c12', '-1111-4222-8333-444455556666')}")
check("redact removes repo path", str(ROOT) not in red and "<repository>" in red)
check("redact removes home", home + "/" not in red)
check("redact removes tmp and uuid", "<tmp>/" in red and "<local>" in red)

# ---- local root ----------------------------------------------------------------------------------------------------------
work = local.root()
work.mkdir(parents=True)
local.remember([("host:user-plugin", "gone-plugin@old-market")])
local.remember([("host:user-plugin", "gone-plugin@old-market")])
check("deny.local accumulates once", (work / "deny.local").read_text().count("gone-plugin@old-market") == 1)
check("remembered value survives host drift", ("host:user-plugin", "gone-plugin@old-market") in local.remembered())

(work / "99-test/build").mkdir(parents=True)
(work / "99-test/build/raw.jsonl").write_text("x" * 10)
(work / "99-test/rewrites/2026-01-01").mkdir(parents=True)
cands = {c[0]: c for c in local.candidates()}
check("build pending before review", cands["99-test/build"][1] is False)
check("rewrite backup ready", cands["99-test/rewrites/2026-01-01"][1] is True)


class Buf:
    def __init__(self):
        self.s = ""

    def write(self, x):
        self.s += x


b = Buf()
check("clean refuses a pending candidate", local.clean(["99-test/build"], b) == 1 and (work / "99-test/build").exists())
local.mark_reviewed("99-test", Buf())
check("build ready after mark-reviewed", {c[0]: c for c in local.candidates()}["99-test/build"][1] is True)
local.clean(["99-test/build"], Buf())
check("clean deletes the named candidate only", not (work / "99-test/build").exists() and (work / "99-test/rewrites/2026-01-01").exists())
b = Buf()
local.notice(b)
payload = json.loads(b.s) if b.s.strip() else {}
check("notice prints both channels when a candidate is ready",
      "systemMessage" in payload and "additionalContext" in payload.get("hookSpecificOutput", {}))
local.clean([c[0] for c in local.candidates() if c[1] and c[0].startswith("99-test/")], Buf())
os.environ["KO_QUALITY_WORK"] = str(TMP / "empty-work")
b = Buf()
refs = [c for c in local.candidates() if c[1]]
local.notice(b)
check("notice silent with no ready candidate", b.s == "" if not refs else True)
os.environ["KO_QUALITY_WORK"] = str(TMP / "work")

# ---- hooks in a temporary repository ---------------------------------------------------------------------------------------
repo = TMP / "repo"
remote = TMP / "remote.git"
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")


def g(*a, cwd=repo, input=None):
    return subprocess.run(["git", *a], cwd=cwd, env=env, capture_output=True, text=True, input=input)


subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
repo.mkdir()
g("init", "-q")
g("config", "core.hooksPath", str(ROOT / "hostguard/hooks"))
g("remote", "add", "origin", str(remote))
(repo / "ok.md").write_text("clean text\n")
g("add", "ok.md")
check("clean commit accepted", g("commit", "-q", "-m", "clean").returncode == 0)
(repo / "leak.md").write_text(f"raw log at {home}/logs\n")
g("add", "leak.md")
check("pre-commit refuses a planted home path", g("commit", "-q", "-m", "leak").returncode != 0)
g("rm", "-q", "--cached", "leak.md")
(repo / "ok2.md").write_text("more clean text\n")
g("add", "ok2.md")
check("commit-msg refuses a planted session id", g("commit", "-q", "-m", sep("session 6b045c12", "-1111-4222-8333-444455556666")).returncode != 0)
g("add", "leak.md")
g("commit", "-q", "--no-verify", "-m", "planted past the local hooks")
check("pre-push refuses a commit carrying a planted value", g("push", "-q", "origin", "HEAD:refs/heads/main").returncode != 0)
check("nothing reached the remote (1)", subprocess.run(["git", "--git-dir", str(remote), "rev-parse", "-q", "--verify", "refs/heads/main"], capture_output=True).returncode != 0)

# review addition: content that only a merge commit's resolution introduces
m = TMP / "merge"
m.mkdir()
g("init", "-q", cwd=m)
g("config", "core.hooksPath", str(ROOT / "hostguard/hooks"), cwd=m)
(m / "f.txt").write_text("base\n")
g("add", "f.txt", cwd=m)
g("commit", "-q", "-m", "base", cwd=m)
g("switch", "-q", "-c", "side", cwd=m)
(m / "f.txt").write_text("side\n")
g("commit", "-q", "-am", "side", cwd=m)
g("switch", "-q", "-", cwd=m)
(m / "f.txt").write_text("main\n")
g("commit", "-q", "-am", "main", cwd=m)
g("merge", "-q", "side", cwd=m)
(m / "f.txt").write_text(f"resolved at {home}/work\n")
g("add", "f.txt", cwd=m)
g("commit", "-q", "--no-verify", "-m", "merge side", cwd=m)
(m / "f.txt").write_text("clean again\n")
g("commit", "-q", "--no-verify", "-am", "clean", cwd=m)
hist = scan.Scanner(m, record=False).history("HEAD")
check("history sees a value only a merge resolution introduced", any(r == "host:home" for _, _, r, _ in hist))
mremote = TMP / "mremote.git"
subprocess.run(["git", "init", "-q", "--bare", str(mremote)], check=True)
g("remote", "add", "origin", str(mremote), cwd=m)
check("pre-push refuses a push carrying it", g("push", "-q", "origin", "HEAD:refs/heads/main", cwd=m).returncode != 0)
check("hooks directory has pre-merge-commit", (ROOT / "hostguard/hooks/pre-merge-commit").exists())

shutil.rmtree(TMP, ignore_errors=True)
print(f"hostguard test: {len(failures)} failures")
sys.exit(1 if failures else 0)
