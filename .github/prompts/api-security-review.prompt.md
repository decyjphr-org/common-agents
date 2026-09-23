---
name: "api-security-review"
description: "Perform a REST API security review"
agent: "agent"
tools: [execute, read, edit, search, web, agent, todo]
model: Claude Sonnet 5
argument-hint: "[api-file]"
---

Perform a REST API security review and provide a TODO list of security
issues to address, grouped by priority and issue type.
