#!/usr/bin/env python3
"""P4 checks for measure/ (10_plan.md P4.2, P4.3): retention on a fixture home, and identical derived records on re-run.
Run from the repository root. Every text here is synthetic."""
import datetime
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from measure import runner  # noqa: E402

TODAY = datetime.date(2026, 9, 17)
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def rec(i, month, task, output):
    return {"id": f"00000000-0000-4000-8000-{i:012d}", "ts": f"{month}-15T00:00:00+00:00", "session_id": f"s-{i}",
            "turn_key": f"t-{i}", "task": task, "output": output, "harness": "claude-code", "harness_position": "main-to-user"}


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as t:
        home = Path(t) / "home"
        ko = "설정 파일을 한 번만 읽도록 `load_config()`를 고쳤습니다. 테스트 12개가 모두 통과했고, 응답 시간도 320ms에서 180ms로 줄었습니다. 다음 배포에서 다시 확인하겠습니다. 문제가 생기면 이전 버전으로 되돌리면 됩니다."
        # 2026-05: last day 05-31, 109 days before TODAY → expired. 2026-06: 06-30, 79 days → current.
        files = {
            "logs/2026-05.jsonl": [rec(1, "2026-05", "고쳐 줘", ko)],
            "logs/2026-06.jsonl": [rec(2, "2026-06", "Fix the loader please", ko), rec(3, "2026-06", "짧게", "네.")],
            "logs/2026-09.jsonl": [rec(4, "2026-09", "상태를 알려 줘", "API 응답은 JSON입니다.")],
            "judge/2026-04.jsonl": [{"text": "copy"}],
            "judge/2026-07.jsonl": [{"text": "copy"}],
            "grader/2026-06.jsonl": [{"text": "copy"}],
            "grader/2026-05.jsonl": [{"text": "copy"}],
            "exports/2025-12.csv": None,
            "derived/2026-01.jsonl": [{"record_id": "old-derived", "exclusion_version": "ex-0", "features": {}}],
            "derived/2026-05.jsonl": [{"record_id": "stale", "exclusion_version": "ex-0", "features": {}}],
            "annotations/2026-01.jsonl": [{"session_id": "s-0", "arm": "A"}],
            "annotations/2026-05.jsonl": [{"session_id": "s-1", "arm": "C", "profile_selected": "agent-reply"}],
            "annotations/2026-06.jsonl": [{"session_id": "s-2", "arm": "B", "stratum": "english", "profile_selected": None},
                                          {"session_id": "s-3", "arm": "C", "stratum": "conversation", "profile_selected": "agent-reply"}],
        }
        for rel, rows in files.items():
            p = home / rel
            if rows is None:
                p.parent.mkdir(parents=True, exist_ok=True); p.write_text("text,copy\n", encoding="utf-8")
            else:
                write_jsonl(p, rows)
        before = sorted(str(p.relative_to(home)) for p in home.rglob("*") if p.is_file())
        report = runner.run(home, today=TODAY)
        after = sorted(str(p.relative_to(home)) for p in home.rglob("*") if p.is_file())
        expected_deleted = sorted(["logs/2026-05.jsonl", "judge/2026-04.jsonl", "grader/2026-05.jsonl", "exports/2025-12.csv"])
        check(sorted(report["retention_deleted"]) == expected_deleted, f"retention deletes exactly the expired text files: {report['retention_deleted']}")
        check(all((home / f).exists() is False for f in expected_deleted), "expired files are gone")
        for kept in ("logs/2026-06.jsonl", "logs/2026-09.jsonl", "judge/2026-07.jsonl", "grader/2026-06.jsonl"):
            check((home / kept).exists(), f"current text file kept: {kept}")
        for kept in ("derived/2026-01.jsonl", "derived/2026-05.jsonl", "annotations/2026-01.jsonl", "annotations/2026-05.jsonl"):
            check((home / kept).exists(), f"never-expiring file kept: {kept}")
        check(set(before) - set(after) == set(expected_deleted), f"nothing else deleted: {sorted(set(before) - set(after))}")
        d05 = [json.loads(l) for l in (home / "derived/2026-05.jsonl").read_text().splitlines()]
        check([d["record_id"] for d in d05] == ["stale"], "a derived record whose log expired is kept")
        d06 = {d["record_id"]: d for d in map(json.loads, (home / "derived/2026-06.jsonl").read_text().splitlines())}
        r2, r3 = d06.get(rec(2, "", "", "")["id"], {}), d06.get(rec(3, "", "", "")["id"], {})
        check(r2.get("instruction_lang") == "en" and r2.get("artifact_lang") == "ko" and r2.get("usable") is True, f"derived fields on record 2: {r2}")
        check(r3.get("instruction_lang") == "ko" and r3.get("usable") is False, f"derived fields on record 3: {r3}")
        check(all(d.get("exclusion_version") == report["exclusion_version"] for d in d06.values()), "exclusion_version on every derived record")
        snapshot = {str(p.relative_to(home)): p.read_bytes() for p in sorted((home / "derived").glob("*.jsonl"))}
        report2 = runner.run(home, today=TODAY)
        again = {str(p.relative_to(home)): p.read_bytes() for p in sorted((home / "derived").glob("*.jsonl"))}
        check(snapshot == again, "re-running on unchanged input yields identical derived files")
        check(report2["retention_deleted"] == [], "second run deletes nothing")
        # 09 §15.6: what every run report carries
        for key in ("exclusion_version", "code_version", "arm_counts", "stratum_counts", "floor_exclusions", "measurements"):
            check(key in report, f"run report carries {key}")
        check(report.get("arm_counts") == {"B": 1, "C": 1, "unannotated": 1}, f"arm counts from joined annotations: {report.get('arm_counts')}")
        check(report.get("stratum_counts") == {"english": 1, "conversation": 1, "unannotated": 1}, f"stratum counts: {report.get('stratum_counts')}")
        check(report.get("annotations_joined") == 2, "two log records join an annotation")
        check(all(m["tier"] in (0, 1, 2) and m["layers"] for m in report.get("measurements", {}).values()), "every measurement declares layer and tier")
        check(all(d.get("features") for d in d06.values()), "derived records carry features")
        # no measurement applies an upstream threshold: thresholds are data only (09 §15.1)
        src = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "measure").rglob("*.py") if ".venv" not in p.parts)
        check("upstream_threshold" not in src, "no measurement code reads upstream_threshold")
        print(json.dumps({"first_run": report, "second_run": report2}, ensure_ascii=False, indent=2))
    for f in failures:
        print("FAIL", f)
    print(f"measure runner test: {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
