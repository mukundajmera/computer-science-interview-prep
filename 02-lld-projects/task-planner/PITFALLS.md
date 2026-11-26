# Task Planner - Common Pitfalls

## 1. Flat Task Models
- **Failure Signal**: Implementing all task types as a single `Task` class with a `type` string and self-referential `parentId` without clear behavior separation.
- **Root Cause**: Over-reliance on database-driven design rather than domain-driven object models.
- **Mitigation**: Use polymorphism or the Composite pattern. Have a distinct `Story` class that manages a list of `Subtask` objects.

## 2. Hardcoded State Transitions
- **Failure Signal**: Giant switch statements or if-else blocks checking string states.
- **Root Cause**: Ignoring the State Pattern or finite state machine design.
- **Mitigation**: Use enums with transition rules or explicit state machine definitions.

## 3. Mutable Completed Sprints
- **Failure Signal**: Tasks can still be added to or modified in a `COMPLETED` sprint.
- **Root Cause**: Missing immutability or finalization checks on sprint objects.
- **Mitigation**: Add validation hooks on all task modification methods that check if the task's parent sprint is active.
