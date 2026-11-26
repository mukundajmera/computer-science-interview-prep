# Task Planner - Follow-Up Questions

## Follow-up questions
1. **Story Point Velocity**: How would you modify the system to calculate the team's velocity (total story points of DONE tasks) over historical sprints?
2. **Dependency Blockers**: How would you implement a feature where Task B is blocked by Task A, preventing Task B from moving to IN_PROGRESS until A is DONE?
3. **Custom Workflows**: What if different task types have different lifecycle states (e.g., Bug has "TO_REPRODUCE")?

## Variants and extensions
- **Gantt Chart Predecessors**: Implementing a directed acyclic graph (DAG) for task dependencies and detecting circular dependencies.
- **Event Sourcing**: Storing every state transition as an immutable event to rebuild the current state and audit history.

## Interviewer probes to prepare
- "If we have millions of tasks, how would you query delayed tasks efficiently?"
- "How does your system handle concurrent users trying to start different sprints?"
