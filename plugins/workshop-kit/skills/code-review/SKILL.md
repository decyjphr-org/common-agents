---
name: code-review
description: Reviews committed changes on the current branch against the repository's custom instructions. Use when asked to review a branch, a diff, or changes before a pull request.
---

Review committed changes on this branch. Do not modify files.

1. Find changed files:

   ```bash
   git diff --name-only $(git merge-base main HEAD)...HEAD
   ```

2. Read `.github/copilot-instructions.md` and each `.github/instructions/*.instructions.md`
   file whose `applyTo` pattern matches a changed file.
3. Report, per file: standards violations, security concerns, error handling gaps,
   and possible null or undefined access. Include a suggested fix for each finding.
