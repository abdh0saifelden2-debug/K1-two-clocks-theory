#!/usr/bin/env python3
"""Wording and report-index guard for the paper-facing surface.

Two checks, both fatal in CI:

1. **Retired claim wording.** The manuscript, the README, the docs pages,
   every report linked from ``docs/FINDINGS.md``, and the ``run_*.py`` files
   that write those reports may not reintroduce the phrases removed in the
   v1.0.4 cleanup: unqualified "pre-registered", "decisive", "exactly as
   expected", and "recently-proved".  Scanning the runners keeps the generated
   report text in sync with its generator.
2. **Report index completeness.** Every ``REPORT*.md`` in the checkout must
   appear exactly once in ``docs/REPORTS.md``, and the stated counts must
   match the files on disk.

Exploratory reports outside the FINDINGS link set are indexed but not scanned
for wording: their claims are outside the manuscript's claim set.  The guard
does not judge science; it blocks the specific wording regressions that the
claim map cannot see.

Exit status: 0 clean, 1 findings, 2 the check could not run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FINDINGS = REPO / "docs" / "FINDINGS.md"
INDEX = REPO / "docs" / "REPORTS.md"

# Phrases retired from the paper-facing surface.  Matching is case-insensitive.
FORBIDDEN = {
    "pre-registered": re.compile(r"pre-register", re.IGNORECASE),
    "decisive": re.compile(r"\bdecisive(?:ly)?\b", re.IGNORECASE),
    "exactly as expected": re.compile(r"exactly as expected", re.IGNORECASE),
    "recently-proved": re.compile(r"recently[- ]proved", re.IGNORECASE),
}

REPORT_LINK = re.compile(r"\]\(\.\./(REPORT[^)/]*\.md)\)")
COUNT_LINE = re.compile(r"`(\d+)` files: `(\d+)` `REPORT_\*\.md` plus `REPORT\.md`")
RUNNER_DEFAULT = re.compile(r'--report",\s*default="(REPORT[^"]+\.md)"')


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"check_report_wording: cannot read {path}: {exc}", file=sys.stderr)
        raise SystemExit(2)


def paper_facing() -> list[Path]:
    """The manuscript, its entry points, and the reports FINDINGS links."""
    paths = [
        REPO / "paper0_two_clocks.tex",
        REPO / "README.md",
        REPO / "CLAIM_MAP.md",
        REPO / "REPORT.md",
        REPO / "docs" / "FINDINGS.md",
        REPO / "docs" / "REPORTS.md",
        REPO / "docs" / "REPO_MAP.md",
    ]
    linked = {name for name in REPORT_LINK.findall(read(FINDINGS))}
    for name in sorted(linked):
        path = REPO / name
        if not path.exists():
            print(f"check_report_wording: FINDINGS links missing report {name}", file=sys.stderr)
            raise SystemExit(2)
        if path not in paths:
            paths.append(path)
    return paths


def runner_sources() -> list[Path]:
    """Runners that write a report; scanning them keeps generator text in sync."""
    out = []
    for path in sorted(REPO.glob("run_*.py")):
        if RUNNER_DEFAULT.search(read(path)):
            out.append(path)
    return out


def scan(path: Path) -> int:
    failures = 0
    for lineno, line in enumerate(read(path).splitlines(), 1):
        for label, pattern in FORBIDDEN.items():
            if pattern.search(line):
                print(f"FAIL wording {path.relative_to(REPO)}:{lineno}: {label}")
                failures += 1
    return failures


def check_wording() -> int:
    paths = paper_facing()
    runners = runner_sources()
    failures = sum(scan(path) for path in paths + runners)
    if not failures:
        print(f"ok   wording ({len(paths)} paper-facing files, {len(runners)} runners)")
    return failures


def check_index() -> int:
    actual = sorted(path.name for path in REPO.glob("REPORT*.md"))
    text = read(INDEX)
    listed = REPORT_LINK.findall(text)

    failures = 0
    seen: set[str] = set()
    for name in listed:
        if name in seen:
            print(f"FAIL index docs/REPORTS.md: {name} listed more than once")
            failures += 1
        seen.add(name)
    for name in actual:
        if name not in seen:
            print(f"FAIL index docs/REPORTS.md: missing {name}")
            failures += 1
    for name in sorted(seen - set(actual)):
        print(f"FAIL index docs/REPORTS.md: listed but not on disk: {name}")
        failures += 1

    match = COUNT_LINE.search(text)
    if match is None:
        print("FAIL index docs/REPORTS.md: count line is missing or malformed")
        failures += 1
    else:
        total, reports = int(match.group(1)), int(match.group(2))
        if total != len(actual):
            print(f"FAIL index docs/REPORTS.md: says {total} files, disk has {len(actual)}")
            failures += 1
        if reports != len(actual) - 1:
            print(f"FAIL index docs/REPORTS.md: says {reports} REPORT_*.md, "
                  f"disk has {len(actual) - 1}")
            failures += 1

    if not failures:
        print(f"ok   report index ({len(actual)} files)")
    return failures


def main() -> int:
    failures = check_wording() + check_index()
    if failures:
        print(f"report wording lint: {failures} failure(s)", file=sys.stderr)
        return 1
    print("report wording lint: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
