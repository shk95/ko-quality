"""Read upstream files at any commit from the cached clones (upstream/.cache/<name>@<lock commit>/, full history)."""
import glob
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AnchorNotFound(Exception):
    """An anchor did not resolve to exactly one place in the upstream file."""


def lock():
    """{name: {url, commit, license, roles}} from upstream/lock.yaml."""
    text = (ROOT / "upstream/lock.yaml").read_text(encoding="utf-8")
    out = {}
    for block in text.split("\n- name: ")[1:]:
        name = block.split("\n")[0].strip()
        fields = dict(re.findall(r"^  (\w+): (.*)$", block, re.M))
        out[name] = fields
    return out


def clone(name):
    hits = glob.glob(str(ROOT / f"upstream/.cache/{name}@*"))
    if not hits:
        raise FileNotFoundError(f"no cached clone for {name} under upstream/.cache/")
    return Path(hits[0])


def read(name, path, commit):
    r = subprocess.run(["git", "-C", str(clone(name)), "show", f"{commit}:{path}"],
                       capture_output=True, check=False)
    if r.returncode != 0:
        raise AnchorNotFound(f"{name}@{commit[:8]}: file {path} not found")
    return r.stdout.decode("utf-8")
