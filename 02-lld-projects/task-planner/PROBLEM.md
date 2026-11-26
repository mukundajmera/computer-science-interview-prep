# Task Planner - Problem Statement

## Functional Requirements
1. **Task Management**: Support creation of different types of tasks (Epic, Story, Feature, Bug, Subtask).
2. **Task Hierarchy**: Support Subtasks nested under Stories.
3. **Task State Machine**: Support transitions like OPEN, IN_PROGRESS, IN_TESTING, DONE.
4. **Sprint Management**: Manage sprints with lifecycle CREATED, ACTIVE, COMPLETED.
5. **Sprint Constraints**: 
   - Only one active sprint is allowed at any given time.
   - Tasks cannot be transitioned to completed if there are any pending Subtasks.
6. **Task Queries**: Query delayed tasks (e.g. tasks not completed within a sprint, or rollover).
7. **Rollover Strategy**: When a sprint is completed, any incomplete tasks should automatically rollover to the next sprint, or move back to the backlog.

## Non-functional Requirements
1. **Extensibility**: It should be easy to add new task types or new status transitions without modifying existing code.
2. **Maintainability**: Clear separation of concerns between task management and sprint lifecycle.

## Clarifying Questions
- Q: Can tasks belong to multiple sprints?
  A: No, a task can be in at most one sprint at a time.
- Q: Are bugs and features hierarchical?
  A: For this version, only Stories support nesting of Subtasks.

## Core Entities
- `Task` (Base class or Interface)
- `Epic`, `Story`, `Feature`, `Bug`, `Subtask`
- `Sprint`
- `TaskPlannerService`
