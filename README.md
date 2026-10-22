# Common Agents

Reusable AI skills, a coordinated agent workflow, and prompt templates for software engineering workflows. This is a collection of instructions and supporting resources, not a standalone application.

## Get started

1. Clone the repository:

   ```bash
   git clone https://github.com/decyjphr-org/common-agents.git
   cd common-agents
   ```

2. Open it in a client that supports repository skills and custom agents, such as a compatible version of GitHub Copilot in VS Code or Copilot CLI. For the Claude-oriented skill, use a client that discovers `.claude/skills/`.
3. Select an agent or invoke a skill as described below. Most workflows should run in the project you want to analyze or change, not in this collection.

To use these resources in another project, copy the selected skill folders into that project's `.github/skills/` or `.claude/skills/`, and the selected agent files into `.github/agents/`. Copy prompt files into `.github/prompts/` for use in VS Code. Preserve each skill's entire folder: its instructions may depend on bundled scripts, templates, or references. Review existing files before copying; do not overwrite project-specific configuration.

Discovery, slash commands, and tool availability vary by client and version. If an item does not appear, check the client's support for its directory and file format. Merely cloning this repository does not install its contents globally.

## Skills

A skill is a task-specific workflow defined in a `SKILL.md` file. Compatible clients can load a skill when your request matches its description. Where skill slash commands are supported, invoke one explicitly:

```text
/code-review Review the committed changes on this branch.
/issue-triage @owner/repo
/release-validator Check release v1.0.0.
/visualize Explain the checkout flow with diagrams.
```

Alternatively, ask directly: "Use the code-review skill to review this branch." Include the target repository, folder, file, or release and any required evidence.

### Available skills

| Skill | Use it for | Inputs and important constraints |
| --- | --- | --- |
| [area-instructions](.github/skills/area-instructions/SKILL.md) | Generate concise instructions for one codebase area. | Provide the area and matching file patterns; complements rather than repeats root instructions. |
| [code-review](.github/skills/code-review/SKILL.md) | Review committed branch changes against repository standards. | Requires Git and a `main` merge base; reads root and matching area instructions. Reports findings without modifying files. |
| [html-in-canvas](.github/skills/html-in-canvas/SKILL.md) | Build live HTML UI rendered into canvas, WebGL, or WebGPU. | Describe the rendering target; uses experimental browser APIs and requires feature detection and a visible fallback. |
| [issue-triage](.github/skills/issue-triage/SKILL.md) | Rank recently updated open issues and summarize the top 20. | Provide `@owner/repo`; requires Python 3.9+ and authenticated GitHub CLI with `gh api --slurp` support. Does not modify issues. |
| [js-to-typescript](.claude/skills/js-to-typescript/SKILL.md) | Migrate JavaScript applications or files to TypeScript. | Provide the migration scope; includes assessment, strict typing, and project-specific build/test checks. Located under `.claude/skills/`. |
| [nested-detail](.github/skills/nested-detail/SKILL.md) | Generate deep-dive instructions for a specific topic. | Provide the topic and repository or area; uses patterns from the actual codebase. |
| [nested-hub](.github/skills/nested-hub/SKILL.md) | Generate a lean `AGENTS.md` hub. | Provide the repository or area and existing root context; recommends 3-5 detail topics. |
| [release-validator](.github/skills/release-validator/SKILL.md) | Produce and validate a release-readiness report. | Provide a release version, test/security evidence, documentation status, questionnaire answers, and named approvals from all four required teams. |
| [root-instructions](.github/skills/root-instructions/SKILL.md) | Generate `.github/copilot-instructions.md`. | Run against the target codebase to capture its stack, structure, commands, and conventions. |
| [visualize](.github/skills/visualize/SKILL.md) | Explain code logic and data flow visually. | Provide code or a target flow; produces Mermaid sequence, entity-relationship, and data-flow diagrams with explanations. |

The four instruction-generation skills (`root-instructions`, `area-instructions`, `nested-hub`, and `nested-detail`) explicitly require an `emit_file_content` tool. Use them in a host that exposes that tool; they are not guaranteed to work unchanged in every chat client. The root workflow also calls for exploration subagents.

### Release validation

The release workflow gathers evidence, applies the [release rules](.github/skills/release-validator/references/release-rules.md), and saves a report using the [template](.github/skills/release-validator/assets/release-template.md). Its default output is `release-validation-<version>.md` in the workspace.

From this repository's root, validate an existing report with:

```bash
python3 .github/skills/release-validator/scripts/validate.py release-validation-v1.0.0.md
```

The script exits with `0` on success and `1` for an incomplete report. It checks that all existing checklist items are checked and rejects angle-bracket approver placeholders on checked approval lines. It does **not** verify evidence, enforce the presence of every required section, or authenticate approvals. Apply the release rules as well: Product, Marketing, Revenue, and Security must each have a named approver, and passing security scans is not a substitute for Security approval.

### Issue triage

For the complete workflow, invoke `issue-triage` with a repository. To run only the ranking step from this repository's root:

```bash
gh auth login
python3 .github/skills/issue-triage/scripts/rank_issues.py '@owner/repo'
```

Replace `owner/repo` with the target repository. The script prints ranked JSON, not the final narrative summary. The skill then investigates up to 20 issues in that exact order and uses the [summary template](.github/skills/issue-triage/assets/summary-template.md). Recurring status reports are excluded. The Python scripts use the standard library; no third-party Python packages are required.

## Agents

A custom agent defines a persistent role and tool boundary for a conversation; a skill supplies a workflow for a particular task.

Choose **coordinator** in the VS Code chat agent picker, or use `/agent` in a compatible Copilot CLI and select it. Give it a concrete task, target paths, constraints, and acceptance criteria:

```text
Plan a fix for duplicate checkout submissions in src/checkout.
Preserve the public API and add a focused regression test.
Do not implement until I approve the consolidated plan.
```

### Coordinated workflow

```text
Coordinator
 +-- Researcher (code-explainer) --+
 +-- Security -------------------+--> Consolidated plan
 +-- Architect ------------------+          |
                                      Human approval
                                           |
                                      Implementer
                                           |
                                   Read-only Reviewer
```

The coordinator fans out only independent analysis questions. When architecture or security depends on research or a proposed design, that analysis waits for its prerequisite. Implementation and review are sequential, not parallel.

| Agent | Receives | Must return | Tools |
| --- | --- | --- | --- |
| [coordinator](.github/agents/coordinator.agent.md) | User goal, target scope, constraints, and acceptance criteria. | Versioned consolidated plan; approval request; final changes, validation evidence, review verdict, and blockers. | Read, search, delegate only to the five listed workers. |
| [code-explainer (Researcher)](.github/agents/code-explainer.agent.md) | Bounded research question and scoped context. | Source-grounded behavior, affected areas, validation guidance, and unknowns. | Read and search only. |
| [security](.github/agents/security.agent.md) | Bounded security question and available prerequisite findings. | Evidence-backed threats, mitigations, acceptance checks, and residual risks. | Read and search only. |
| [architect](.github/agents/architect.agent.md) | Design question, constraints, and completed prerequisites where needed. | Minimal design, alternatives, ordered steps, validation/rollback guidance, and open decisions. | Read and search only. |
| [implementer](.github/agents/implementer.agent.md) | Exact approved plan/version, human approval, allowed paths, and acceptance criteria. | Change inventory, acceptance evidence, actual validation results, and review handoff. | Read, search, edit, and execute. |
| [reviewer](.github/agents/reviewer.agent.md) | Approved plan, implementation changes, before/after evidence, and validation results. | `accepted`, `changes-required`, or `blocked`, with actionable findings and verification limits. | Read and search only. |

Each worker file defines its full input/output contract and boundaries. Workers have `user-invocable: false` and are hidden from the picker; the coordinator delegates to them by name. The existing code-explainer is reused as the Researcher rather than duplicated. Implementer and Reviewer set `include-custom-instructions: true` so repository custom instructions are included when they run as subagents.

The coordinator must present a plan such as `P1`, ask for explicit approval of that version, and stop. Reply with an approval such as `Approve P1` or request revisions. A material plan change requires a new approval. Only the Implementer can edit or execute commands; review findings return to it for in-scope fixes and another read-only review.

Use a client supporting the `agents`, `user-invocable`, and `include-custom-instructions` fields and subagent delegation. These files define an instruction-level approval gate, not an external access-control mechanism: keep client tool permissions enabled and do not assume that hiding a worker removes its capabilities.

### VS Code and Copilot CLI

Both clients are intended targets for the same six workflow files; no client-specific copies are maintained. Runtime compatibility has not yet been verified, and no minimum supported version has been established.

| Client | Setup and launch | Verify before use |
| --- | --- | --- |
| VS Code with GitHub Copilot | Open the target project containing `.github/agents/`, then select **coordinator** in Chat. | Custom-agent discovery, named subagent delegation, worker visibility, allowed tools, and repository-instruction inclusion. |
| GitHub Copilot CLI | Start `copilot` from the target project, run `/agent`, and select **coordinator**. | The same capabilities, including how this CLI version handles each frontmatter field. |

Do not assume a client enforces a field simply because it loads the file. If any required capability is unsupported, stop using the workflow in that client until it is supported or explicitly adapted; do not broaden worker tools as a workaround.

For each client, run this smoke test in a disposable project with no unrelated changes:

1. Confirm the coordinator is selectable and the five workers are hidden. Unrelated standalone agents may still appear.
2. Request a small documentation change with an explicit acceptance criterion. Inspect delegation activity: independent questions may overlap, dependent questions must wait, and analysis workers must have only read/search tools.
3. Confirm a versioned consolidated plan is presented and no files change before a subsequent explicit approval. Request a revision and confirm the revised plan requires its own approval.
4. Approve the current version. Confirm implementation occurs only afterward and review starts only when implementation stops.
5. Use a harmless, distinctive repository instruction in the disposable project and verify both Implementer and Reviewer receive it. Check tool availability as well as worker-reported compliance.
6. Confirm the Reviewer cannot edit or execute and returns a verdict grounded in the actual changes. Record each client's version and observed results before treating it as verified.

The independent [readme-specialist](.github/agents/readme-specialist.agent.md) agent remains available for README/supporting documentation work with read, search, and edit tools; it is not part of the coordinator's delegation list.

Run the workflow in the relevant application workspace, with all six workflow agent files installed together. Agents can inspect only the code and context they can access.

## Prompt templates

The files in [`.github/prompts/`](.github/prompts/) are reusable prompts, separate from skills and agents. In VS Code versions supporting prompt files, invoke a supported template by its slash-command name or select it through the prompt picker.

| Prompt | Purpose | Notes |
| --- | --- | --- |
| [1-1-meeting-agenda](.github/prompts/1-1-meeting-agenda.prompt.md) | Draft a meeting agenda from Daily notes. | Supply a date range and make the relevant notes available. |
| [api-security-review](.github/prompts/api-security-review.prompt.md) | Produce prioritized REST API security findings. | Supply an API file; declares a specific model (`Claude Sonnet 5`) and tool set, which must be available or adjusted for your environment. |
| [issues-summarizer](.github/prompts/issues-summarizer.prompt.md) | Summarize the top 20 active issues and their comments. | Supply `@owner/repo`; use the `issue-triage` skill when deterministic ranking and its exclusion rules are required. |
| [review-code](.github/prompts/review-code.prompt.md) | Review committed changes against project instructions. | Requires a `main` merge base; explicitly forbids file modifications. |
| [analyze-zendesk](.github/prompts/analyze-zendesk.prompt.md) | Reference text for analyzing a Zendesk ticket. | Explicitly marked **not for Copilot Chat**; use as a reference in Zendesk instead. |

## Repository layout

```text
.github/
  agents/             Custom agent definitions (*.agent.md)
  prompts/            Reusable prompt templates (*.prompt.md)
  skills/             Skill folders, each containing SKILL.md
    <skill>/
      assets/         Templates or example files, when provided
      references/     Detailed rules and guidance, when provided
      scripts/        Supporting utilities, when provided
.claude/
  skills/
    js-to-typescript/ TypeScript migration workflow
```

## Adding or adapting resources

Follow the format of a nearby resource: a skill folder with `SKILL.md`, an agent file with the `.agent.md` suffix, or a prompt file with the `.prompt.md` suffix. Give it a clear description, specify required inputs and tools, and keep supporting paths relative to its location.

Test the workflow in its intended client and target project. Review generated files and suggested commands before applying them; client permissions, available tools, project instructions, and access to external services determine what a workflow can actually do.
