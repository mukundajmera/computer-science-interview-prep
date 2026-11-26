# HLD Project Pack Template

Create these files for a complete HLD project pack:

- `PROBLEM.md`
- `APPROACH.md`
- `DESIGN.md`
- `RUBRIC.md`
- `PITFALLS.md`
- `FOLLOW-UPS.md`
- `COMPARISON.md`
- `STRONG-ANSWER.md`

## Required Problem Sections

- Concrete problem statement.
- Functional requirements with explicit scope.
- Non-functional requirements with target numbers.
- Constraints and out-of-scope items.
- API/system interface sketch.
- Key design challenges.
- Related links.

## Required Design Sections

- Back-of-envelope estimates that affect architecture.
- API request/response/error examples.
- Data model with keys, indexes, retention, and consistency.
- High-level architecture.
- Write path.
- Read path.
- Failure/recovery path.
- Deep dives.
- Trade-offs.
- Rollout and observability.

## Required Strong Answer

Provide a time-boxed verbal script:

- 0-5 min: requirements and assumptions.
- 5-10 min: estimates.
- 10-20 min: API and data model.
- 20-35 min: architecture and paths.
- 35-42 min: deep dives.
- 42-45 min: wrap-up.

## Done Gate

The project is not complete until `scripts/check_interview_readiness.py` passes and the matrix row is at least `validated`.
