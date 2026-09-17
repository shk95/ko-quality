"""The measurement runner (09 §15): reads logs/, joins annotations/, writes derived/. Offline; nothing reaches a model.

  python3 -m measure run --home <KO_QUALITY_HOME> [--report <path>]

Every invocation enforces retention first (09 §20). The runner is the only writer of derived/ (§11.4). Derived records
carry no timestamp, so re-running on unchanged input yields identical files. A derived record whose log record has
expired is kept: derived values never expire.
"""
import hashlib
import json
from pathlib import Path

from measure import derived_fields, exclusion, retention
from measure import measurements as registry

MEASURE_DIR = Path(__file__).resolve().parent


def code_version():
    h = hashlib.sha256()
    for f in sorted(MEASURE_DIR.rglob("*.py")):
        if "__pycache__" not in f.parts and ".venv" not in f.parts:   # the virtualenv lives inside measure/ (P4 V4)
            h.update(str(f.relative_to(MEASURE_DIR)).encode("utf-8") + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def read_jsonl(directory):
    out = []
    if directory.is_dir():
        for f in sorted(directory.glob("*.jsonl")):
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines()):
                if line.strip():
                    out.append((f.stem, json.loads(line)))
    return out


def annotation_index(home):
    """session_id -> annotation; (session_id, turn_key) -> annotation when an annotation names a turn."""
    by_session, by_turn = {}, {}
    for _, a in read_jsonl(Path(home) / "annotations"):
        if a.get("turn_key"):
            by_turn[(a["session_id"], a["turn_key"])] = a
        else:
            by_session[a["session_id"]] = a
    return by_session, by_turn


def join(record, index):
    by_session, by_turn = index
    return by_turn.get((record.get("session_id"), record.get("turn_key"))) or by_session.get(record.get("session_id"))


def derive_record(record, annotation):
    d = {"record_id": record["id"], "exclusion_version": exclusion.version()}
    d.update(derived_fields.derive(record))
    d["features"] = registry.compute(record, annotation)
    return d


def run(home, write=True, today=None):
    home = Path(home)
    report = {"exclusion_version": exclusion.version(), "code_version": code_version()}
    report["retention_deleted"] = retention.enforce(home, today)
    logs = read_jsonl(home / "logs")
    index = annotation_index(home)
    existing = {}
    for month, d in read_jsonl(home / "derived"):
        existing.setdefault(month, []).append(d)
    fresh = {}
    joined = 0
    for month, rec in logs:
        ann = join(rec, index)
        joined += ann is not None
        fresh.setdefault(month, {})[rec["id"]] = derive_record(rec, ann)
    months = sorted(set(existing) | set(fresh))
    written = 0
    for month in months:
        keep = [d for d in existing.get(month, []) if d["record_id"] not in fresh.get(month, {})]
        rows = keep + list(fresh.get(month, {}).values())
        written += len(rows)
        if write and rows:
            p = home / "derived" / f"{month}.jsonl"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    report.update(log_records=len(logs), annotations_joined=joined, derived_records=written,
                  derived_kept_without_log=sum(len([d for d in existing.get(m, []) if d["record_id"] not in fresh.get(m, {})]) for m in months))
    report.update(registry.report(logs, index))
    return report
