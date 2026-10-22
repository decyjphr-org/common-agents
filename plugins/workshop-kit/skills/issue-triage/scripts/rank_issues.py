#!/usr/bin/env python3
"""Rank recently updated open issues using complete GitHub comment histories."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError(f"Timestamp has no timezone: {value!r}")
    return result.astimezone(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def gh_json(arguments: list[str]) -> object:
    result = subprocess.run(
        ["gh", *arguments], check=True, capture_output=True, text=True
    )
    return json.loads(result.stdout)


def records(value: object, context: str) -> list[dict]:
    if not isinstance(value, list) or any(
        not isinstance(item, dict) for item in value
    ):
        raise ValueError(f"Expected a list of objects for {context}")
    return value


def text(record: dict, field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str):
        raise ValueError(f"Expected string field {field!r}")
    return value


def exclusion_reason(issue: dict) -> str:
    labels = records(issue.get("labels"), "issue labels")
    for label in labels:
        name = text(label, "name")
        if name.lower() in {"status-report", "recurring-status-report"}:
            return f"Recurring status-report label: {name}"
    if re.match(
        r"^\s*(daily|weekly|monthly)\s+status\s+report\b",
        text(issue, "title"),
        re.IGNORECASE,
    ):
        return "Recurring status-report title prefix"
    return ""


def fetch_comments(repository: str, number: int) -> list[dict]:
    pages = gh_json(
        ["api", "--paginate", "--slurp", f"repos/{repository}/issues/{number}/comments"]
    )
    if not isinstance(pages, list):
        raise ValueError(f"Expected comment pages for issue {number}")
    comments = []
    for page in pages:
        for comment in records(page, f"issue {number} comments"):
            user = comment.get("user")
            if user is not None and not isinstance(user, dict):
                raise ValueError(f"Invalid comment author for issue {number}")
            comments.append(
                {
                    "author": {"login": text(user, "login")} if user is not None else None,
                    "body": text(comment, "body"),
                    "createdAt": text(comment, "created_at"),
                    "updatedAt": text(comment, "updated_at"),
                    "url": text(comment, "html_url"),
                }
            )
    return comments


def rank_issues(repository: str, now: datetime) -> dict:
    updated_since = now - timedelta(days=30)
    comments_since = now - timedelta(days=7)
    candidates = records(
        gh_json(
            [
                "issue", "list",
                "--repo", repository,
                "--state", "open",
                "--search", f"updated:>={updated_since.date().isoformat()}",
                "--limit", "1000",
                "--json", "number,title,updatedAt,comments,labels,url",
            ]
        ),
        "issues",
    )
    if len(candidates) >= 1000:
        raise ValueError(
            "The 1,000-result GitHub search limit was reached; "
            "cannot guarantee a complete 30-day ranking."
        )

    issues = []
    excluded = []
    candidate_count = 0
    for issue in candidates:
        updated_at = timestamp(text(issue, "updatedAt"))
        if not updated_since <= updated_at <= now:
            continue
        candidate_count += 1
        number = issue.get("number")
        if type(number) is not int or number <= 0:
            raise ValueError("Expected a positive integer issue number")
        text(issue, "title")
        text(issue, "url")
        reason = exclusion_reason(issue)
        if reason:
            excluded.append({"number": number, "reason": reason})
            continue
        comments = fetch_comments(repository, number)
        recent_count = sum(
            comments_since <= timestamp(text(comment, "createdAt")) <= now
            for comment in comments
        )
        stale_seconds = (now - updated_at).total_seconds()
        issues.append(
            {
                **issue,
                "comments": comments,
                "recent_comment_count": recent_count,
                "stale_seconds": stale_seconds,
                "stale_days": round(stale_seconds / 86400, 3),
            }
        )

    issues.sort(
        key=lambda issue: (
            -issue["recent_comment_count"], -issue["stale_seconds"], issue["number"]
        )
    )
    for rank, issue in enumerate(issues, start=1):
        issue["rank"] = rank
    return {
        "repository": f"@{repository}",
        "ranked_at": utc_text(now),
        "updated_since": utc_text(updated_since),
        "comments_since": utc_text(comments_since),
        "candidate_count": candidate_count,
        "excluded": excluded,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="GitHub repository as @owner/repo")
    args = parser.parse_args()
    if not re.fullmatch(r"@[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("repository must have the form @owner/repo")
    try:
        result = rank_issues(args.repository[1:], datetime.now(timezone.utc))
    except FileNotFoundError:
        print("ERROR: GitHub CLI (gh) was not found on PATH.", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(
            f"ERROR: GitHub request failed (exit {error.returncode}): "
            f"{error.stderr.strip()}",
            file=sys.stderr,
        )
        return 1
    except (ValueError, OverflowError) as error:
        print(f"ERROR: Invalid or incomplete GitHub response: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
