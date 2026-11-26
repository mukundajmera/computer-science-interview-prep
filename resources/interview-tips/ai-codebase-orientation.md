# 🧭 AI Codebase Orientation

A focused guide for quickly understanding unfamiliar codebases before using AI to edit them.

---

## Orientation goals

- Build a stable mental model of the system before prompting.
- Identify correctness boundaries and extension points.
- Avoid contradictory changes that fight existing architecture.

---

## First 10 minutes

1. Locate entry points and request flow.
2. Identify core domain models and state transitions.
3. Find critical interfaces and invariants.
4. Scan tests for expected behavior and edge cases.
5. Note constraints hidden in comments/configs.

If time is limited, prioritize flow + invariants over line-by-line reading.

---

## Structure-reading sequence

Use this sequence consistently:

1. Runtime entry (`main`, handler/router, scheduler loop).
2. Domain model layer (entities, enums, lifecycle states).
3. Service orchestration layer.
4. Persistence/adapter boundaries.
5. Tests and fixtures.

This sequence minimizes wrong assumptions in subsequent prompts.

---

## AI-assisted orientation

Use AI for acceleration, not delegation of judgment.

High-value prompt examples:
- "Summarize data flow from request entry to persistence in this file."
- "List public interfaces consumed by this class."
- "Highlight potential invariant assumptions in this module."

Guardrails:
- Ask for summaries anchored to visible code.
- Verify each claim by reading source.
- Do not ask AI to redesign architecture during orientation.

---

## Verification checkpoints

Before first implementation prompt, confirm:

- You can explain end-to-end flow in 60-90 seconds.
- You can name at least 2-3 invariants that must not break.
- You know where tests should be added/updated.
- You can state one rollback-safe implementation path.

---

## Pitfalls

- Prompting before locating entry points.
- Misreading domain models and introducing invalid state transitions.
- Editing internals instead of using existing public interfaces.
- Ignoring tests that document intended behavior.

---

## Follow-ups

- "Which part of this codebase is the most likely regression hotspot?"
- "How would your orientation strategy change for a greenfield repo?"
- "What minimal tests would you run before and after each edit phase?"

---

## Variants

- **Structured platform:** focus on codebase constraints and phase pacing.
- **Open-ended BYOE:** focus on architecture scaffolding and test harness setup.
- **Legacy monolith:** prioritize seams, adapters, and risk-limiting edits.

---

## Cross-links

- [AI Coding Interview Playbook](./ai-coding-interview-playbook.md)
- [AI Coding Practice Drills](./ai-coding-practice-drills.md)
- [Common Pitfalls](./common-pitfalls.md)
- [AI Coding Copilot Interview Guide](../../06-genai-systems/02-llm-hld-projects/ai-coding-copilot/INTERVIEW-GUIDE.md)
