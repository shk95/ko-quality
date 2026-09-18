"""python3 -m hostguard <command>   (era 98 spec §2)

  scan --staged | --message FILE | --push | --history [REF] | --text FILE...   exit 1 on a host-state hit
  allow PATH LINE REASON        print the allow.tsv line for a false positive at PATH:LINE (add it yourself)
  status                        deletion candidates in the local root; nothing is deleted
  clean ID...                   delete exactly the named ready candidates
  mark-reviewed ERA             the era's review has closed; its build material becomes a candidate
  notice                        SessionStart hook output (silent with no ready candidate)
  redact                        stdin to stdout with host values replaced by placeholders
"""
import subprocess
import sys
from pathlib import Path

from hostguard import local, redact, scan


def main(argv):
    if not argv:
        sys.stdout.write(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    if cmd == "scan":
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
        s = scan.Scanner(top or ".")
        if args[:1] == ["--staged"]:
            hits = s.staged()
        elif args[:1] == ["--message"]:
            hits = s.message(Path(args[1]).read_text(encoding="utf-8"))
        elif args[:1] == ["--push"]:
            hits = s.push(sys.stdin.read().splitlines())
        elif args[:1] == ["--history"]:
            hits = s.history(args[1] if len(args) > 1 else "HEAD")
        elif args[:1] == ["--text"]:
            hits = [h for f in args[1:] for h in s.text(Path(f).read_text(encoding="utf-8"), f)]
        else:
            sys.stdout.write(__doc__)
            return 2
        return scan.report(hits, sys.stdout)
    if cmd == "allow" and len(args) >= 3:
        path, n, reason = args[0], int(args[1]), " ".join(args[2:])
        line = Path(path).read_text(encoding="utf-8").splitlines()[n - 1]
        hits = scan.Scanner(record=False).text(line, path)
        for _, _, rule, _ in hits:
            sys.stdout.write(f"{path}\t{rule}\t{scan.line_hash(line)}\t{reason}\n")
        return 0 if hits else 1
    if cmd == "status":
        return local.status()
    if cmd == "clean" and args:
        return local.clean(args)
    if cmd == "mark-reviewed" and len(args) == 1:
        return local.mark_reviewed(args[0])
    if cmd == "notice":
        return local.notice()
    if cmd == "redact":
        sys.stdout.write(redact.redact(sys.stdin.read()))
        return 0
    sys.stdout.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
