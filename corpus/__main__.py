"""python3 -m corpus run --batch <id> --home <corpus home> --work <scratch dir> [--arms A,B,C] [--per-stratum 3] [--ceiling-usd N] [--spent-usd N] [--only key,...] [--replicates N] [--jobs J]
python3 -m corpus canary --batch <id> --home <canary home> --work <scratch dir> [--mislabel] [--report <path>]
python3 -m corpus summary --progress <batch>.progress.jsonl --out <path>

Commit-safe output (era 98 spec §3): `summary` drops session_id from the progress rows; `canary` keeps its full report in
the work directory and writes --report and stdout through hostguard's redact, session_id replaced by <local>.
"""
import argparse
import json
import sys
from pathlib import Path

from corpus import generator
from hostguard.redact import redact


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python3 -m corpus")
    sub = ap.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="generate a batch: one headless session per (prompt, arm), annotations written per turn")
    r.add_argument("--batch", required=True)
    r.add_argument("--home", required=True)
    r.add_argument("--work", required=True)
    r.add_argument("--arms", default="A,B,C")
    r.add_argument("--prompts", default=str(generator.PROMPTS))
    r.add_argument("--per-stratum", type=int, default=3)
    r.add_argument("--ceiling-usd", type=float)
    r.add_argument("--spent-usd", type=float, default=0.0)
    r.add_argument("--only")
    r.add_argument("--replicates", type=int, default=1, help="rounds over every (prompt, arm) cell")
    r.add_argument("--jobs", type=int, default=1, help="sessions run at once")
    c = sub.add_parser("canary", help="one canary session per arm; reject the batch on a marker in the wrong arm")
    c.add_argument("--batch", required=True)
    c.add_argument("--home", required=True)
    c.add_argument("--work", required=True)
    c.add_argument("--mislabel", action="store_true")
    c.add_argument("--report")
    m = sub.add_parser("summary", help="commit-safe session list from a progress file: every row without session_id")
    m.add_argument("--progress", required=True)
    m.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if args.command == "summary":
        rows = [json.loads(l) for l in Path(args.progress).read_text(encoding="utf-8").splitlines() if l.strip()]
        safe = [{k: v for k, v in r.items() if k != "session_id"} for r in rows]
        Path(args.out).write_text(redact(json.dumps(safe, ensure_ascii=False, indent=1, sort_keys=True)) + "\n", encoding="utf-8")
        print(f"{len(safe)} rows, session_id dropped -> {args.out}")
        return 0
    if args.command == "run":
        progress = generator.run_batch(args.batch, args.home, args.work, tuple(args.arms.split(",")), args.prompts, args.per_stratum,
                                       args.ceiling_usd, args.spent_usd, set(args.only.split(",")) if args.only else None,
                                       args.replicates, args.jobs)
        print(progress)
        return 0
    out = generator.canary(args.batch, args.home, args.work, args.mislabel)
    full = Path(args.work) / f"{args.batch}.canary{'-mislabel' if args.mislabel else ''}.json"
    full.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for run in out["runs"]:
        if run.get("session_id"):
            run["session_id"] = "<local>"
    text = redact(json.dumps(out, ensure_ascii=False, indent=2)) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 1 if out["rejected"] else 0


if __name__ == "__main__":
    sys.exit(main())
