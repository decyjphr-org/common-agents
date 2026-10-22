# Common Agents

Reusable AI skills, a read-only code-explanation agent, and prompt templates for software engineering workflows. This is a collection of instructions and supporting resources, not a standalone application.

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

The repository includes one agent: [code-explainer](.github/agents/code-explainer.agent.md). It explains repository structure, architecture, domain concepts, build/test/deployment steps, and potential hotspots, grounded in the code. It uses read and search tools only and must not edit code.

In VS Code, choose **code-explainer** from the chat agent picker. In Copilot CLI versions supporting custom agents, use `/agent` and select it. Then ask, for example:

```text
Explain this repository's architecture and key dependencies.
Explain how the scene, parts, and layout modules fit together.
Trace the authentication flow and include a Mermaid diagram.
```

Run these requests in the relevant application workspace. The agent can explain only the code and context it can access.

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
