"""Extractors CLI (06 §12 check 1). Run from the repository root:

  python3 -m upstream.extractors extract [--upstream NAME] [--commit SHA]   write upstream/normalized/ (default: lock commits)
  python3 -m upstream.extractors check                                       re-extract at lock commits and compare (exit 1 on failure)
  python3 -m upstream.extractors diff --upstream NAME --commit SHA           re-extract one upstream at another commit, report by anchor
  python3 -m upstream.extractors validate                                    validate committed files against upstream/interface/
"""
import argparse
import sys

from . import fluent_korean, im_not_ai, yoonmoon
from .normalized import load, sha
from .source import ROOT, lock
from .validate import validate_all

MODULES = {"im-not-ai": im_not_ai, "yoonmoon": yoonmoon, "fluent-korean": fluent_korean}
try:
    from . import korean_skills
    MODULES["korean-skills"] = korean_skills
except ImportError:
    pass
NORM = ROOT / "upstream/normalized"


def run(names, commit=None):
    files, failures = {}, []
    for name in names:
        out, fails = MODULES[name].extract(commit or lock()[name]["commit"])
        files.update(out)
        failures += [(name, fid, why) for fid, why in fails]
    return files, failures


def compare(committed_text, fresh_text):
    """By (path, anchor): anchor not found, hash differs, new."""
    _, old = load(committed_text)
    _, new = load(fresh_text)
    new_by = {(f["path"], f["anchor"]): f for f in new}
    old_keys = set()
    missing, changed, added = [], [], []
    for f in old:
        key = (f["path"], f["anchor"]); old_keys.add(key)
        if key not in new_by:
            missing.append(f)
        elif sha(new_by[key]["text"]) != f["content_hash"]:
            changed.append((f, new_by[key]))
        # an id may move while the anchor stays; that is not a failure
    added = [f for k, f in new_by.items() if k not in old_keys]
    return missing, changed, added


def short(text, n=70):
    t = text.replace("\n", " ⏎ ")
    return t if len(t) <= n else t[:n] + "…"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="upstream.extractors")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract"); e.add_argument("--upstream"); e.add_argument("--commit")
    sub.add_parser("check")
    d = sub.add_parser("diff"); d.add_argument("--upstream", required=True); d.add_argument("--commit", required=True)
    sub.add_parser("validate")
    a = ap.parse_args(argv)

    if a.cmd == "extract":
        names = [a.upstream] if a.upstream else list(MODULES)
        files, failures = run(names, a.commit)
        for rel, text in files.items():
            p = NORM / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")
            print(f"wrote upstream/normalized/{rel}")
        for name, fid, why in failures:
            print(f"ANCHOR NOT FOUND {name} {fid}: {why}")
        return 1 if failures else 0

    if a.cmd == "validate":
        errors = validate_all()
        for err in errors:
            print(err)
        print(f"validate: {len(errors)} errors")
        return 1 if errors else 0

    names = [a.upstream] if a.cmd == "diff" else list(MODULES)
    files, failures = run(names, a.commit if a.cmd == "diff" else None)
    bad = 0
    for name, fid, why in failures:
        print(f"ANCHOR NOT FOUND  {name} {fid}: {why}"); bad += 1
    committed = {str(p.relative_to(NORM)): p.read_text(encoding="utf-8") for p in NORM.rglob("*.yaml")}
    for rel in sorted(set(committed) | set(files)):
        if rel not in files:
            if a.cmd == "check":
                print(f"NOT PRODUCED      {rel} (committed file has no extractor output)"); bad += 1
            continue
        if rel not in committed:
            print(f"NEW FILE          {rel}"); continue
        missing, changed, added = compare(committed[rel], files[rel])
        for f in missing:
            print(f"ANCHOR NOT FOUND  {rel} {f['id']}  {f['anchor']}  (committed anchor absent from the extracted commit)"); bad += 1
        for old, new in changed:
            k = next((i for i, (x, y) in enumerate(zip(old["text"], new["text"])) if x != y), min(len(old["text"]), len(new["text"])))
            start = max(0, k - 20)
            print(f"HASH DIFFERS      {rel} {old['id']}  {old['anchor']}  (first difference at char {k})\n"
                  f"    committed: …{short(old['text'][start:])}\n    extracted: …{short(new['text'][start:])}"); bad += 1
        for f in added:
            print(f"NEW FRAGMENT      {rel} {f['id']}  {f['anchor']}  (only in the extracted commit)\n    text: {short(f['text'])}")
        if a.cmd == "check" and committed[rel] != files[rel] and not (missing or changed or added):
            print(f"BYTES DIFFER      {rel} (ids, order or file-level fields; fragments equal)"); bad += 1
    total = sum(len(load(t)[1]) for r, t in files.items())
    print(f"{a.cmd}: {len(files)} files, {total} fragments, {bad} failures")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
