"""python3 -m measure run --home <KO_QUALITY_HOME> [--report <path>]
python3 -m measure exclusion-cases [--cases tests/exclusion-cases] [--report <path>]
"""
import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python3 -m measure")
    sub = ap.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="retention, then derived records for every log record")
    r.add_argument("--home", required=True)
    r.add_argument("--report")
    x = sub.add_parser("exclusion-cases", help="false negatives per zone on the labelled set")
    x.add_argument("--cases", default="tests/exclusion-cases")
    x.add_argument("--report")
    args = ap.parse_args(argv)
    if args.command == "run":
        from measure import runner
        out = runner.run(Path(args.home).expanduser())
    else:
        from measure import exclusion_cases
        out = exclusion_cases.evaluate(Path(args.cases))
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
