# Task Planner - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
| --- | --- | --- |
| Object-Oriented Design | 30% | Correctly uses polymorphism and abstraction for task types. Understands composite pattern for hierarchical tasks. |
| Business Logic Integrity | 30% | Enforces single active sprint. Prevents completing stories with open subtasks. |
| Code Quality | 20% | Clean code, proper naming, modular structure. Uses enums for statuses. |
| Testability | 20% | Core logic (state transitions, active sprint guard) is highly unit testable without mocking the whole system. |

## Performance Bands
- **Strong Hire**: Implements all constraints flawlessly, elegant Composite pattern, handles edge cases around sprint rollover.
- **Hire**: Completes basic state transitions and nested subtasks checks, but code might be slightly monolithic.
- **No Hire**: Fails on hard failure gates.

## Hard Failure Gates
- Allowing multiple ACTIVE sprints at the same time.
- Allowing a Story to be marked DONE while it has OPEN subtasks.

## Cross-links
- [Problem](PROBLEM.md)
- [Design](DESIGN.md)
