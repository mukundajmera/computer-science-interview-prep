# LLD Project Pack Template

Create these files for a complete LLD project pack:

- `PROBLEM.md`
- `APPROACH.md`
- `DESIGN.md`
- `CODE-WALKTHROUGH.md`
- `RUBRIC.md`
- `PITFALLS.md`
- `FOLLOW-UPS.md`
- Java and Python version folders where parity is required

## Required Problem Sections

- Functional requirements.
- Non-functional requirements.
- Constraints and invariants.
- API signals interviewers expect.
- Clarifying questions.
- Core entities.
- Version roadmap.
- Cross-links.

## Required Design Sections

- Public API contract.
- Class responsibilities.
- State transitions and invariants.
- Edge cases.
- Concurrency and testability notes.
- Design patterns used and rejected.
- Complexity.

## Code Walkthrough

Map each important class/function to:

- What it owns.
- What invariant it protects.
- Which tests prove it.
- How it changes between `v1-basic`, `v2-extended`, and `v3-optimized`.

## Done Gate

Both Java and Python tracks must compile/run where required, or the matrix must explicitly mark the language gap and why it is accepted.
