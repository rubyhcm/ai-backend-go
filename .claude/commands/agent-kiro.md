# Agent Kiro

> **Model:** `claude-opus-4-6`
> Run with: `claude --model claude-opus-4-6` or switch via `/model claude-opus-4-6`

Generate a complete Kiro feature spec (requirements, design, tasks) for the given feature.

## Input

Feature description: $ARGUMENTS

## Instructions

Read and follow the agent prompt at `prompts/agent-kiro.md`.

1. If `$ARGUMENTS` is a `.md` file path, read the file content as the feature description.
2. Read all steering rules in `.kiro/steering/`.
3. Read spec templates in `.kiro/specs/_template/`.
4. Analyze the feature requirement thoroughly — ask no questions, make informed decisions.
5. Generate the spec under `.kiro/specs/<feature-slug>/`:
   - `requirements.md` — user stories, acceptance criteria, business rules
   - `design.md` — domain entities, service interfaces, DB schema, gRPC proto, architecture diagram
   - `tasks.md` — ordered, dependency-aware task breakdown
6. Create report: `reports/<unix_timestamp>_kiro_agent.md`

## Next Steps

```
✅ Spec generated → Copy .kiro/ to your target project and tell Kiro:

  "Implement the <feature-name> feature based on .kiro/specs/<feature-slug>/
   Follow all guidelines in .kiro/steering/. Start with Task 1."
```
