# Release Rules

Detailed criteria for each item in the release validation report. An item is only "complete" if it meets its criteria below — not merely mentioned as done.

## Functional Testing
- All planned test cases for the release scope have been executed.
- No open severity-1 or severity-2 defects remain from functional test runs.
- Evidence: link to the test run, test suite report, or QA sign-off.

## Regression Testing
- Full (or scoped, if explicitly agreed with QA) regression suite has been run against the release candidate build.
- No new regressions introduced relative to the previous release.
- Evidence: link to the regression run/report.

## Security Checks
- Static/dependency scanning (e.g., code scanning, secret scanning, dependency review) has completed with no unresolved critical or high findings.
- Any accepted-risk findings are explicitly documented with a named approver.
- Evidence: link to the security scan results or security team sign-off.

## Documentation
- **Release notes**: written, cover all user-facing changes, and reviewed.
- **Changelog**: updated with entries matching the release notes.
- **Blog post(s)**: drafted (and published, if the release requires external announcement); not required for internal-only or patch releases unless specified.

## Release Questionnaire
- All remaining questions in the org's standard release questionnaire (rollout plan, rollback plan, support readiness, feature flag state, telemetry/monitoring in place) are answered.
- No question is left blank or marked "TBD".

## Approvals
All four approvals are required before a release can ship. An approval is only valid if it names an approver (not just a checked box):
- **Product**: confirms scope and readiness from a product perspective.
- **Marketing**: confirms external messaging/announcement plan is ready (or explicitly not needed).
- **Revenue**: confirms pricing/packaging/billing impact has been reviewed (or explicitly not applicable).
- **Security**: confirms security checks above have been reviewed and accepted.

A release is **not ready** if any single approval is missing, even if every other section is complete.
