---
name: release-validator
description: 'Validate that a software release is ready to ship. Checks functional and regression testing sign-off, security checks, documentation (release notes, changelog, blog posts), remaining release questionnaire items, and required approvals from Product, Marketing, Revenue, and Security. Use when asked to "validate a release", "check release readiness", "run the release checklist", "is this release ready to ship", "generate a release validation report", or "review release questionnaire".'
argument-hint: "Release name/version, or path to an existing release questionnaire to validate"
---

# Release Validator

## When to Use

- Before shipping a release, to confirm every gating requirement is actually met
- When asked to fill out or check a release questionnaire
- When a release report needs sign-off from Product, Marketing, Revenue, and Security before it can go out

## Procedure

1. **Gather status.** Ask the user (or read from context/attached notes) for the current status of each item below. Do not assume something is done — only mark an item complete if the user confirms it or points to evidence (test run link, PR, doc link, approval message).
   - Functional testing complete
   - Regression testing complete
   - Security checks passed
   - Release notes written
   - Changelog updated
   - Blog post(s) drafted/published (if applicable)
   - Remaining release questionnaire items
   - Approvals: Product, Marketing, Revenue, Security

2. **Apply the rules.** Read [release rules](./references/release-rules.md) to determine exactly what counts as "done" and "approved" for each item above before filling in the report — do not accept a vague "yes" for items the rules require evidence for.

3. **Render the report.** Fill in [the release template](./assets/release-template.md) with the gathered status, using `[x]` for complete/approved items and `[ ]` for anything not yet done. Save the completed report to a file (ask the user for a path, or default to `./release-validation-<version>.md` in the workspace).

4. **Validate the output.** Run [scripts/validate.py](./scripts/validate.py) against the saved file:

   ```
   python3 scripts/validate.py OUTPUT
   ```

   Replace `OUTPUT` with the path used in step 3.

5. **Report the result.**
   - If validation fails, stop — do not tell the user the release is ready. Show the exact failures the script printed and what's still needed to fix them.
   - If validation passes, present the completed report and confirm the release is ready to ship.

## Notes

- The four approvals (Product, Marketing, Revenue, Security) are all mandatory; a release is not ready if any one is missing, even if every other item is complete.
- Re-run validation after any correction — don't hand-wave a fix without re-checking the file.
