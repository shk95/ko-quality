#!/usr/bin/env python3
"""measure/cost.py (era 98 spec §6, done condition 5). Run: python3 tests/cost_test.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from measure.cost import api_equivalent  # noqa: E402

fails = 0
cases = [
    ("priced model, no cache", api_equivalent("gpt-5.6-terra", 1_000_000, 0, 1_000_000), 14.0),
    ("cached input priced at the cached rate", api_equivalent("gpt-5.6-terra", 1_000_000, 1_000_000, 0), 0.2),
    ("era 02 P2 Codex run, for scale", api_equivalent("gpt-5.6-terra", 83_703, 0, 318), 0.171222),
    ("unpriced model gives None", api_equivalent("no-such-model", 10, 0, 10), None),
]
for name, got, want in cases:
    ok = got == want
    fails += not ok
    print(("ok   " if ok else "FAIL ") + f"{name}: {got}")
print(f"cost test: {fails} failures")
sys.exit(1 if fails else 0)
