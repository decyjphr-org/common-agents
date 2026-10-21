# Attention Scoring

## Candidate Window

Capture one UTC timestamp at the start of a run. Include open issues with
`updatedAt` in the inclusive interval `[now - 30 days, now]`.

Fetch candidates using:

```bash
gh issue list --repo owner/repo --state open --search 'updated:>=YYYY-MM-DD' --limit 1000 --json number,title,updatedAt,comments,labels,url
```

The search date is the UTC date of the cutoff. Apply the exact timestamp window
locally after fetching. GitHub search is limited to 1,000 results, so the script
fails explicitly if 1,000 candidates are returned, rather than silently ranking
an incomplete set. Narrowing the window would change this workflow's scope and
requires user agreement.

## Recurring Status Reports

Skip an issue when either condition holds (case-insensitive):

- It has the exact label `status-report` or `recurring-status-report`.
- Its title starts with `Daily Status Report`, `Weekly Status Report`, or
  `Monthly Status Report`, optionally preceded by whitespace.

Match a word boundary after `Report` so `Weekly Status Reporting` is not excluded.
Do not infer recurrence from an issue's author, body, or unrelated labels.
Include skipped issue numbers and reasons in the output.

## Score and Ordering

The attention score is the ordered pair:

```text
(recent_comment_count, stale_seconds)
```

1. **Hot topics first:** Count comments created in the inclusive interval
   `[now - 7 days, now]`; sort descending by that count. Count human and bot
   comments alike. Editing an old comment does not make it recent.
2. **Stale issues second:** For equal recent-comment counts, sort descending by
   `stale_seconds = now - updatedAt`. Display `stale_days` as fractional days,
   but use full timestamp precision for sorting.
3. **Stable tie-break:** For identical scores, sort by issue number ascending.

This is lexicographic ordering, not a weighted sum: one recent comment always
outranks zero recent comments, regardless of staleness. Among issues with no
recent comments, the oldest update comes first. Staleness is relative only to
the candidate window; issues untouched for more than 30 days are out of scope.

Fetch all comment pages for every eligible candidate with:

```bash
gh api --paginate --slurp repos/owner/repo/issues/NUMBER/comments
```

Do not rely on the embedded comment list from `gh issue list` being complete.
Normalize API comment fields without changing their contents: `user.login` to
`author.login`, `created_at` to `createdAt`, `updated_at` to `updatedAt`, and
`html_url` to `url`. Preserve the body verbatim and unavailable authors as null.
Any failed request or invalid response fails the run explicitly.

## Output Contract

The script prints one JSON object:

- `repository`: `@owner/repo`.
- `ranked_at`, `updated_since`, `comments_since`: UTC ISO timestamps.
- `candidate_count`: issues in the exact 30-day window before exclusions.
- `excluded`: issue numbers and exclusion reasons.
- `issues`: all eligible issues, in ranked order, each containing `rank`,
  `number`, `title`, `updatedAt`, `comments`, `labels`, `url`,
  `recent_comment_count`, `stale_seconds`, and `stale_days`.

The model summarizes only the first 20 entries, preserving their order.
GitHub requests are not an atomic snapshot: activity after `ranked_at` is not
counted as recent, and concurrent updates may require a later fresh run.
