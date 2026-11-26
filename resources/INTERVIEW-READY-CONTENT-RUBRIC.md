# Interview-Ready Content Rubric

This rubric defines when a topic is good enough for a learner to read, rehearse, and use in an interview without needing to invent missing details.

## Readiness Levels

| Score | Status | Meaning |
|---:|---|---|
| 0-2 | `missing` | Topic or required artifact does not exist. |
| 3-4 | `thin` | Has headings or overview but lacks concrete interview transfer. |
| 5-6 | `in-progress` | Useful, but missing examples, failure handling, rubric, or cross-links. |
| 7-8 | `review-ready` | Rehearsable with minor gaps; ready for five read-check rounds. |
| 9 | `validated` | Passes deterministic checks and human review for its current scope. |
| 10 | `complete` | Interview-ready, linked, validated, and tracked across portal/practice assets. |

## Universal Required Signals

Every completed topic must include:

- Mental model: one concise explanation of what the concept/problem is.
- Recognition cues: how to identify when it applies in an interview.
- Concrete example: API, state transition, dry run, scenario, or code-shaped walkthrough.
- Approach: step-by-step solving/design path.
- Trade-offs: explicit choices, alternatives, and why the chosen path fits.
- Failure modes: correctness, scaling, operational, abuse, or edge-case risks.
- Pitfalls: common wrong answers and how to avoid them.
- Follow-ups: realistic interviewer questions.
- Strong answer: a 60-90 second opening or wrap-up a candidate can say aloud.
- Rubric: how the answer is scored.
- Cross-links: prerequisites, related topics, quiz, flashcards, solution, or project links.

## HLD Concept Contract

Required artifacts:

- `README.md` or `THEORY.md`
- `INTERVIEW-QA.md` for concepts that commonly appear as standalone interview follow-ups

Required content:

- Problem it solves and when it is a bad fit.
- Design knobs and selection criteria.
- Failure modes and observability signals.
- Security/privacy/cost notes when relevant.
- Interview score rubric and follow-up questions.

## HLD Project Contract

Required artifacts:

- `PROBLEM.md`
- `APPROACH.md`
- `DESIGN.md`
- `RUBRIC.md`
- `PITFALLS.md`
- `FOLLOW-UPS.md`
- `COMPARISON.md`
- `STRONG-ANSWER.md`

Required content:

- Concrete functional and non-functional requirements with numbers.
- Back-of-envelope estimates that affect architecture.
- API request/response/error contracts.
- Data model with keys, indexes, and retention notes.
- Read path, write path, failure path, and recovery path.
- Deep dives for the hardest correctness or scale risks.
- Observability, rollout, and rollback notes.

## LLD Project Contract

Required artifacts:

- `PROBLEM.md`
- `APPROACH.md`
- `DESIGN.md`
- `CODE-WALKTHROUGH.md`
- `RUBRIC.md`
- `PITFALLS.md`
- `FOLLOW-UPS.md`
- Java and Python implementation folders when the local AGENTS contract requires parity

Required content:

- Public API and object responsibilities.
- Invariants and state transitions.
- Edge cases and validation behavior.
- Concurrency/testability notes when relevant.
- Version progression from `v1-basic` to deeper variants.
- Tests for main behavior and important edge cases.

## Coding Pattern Contract

Required content:

- Pattern recognition cues.
- Window/invariant/state definition.
- Language-neutral algorithm.
- Dry run on a representative example.
- Complexity proof.
- Pitfalls and follow-ups.
- Links to quiz, flashcards, and coach answer where available.

## GenAI Contract

Required content:

- Architecture first, dated product examples second.
- Model, retrieval, routing, evaluation, safety, cost, latency, and freshness dimensions.
- Failure modes: hallucination, stale context, prompt injection, leakage, eval drift, cost spikes.
- When not to use GenAI or RAG.
- Currentness note when naming fast-moving products or APIs.

## Five Read-Check Gate

No batch can be marked `complete` until these checks are recorded:

1. Contract/readiness check.
2. Coverage/matrix check.
3. Readability/interview-transfer check.
4. Validation/portal/static-export check.
5. Risk/provenance/diff check.
