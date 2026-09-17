"""python3 -m measure run --home <KO_QUALITY_HOME> [--report <path>]
python3 -m measure exclusion-cases [--cases tests/exclusion-cases] [--report <path>]
python3 -m measure cases [--cases tests/measure-cases] [--report <path>]
python3 -m measure separation [--cases tests/measure-cases] [--report <path>]
python3 -m measure pilot --home <corpus home> --batch <id> [--prompts corpus/prompts/set-1.json] [--report <path>]
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
    c = sub.add_parser("cases", help="every measurement against its correct and defective cases (09 §17.3)")
    c.add_argument("--cases", default="tests/measure-cases")
    c.add_argument("--report")
    sp = sub.add_parser("separation", help="correct vs telegraphic on the F7 set, beside E2 (10_plan.md P6.1)")
    sp.add_argument("--cases", default="tests/measure-cases")
    sp.add_argument("--report")
    pl = sub.add_parser("pilot", help="pilot report and power calculation for one corpus batch (10_plan.md P8.3-P8.4)")
    pl.add_argument("--home", required=True)
    pl.add_argument("--batch", required=True)
    pl.add_argument("--prompts", default="corpus/prompts/set-1.json")
    pl.add_argument("--report")
    args = ap.parse_args(argv)
    if args.command == "run":
        from measure import runner
        out = runner.run(Path(args.home).expanduser())
    elif args.command == "pilot":
        from measure import pilot
        out = pilot.run(Path(args.home).expanduser(), args.batch, Path(args.prompts))
    elif args.command == "separation":
        from measure import separation
        out = separation.run(Path(args.cases))
    elif args.command == "cases":
        from measure import cases
        out = cases.run(Path(args.cases))
    else:
        from measure import exclusion_cases
        out = exclusion_cases.evaluate(Path(args.cases))
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 1 if out.get("failures") else 0


if __name__ == "__main__":
    sys.exit(main())
