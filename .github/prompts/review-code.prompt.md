---
description: 'Review code changes against project standards'
agent: 'agent'
---

Review committed changes on this branch. DO NOT modify files.

## Find changes

Use git to find changed files:

```bash
git diff --name-only $(git merge-base main HEAD)...HEAD
```

```powershell
git diff $(git merge-base main HEAD)...HEAD
```

## Standards

Read and apply `.github/copilot-instructions.md` and every
`.github/instructions/*.instructions.md` file in this workspace whose
`applyTo` pattern matches a changed file.

## Focus

- Violations of coding standards
- Security concerns
- Error handling gaps
- Defensive programming: null/undefined access
