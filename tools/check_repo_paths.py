#!/usr/bin/env python3
"""Repository path guard.

Two checks, both fatal in CI:

1. **Old monorepo prefix.** No tracked file may reference the pre-split
   ``general_two_clocks/`` prefix. Those paths do not exist after the split, so
   any command, inline code span, or link that keeps the prefix is broken.
   ``AUDIT.md`` is exempt: it documents the pre-split provenance on purpose.

2. **Relative Markdown links.** Every relative link in ``README.md`` and
   ``docs/*.md`` must resolve to a file or directory in the checkout. Absolute
   URLs, anchor-only links, and ``mailto:`` are skipped.

The prefix is assembled at runtime so this file does not trip its own check.
Exit status: 0 clean, 1 findings, 2 the check could not run.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parent.parent

TOKEN = "general_two_" + "clocks"

# Files allowed to keep the historical prefix, with the reason.
HISTORICAL = {
    "AUDIT.md",  # records where the split files came from
}

# The guard itself names the prefix in its documentation.
SELF = "tools/check_repo_paths.py"

TEXT_SUFFIXES = {
    ".cfg", ".ini", ".json", ".md", ".py", ".sh", ".tex",
    ".toml", ".txt", ".yaml", ".yml",
}

COMMAND_RE = re.compile(r"\b(?:python3?|pytest|cd)\b[^\n]*" + re.escape(TOKEN))
LINK_RE = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def tracked_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=REPO,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"check_repo_paths: cannot list tracked files: {exc}", file=sys.stderr)
        raise SystemExit(2)
    return [p for p in out.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def read_text(path: Path) -> str | None:
    """Return decoded text, or None for binary/unreadable files."""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw[:8192]:
        return None
    return raw.decode("utf-8", "replace")


def classify(line: str) -> str:
    if COMMAND_RE.search(line):
        return "command"
    if "](" in line and TOKEN in line.split("](", 1)[1]:
        return "link"
    if "`" in line:
        return "inline code"
    return "reference"


def check_old_prefix(files: list[str]) -> list[str]:
    findings = []
    for rel in files:
        if rel in HISTORICAL or rel == SELF:
            continue
        if Path(rel).suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = read_text(REPO / rel)
        if text is None or TOKEN not in text:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if TOKEN in line:
                findings.append(
                    f"{rel}:{lineno}: [{classify(line)}] {line.strip()[:160]}"
                )
    return findings


def check_links(files: list[str]) -> list[str]:
    tracked = set(files)
    docs = [rel for rel in ("README.md",) if rel in tracked]
    docs += sorted(
        rel for rel in files
        if rel.startswith("docs/") and rel.endswith(".md")
    )
    findings = []
    for rel in docs:
        text = read_text(REPO / rel)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in LINK_RE.finditer(line):
                target = match.group(1).strip()
                if not target or target.startswith("#") or target.startswith("//"):
                    continue
                if SCHEME_RE.match(target):
                    continue
                target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not target:
                    continue
                if not (REPO / rel).parent.joinpath(target).exists():
                    findings.append(
                        f"{rel}:{lineno}: [link] missing target {match.group(1)!r}"
                    )
    return findings


def main() -> int:
    files = tracked_files()
    findings = check_old_prefix(files) + check_links(files)

    if findings:
        print(f"check_repo_paths: {len(findings)} finding(s)\n", file=sys.stderr)
        for item in findings:
            print(f"  ERROR {item}", file=sys.stderr)
        print(
            "\nFix the reference. If it is historical, add the file to HISTORICAL "
            "in tools/check_repo_paths.py with a reason.",
            file=sys.stderr,
        )
        return 1

    print(
        f"check_repo_paths: OK - no stale {TOKEN} references in {len(files)} "
        "tracked files; README/docs relative links resolve."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
