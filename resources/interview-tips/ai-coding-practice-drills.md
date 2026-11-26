# 🏋️ AI Coding Practice Drills

Timed drills to build control, verification discipline, and communication in AI-enabled coding interviews.

---

## 45/60-minute drill formats

### 45-minute drill

| Segment | Time | Goal |
|---|---|---|
| Orientation + requirements | 7 min | Build mental model and constraints |
| Plan + prompt sequence | 8 min | Define phased implementation path |
| Implement + verify loop | 22 min | Execute incremental changes with checks |
| Wrap-up + trade-offs | 8 min | Explain decisions and residual risks |

### 60-minute drill

| Segment | Time | Goal |
|---|---|---|
| Orientation + requirements | 10 min | Establish architecture and invariants |
| Plan + prompt sequence | 10 min | Scope implementation phases |
| Implement + verify loop | 30 min | Deliver core path + edge-case handling |
| Wrap-up + follow-ups | 10 min | Communicate extensions and trade-offs |

---

## Structured drills

1. **Bug -> feature -> optimize**
- Phase 1: fix one failing behavior.
- Phase 2: add one new capability.
- Phase 3: improve complexity/latency path.

2. **Constrained tooling rehearsal**
- Use only one AI model and no external docs.
- Goal: improve precision of prompts and verification.

3. **Prompt-budget drill**
- Limit to 8-10 prompts total.
- Goal: force planning quality and reduce noisy prompting.

---

## Open-ended drills

1. **Greenfield contract-first**
- Define interfaces/types and tests before major implementation prompts.

2. **Code-review simulation**
- Treat AI output as a proposed diff; explicitly approve/reject each chunk.

3. **Refactor-under-timebox**
- Start with naive solution and push one targeted refactor with tests.

---

## Self-scoring sheet

Score each dimension 1-5 after every drill:

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Planning clarity |  |  |
| AI control |  |  |
| Verification discipline |  |  |
| Communication cadence |  |  |
| Time management |  |  |

Targets:
- Minimum acceptable average: `3.5`
- Interview-ready target average: `4.2+`

---

## Replay checklist

After each drill, answer:

- Did I set constraints before first prompt?
- Where did I accept AI output too quickly?
- Which verification step caught the most important issue?
- Did I narrate consistently or go silent?
- What one change will improve the next run?

---

## Cross-links

- [AI Coding Interview Playbook](./ai-coding-interview-playbook.md)
- [AI Codebase Orientation](./ai-codebase-orientation.md)
- [Common Pitfalls](./common-pitfalls.md)
- [Communication Guide](./communication-guide.md)
