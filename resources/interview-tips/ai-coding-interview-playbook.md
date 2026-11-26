# 🤖 AI Coding Interview Playbook

A practical guide for AI-enabled coding interviews where you must stay in control of decisions while using AI as an accelerator.

---

## Overview

AI-enabled coding rounds evaluate four things repeatedly: solution judgment, control over AI output, verification discipline, and communication clarity. The strongest candidates do not optimize for prompt cleverness. They optimize for direction, correctness, and explainability.

---

## Requirements and constraints

Before writing prompts, align on:

- Problem scope: bug fix, feature addition, refactor, or optimization.
- Environment constraints: allowed tools, language requirements, starter code, and banned libraries.
- Performance constraints: expected time complexity, memory ceilings, latency goals.
- Delivery constraints: timebox, expected phases, and what "done" means.
- Verification constraints: what tests exist, what must be added, and how success is measured.

A reliable opening line:

> "I’ll confirm requirements and constraints first, then propose a phased plan before using AI for implementation."

---

## Interview formats

### Structured (platform-based)

Typical traits:
- Hosted environment (for example, CoderPad/HackerRank-like workflow).
- Pre-seeded codebase and multi-phase tasks.
- Limited AI controls and fixed tooling.

Execution posture:
- Spend initial minutes on codebase orientation before any prompt.
- Keep prompts small and phase-specific.
- Narrate each change and why it matches existing architecture.

### Open-ended (BYOE)

Typical traits:
- Your IDE and tooling.
- Greenfield or lightly scaffolded problem.
- Workflow quality is fully visible.

Execution posture:
- Establish structure early (interfaces, invariants, test strategy).
- Keep prompt history disciplined and explainable.
- Validate continuously to avoid drift.

---

## Scoring rubric

| Dimension | Strong signal |
|---|---|
| Problem-solving and approach | Clear phased plan, prioritization, and trade-off awareness before coding |
| Control over AI | You direct architecture and accept/reject output intentionally |
| Verification habits | You test and inspect every major AI-generated change |
| Communication | You narrate intent, changes, and risks without going silent |

Use this quick self-score after each mock:
- `5`: Consistently demonstrated.
- `3`: Partially demonstrated.
- `1`: Mostly missing.

---

## Common pitfalls

1. **Planless prompting**
- Symptom: dumping the whole problem into AI immediately.
- Fix: state phased plan first, then prompt per phase.

2. **Passive AI acceptance**
- Symptom: accepting architecture or code without critical review.
- Fix: ask "does this align with constraints and existing patterns?" before accepting.

3. **Unverified edits**
- Symptom: moving forward without tests or walkthrough.
- Fix: run/inspect after every meaningful change.

4. **Silent execution**
- Symptom: long quiet stretches while prompting.
- Fix: narrate intent and checkpoints every few minutes.

---

## Follow-up questions

- "How would you adapt this if the platform AI quality degrades mid-round?"
- "What would you change if this became a two-hour take-home?"
- "Which part of your approach is most sensitive to incorrect AI output?"
- "How would you reduce risk if you had to skip one implementation phase?"
- "What would you monitor in production for this solution?"

---

## Variants and extensions

- **Bug-fix-first format:** Prioritize root-cause trace, then patch, then regression test.
- **Feature + optimization format:** Deliver correct feature first, then tune hot paths.
- **Greenfield format:** Define contracts and invariants before implementation prompts.
- **Review-driven format:** Treat AI output as a draft PR; explain approve/request-changes decisions.

---

## Cross-links

- [AI Codebase Orientation](./ai-codebase-orientation.md)
- [AI Coding Practice Drills](./ai-coding-practice-drills.md)
- [LLD Checklist](./lld-checklist.md)
- [HLD Checklist](./hld-checklist.md)
- [Communication Guide](./communication-guide.md)
- [Common Pitfalls](./common-pitfalls.md)
- [AI Coding Copilot Interview Guide](../../06-genai-systems/02-llm-hld-projects/ai-coding-copilot/INTERVIEW-GUIDE.md)
