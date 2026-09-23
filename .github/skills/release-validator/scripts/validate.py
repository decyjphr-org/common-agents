#!/usr/bin/env python3
"""Validate a release-validator report.

Usage: python3 validate.py OUTPUT.md

Checks:
- Every markdown checkbox ("- [ ]" / "- [x]") is checked.
- Approval lines name a real approver (not a placeholder like "<name>").
Exits 0 and prints "PASS" if everything checks out, otherwise exits 1 and
prints every failure found.
"""
import re
import sys

CHECKBOX_RE = re.compile(r"^-\s*\[( |x|X)\]\s*(.+)$")
SECTION_RE = re.compile(r"^##\s+(.+)$")
PLACEHOLDER_RE = re.compile(r"<[^>]+>")


def validate(path: str) -> list[str]:
    failures: list[str] = []
    section = "(no section)"

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    checkbox_count = 0
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")

        section_match = SECTION_RE.match(line)
        if section_match:
            section = section_match.group(1).strip()
            continue

        box_match = CHECKBOX_RE.match(line)
        if not box_match:
            continue

        checkbox_count += 1
        checked = box_match.group(1).lower() == "x"
        item_text = box_match.group(2).strip()

        if not checked:
            failures.append(f"[{section}] line {lineno}: unchecked — \"{item_text}\"")
            continue

        if "approved by" in item_text.lower() and PLACEHOLDER_RE.search(item_text):
            failures.append(
                f"[{section}] line {lineno}: checked but approver placeholder "
                f"not filled in — \"{item_text}\""
            )

    if checkbox_count == 0:
        failures.append("No checklist items found — is this a release-validator report?")

    return failures


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 validate.py OUTPUT.md", file=sys.stderr)
        return 2

    path = sys.argv[1]
    try:
        failures = validate(path)
    except FileNotFoundError:
        print(f"FAIL: file not found: {path}", file=sys.stderr)
        return 1

    if failures:
        print(f"FAIL: {len(failures)} issue(s) found in {path}:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"PASS: {path} is complete — all checklist items checked and approved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
