#!/usr/bin/env python3
"""Run Phase 1 repository checks with clear pass/fail output."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS: list[tuple[str, list[str]]] = [
    ("Architecture contract", [sys.executable, "scripts/validate_site_architecture.py"]),
    ("Feed health test", [sys.executable, "test_feeds.py"]),
    ("Brief generation", [sys.executable, "generate_latest.py"]),
]


def run_check(name: str, cmd: list[str]) -> int:
    print(f"\n=== {name} ===")
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode == 0:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name} (exit {result.returncode})")
    return result.returncode


def main() -> int:
    failures = 0
    for name, cmd in CHECKS:
        failures += 1 if run_check(name, cmd) != 0 else 0

    if failures:
        print(f"\nPhase 1 checks failed: {failures} check(s) did not pass.")
        return 1

    print("\nAll Phase 1 checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
