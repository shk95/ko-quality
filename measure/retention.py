"""Retention (09 §20): text expires after 90 days, by whole monthly file. Run first in every invocation.

A monthly file is any file named `<yyyy-mm>.<ext>` in a text directory, at any depth (judge and grader copies may nest per run). It is deleted once its month's last day is more than
90 days before today, so text lives 90 to about 120 days. `derived/` and `annotations/` hold no text copy and never expire.
Deletion is automatic and irreversible (user, 2026-09-17). Every deletion is reported.
"""
import calendar
import datetime
import re
from pathlib import Path

RETENTION_DAYS = 90
# every place a copy of task or output text may live under KO_QUALITY_HOME (§20: logs, judge and grader copies, exports)
TEXT_DIRS = ("logs", "judge", "grader", "exports")
NEVER_EXPIRE = ("derived", "annotations")
MONTHLY = re.compile(r"^(\d{4})-(\d{2})\.[A-Za-z0-9]+$")


def last_day(year, month):
    return datetime.date(year, month, calendar.monthrange(year, month)[1])


def expired(name, today):
    m = MONTHLY.match(name)
    if not m:
        return False
    year, month = int(m.group(1)), int(m.group(2))
    if not 1 <= month <= 12:
        return False
    return (today - last_day(year, month)).days > RETENTION_DAYS


def enforce(home, today=None):
    """Delete expired monthly files in every text directory. Returns the deleted paths, relative to home."""
    home, today = Path(home), today or datetime.date.today()
    deleted = []
    for d in TEXT_DIRS:
        base = home / d
        if not base.is_dir():
            continue
        for f in sorted(p for p in base.rglob("*") if p.is_file()):
            if expired(f.name, today):
                f.unlink()
                deleted.append(str(f.relative_to(home)))
    return deleted
