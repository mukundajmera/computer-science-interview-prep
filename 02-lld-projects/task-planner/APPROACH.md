# Task Planner - Approach

## Entity Identification
- **Tasks**: An abstract `Task` concept with subclasses for `Story`, `Subtask`, `Bug`, `Feature`, etc.
- **Sprint**: Holds a collection of tasks and a status.
- **Service**: Orchestrates task creation, sprint management, and transitions.

## Design Patterns
- **Composite Pattern**: Used for task hierarchies. A `Story` acts as a composite containing `Subtask` leaves. Completing a `Story` requires checking the status of all child `Subtask`s.
- **State Pattern**: Used to manage Task and Sprint lifecycle transitions, ensuring valid status changes (e.g., CREATED -> ACTIVE -> COMPLETED for sprints, OPEN -> IN_PROGRESS -> DONE for tasks).

## Sprint Lifecycle Constraints
- Ensure a singleton-like state constraint at the system level: `TaskPlannerService` tracks the current active sprint. Attempting to start another sprint throws an exception.
- When completing a sprint, we iterate through its tasks to find uncompleted tasks and either unassign them (move to backlog) or immediately roll them into a newly created sprint.

## Rollover Strategies
- We can return delayed tasks on demand by checking the status of tasks attached to historical sprints.
