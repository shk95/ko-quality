"""python3 -m corpus run --batch <id> --home <corpus home> --work <scratch dir> [--arms A,B,C] [--per-stratum 3] [--ceiling-usd N] [--spent-usd N] [--only key,...]
python3 -m corpus canary --batch <id> --home <canary home> --work <scratch dir> [--mislabel] [--report <path>]
"""
import argparse
import json
import sys
from pathlib import Path

from corpus import generator


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
    c = sub.add_parser("canary", help="one canary session per arm; reject the batch on a marker in the wrong arm")
    c.add_argument("--batch", required=True)
    c.add_argument("--home", required=True)
    c.add_argument("--work", required=True)
    c.add_argument("--mislabel", action="store_true")
    c.add_argument("--report")
    args = ap.parse_args(argv)
    if args.command == "run":
        progress = generator.run_batch(args.batch, args.home, args.work, tuple(args.arms.split(",")), args.prompts, args.per_stratum,
                                       args.ceiling_usd, args.spent_usd, set(args.only.split(",")) if args.only else None)
        print(progress)
        return 0
    out = generator.canary(args.batch, args.home, args.work, args.mislabel)
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 1 if out["rejected"] else 0


if __name__ == "__main__":
    sys.exit(main())
