# Task Planner - Code Walkthrough

## 1. Task Creation and Subtask Composition
The creation flow begins in `TaskPlannerService` which instantiates subclasses of `Task` (e.g. `Story`). When a user adds a `Subtask` to a `Story`, the `Story` uses the composite pattern to maintain a reference to the `Subtask`.

## 2. Sprint Lifecycle and Validation
When creating a sprint, its status is `CREATED`. 
Calling `startSprint()` validates that no other sprint is in `ACTIVE` state.
Calling `completeSprint()` transitions the active sprint to `COMPLETED` and calculates rollover.

## 3. Story Completion Block
The `changeTaskStatus` method checks if the task is a `Story` and the target status is `DONE`. If so, it iterates over the nested `Subtasks`. If any subtask is not `DONE`, the operation fails, enforcing hierarchical integrity.

## 4. Delayed Task Calculation
When a sprint completes, any tasks still `OPEN` or `IN_PROGRESS` are classified as delayed. These tasks can either be rolled over into the next sprint automatically, or reported through a specific query method.
