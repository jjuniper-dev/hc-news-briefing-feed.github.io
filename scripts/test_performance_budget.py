#!/usr/bin/env python3
"""File-size performance budget checks for static pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAX_SINGLE_ASSET_KB = 300
MAX_TOTAL_KB = 1500
INCLUDE_EXTENSIONS = {".html", ".css", ".js", ".json"}
SKIP_DIRS = {".git"}

tracked_files: list[Path] = []
for path in ROOT.rglob("*"):
    if path.is_dir():
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    if path.suffix.lower() in INCLUDE_EXTENSIONS:
        tracked_files.append(path)

errors: list[str] = []
total_bytes = 0

for file_path in tracked_files:
    size = file_path.stat().st_size
    total_bytes += size
    if size > MAX_SINGLE_ASSET_KB * 1024:
        errors.append(
            f"{file_path.relative_to(ROOT)} is {size / 1024:.1f} KB (limit {MAX_SINGLE_ASSET_KB} KB)"
        )

total_kb = total_bytes / 1024
if total_kb > MAX_TOTAL_KB:
    errors.append(f"Total tracked asset size {total_kb:.1f} KB exceeds {MAX_TOTAL_KB} KB")

if errors:
    print("Performance budget checks failed:")
    for err in errors:
        print(f"- {err}")
    raise SystemExit(1)

print(f"Performance budget checks passed. Total tracked size: {total_kb:.1f} KB")
