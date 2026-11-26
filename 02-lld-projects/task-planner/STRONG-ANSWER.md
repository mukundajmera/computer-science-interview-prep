# Strong Answer: Task Planner (Jira/Trello clone)

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Task Planner, I will focus on modeling the core entities, defining the lifecycle constraints, and ensuring thread-safe operations under concurrent loads. I'll begin by outlining the core data models (Epic, Story, Subtask, Sprint), then progress to the architecture, covering APIs, design alternatives, correctness, and a failure/concurrency discussion."

The system needs to manage a task hierarchy and enforce domain rules:
- Subtasks belong only to Stories, and Epics contain Stories/Tasks/Bugs.
- Cyclic dependencies must be prevented.
- State transitions must be strictly validated (e.g., cannot complete a story with pending subtasks, or a task with pending dependencies).
- Sprints have a strict lifecycle with exactly one active sprint permitted at a time.

## 2. Entity Modeling & Core APIs (5-15 minutes)

**Say:** "I will use Object-Oriented principles to define the domain model. We have an abstract `Task` with subclasses `Epic`, `Story`, and `Subtask`. Tasks track their state (`TaskStatus`) and dependencies. I'll expose a centralized `TaskPlannerService` to orchestrate operations and enforce cross-entity rules."

### Core Entities
- **`Task` (Abstract)**: Base fields `id`, `title`, `status`, `storyPoints`, `assignee`, and a `List<Task>` of dependencies.
- **`Story`**: Extends `Task`. Implements the Composite pattern to hold `List<Subtask>`. Overrides status transition to enforce child completion.
- **`Epic`**: Extends `Task`. Holds a collection of child tasks (Stories/Bugs) but rejects nested Epics/Subtasks.
- **`Sprint`**: Maintains an ID, name, list of tasks, and `SprintStatus` (CREATED, ACTIVE, COMPLETED).

### Public APIs & Validations
- `Task createTask(id, title, type, points)`: Rejects duplicate IDs.
- `Subtask createSubtask(id, title, storyId, points)`: Binds a new subtask strictly to an existing `Story`.
- `void addDependency(taskId, dependsOnId)`: Performs an acyclic check before mutating state.
- `Sprint createSprint(id, name)`: Creates a sprint in the `CREATED` state.
- `void startSprint(sprintId)`: Requires the sprint to be `CREATED` and validates no other sprint is `ACTIVE`.
- `void completeSprint(sprintId, rolloverSprintId)`: Transitions sprint to `COMPLETED` and rolls pending tasks to the next sprint or backlog.

*Version Delta:* In `v1-basic`, we only handled basic tasks and statuses. In `v2-extended`, sprint rollover and velocity (points sum) were handled. In `v3-optimized`, we introduced cyclical dependency detection via DFS and hierarchical state validation (Epic -> Story -> Subtask). Focused tests target this specific version rather than silently importing `v1-basic`.

## 3. Design Patterns & Alternatives (15-25 minutes)

**Say:** "For the design, I've incorporated the **Composite Pattern** for task hierarchies (Stories containing Subtasks, Epics containing Stories). I use the **State Pattern** implicitly for state transition guards, ensuring tasks move from OPEN to IN_PROGRESS to DONE only when valid."

### Trade-offs
- **Graph vs Adjacency List**: I track dependencies via an adjacency list within the `Task` object. An alternative is maintaining a central Directed Graph in the service. Keeping references in the domain object reduces lookup overhead for single-task operations but increases memory if tasks have massive fan-outs.
- **Immediate vs Deferred Validation**: For dependencies, I validate cycles *on edge insertion* (`addDependency`) via DFS rather than at execution time. This guarantees the task graph is always a Directed Acyclic Graph (DAG) but makes insertion O(V+E). Since reads/transitions are much more frequent than dependency additions, paying the traversal cost at write-time is optimal.

## 4. Acceptance Criteria & Edge Cases (25-35 minutes)

**Say:** "The system must predictably handle edge cases to prevent corrupting project state. The implementation enforces strict API contracts across both languages to maintain stability."

1. **Normal Use-Case**: Create a Sprint, add an Epic and Story, start the Sprint, finish tasks, and complete the Sprint. This demonstrates correct state transitions and hierarchy maintenance.

**Java (`TaskPlannerV3Test.java`)**:
```java
    @Test
    void testEpicHierarchy() {
        Task epic = service.createTask("E-1", "Epic 1", TaskType.EPIC, 0);
        Task story = service.createTask("S-1", "Story 1", TaskType.STORY, 3);
        Task bug = service.createTask("B-1", "Bug 1", TaskType.BUG, 1);
        
        service.addToEpic("E-1", "S-1");
        service.addToEpic("E-1", "B-1");
        
        assertTrue(epic instanceof Epic);
        Epic castedEpic = (Epic) epic;
        assertEquals(2, castedEpic.getChildren().size());
        assertEquals("S-1", castedEpic.getChildren().get(0).getId());
        assertEquals("B-1", castedEpic.getChildren().get(1).getId());
    }
```
**Python (`test_v3_optimized.py`)**:
```python
def test_v3_epic_hierarchy(service):
    epic = service.create_task("E-1", "Epic 1", TaskType.EPIC)
    story = service.create_task("S-1", "Story 1", TaskType.STORY)
    bug = service.create_task("B-1", "Bug 1", TaskType.BUG)
    
    service.add_to_epic("E-1", "S-1")
    service.add_to_epic("E-1", "B-1")
    
    assert len(epic.children) == 2
    assert epic.children[0].id == "S-1"
    assert epic.children[1].id == "B-1"

```

2. **Empty/Invalid Input**: API calls with null or non-existent Task IDs throw explicit exceptions (`IllegalArgumentException` in Java, `ValueError`/`RuntimeError` in Python), safely terminating requests before any partial mutations occur. Invalid operations, like adding a Subtask to a non-Story task, are immediately rejected.

**Java (`TaskPlannerService.java`)**:
```java
    public void addToEpic(String epicId, String childId) {
        Task epicTask = tasks.get(epicId);
        Task child = tasks.get(childId);
        if (!(epicTask instanceof Epic)) {
            throw new IllegalArgumentException("Parent must be an Epic.");
        }
        if (child == null) {
            throw new IllegalArgumentException("Child task not found.");
        }
        ((Epic) epicTask).addChild(child);
    }
```
**Python (`task_planner_service.py`)**:
```python
    def add_to_epic(self, epic_id: str, child_id: str):
        epic = self.tasks.get(epic_id)
        child = self.tasks.get(child_id)
        if not isinstance(epic, Epic):
            raise ValueError("Parent must be an Epic.")
        if not child:
            raise ValueError("Child task not found.")
        epic.add_child(child)
```
3. **Duplicate Operation**: Attempting to create a task or sprint with an existing ID, or attempting to start an already `ACTIVE` sprint, results in an immediate exception (`IllegalStateException` or `RuntimeError`).

**Java (`TaskPlannerService.java`)**:
```java
    public Task createTask(String id, String title, TaskType type, int storyPoints) {
        if (tasks.containsKey(id)) {
            throw new IllegalArgumentException("Task with id " + id + " already exists.");
        }
        Task task;
        if (type == TaskType.EPIC) {
            task = new Epic(id, title, storyPoints);
        } else if (type == TaskType.STORY) {
            task = new Story(id, title, storyPoints);
        } else if (type == TaskType.SUBTASK) {
            throw new IllegalArgumentException("Subtasks must be created using createSubtask.");
        } else {
            task = new Task(id, title, type, storyPoints);
        }
        tasks.put(id, task);
        backlog.add(task);
        return task;
    }

    public void startSprint(String sprintId) {
        if (activeSprint != null) {
            throw new IllegalStateException("Another sprint is already active.");
        }
        Sprint sprint = sprints.get(sprintId);
        if (sprint == null) {
            throw new IllegalArgumentException("Sprint not found.");
        }
        sprint.start();
        activeSprint = sprint;
    }
```
**Python (`task_planner_service.py`)**:
```python
    def create_task(self, id: str, title: str, type: TaskType, story_points: int = 0) -> Task:
        if id in self.tasks:
            raise ValueError(f"Task with id {id} already exists.")
        
        if type == TaskType.EPIC:
            task = Epic(id, title, story_points)
        elif type == TaskType.STORY:
            task = Story(id, title, story_points)
        elif type == TaskType.SUBTASK:
            raise ValueError("Subtasks must be created using create_subtask.")
        else:
            task = Task(id, title, type, story_points)
            
        self.tasks[id] = task
        self.backlog.append(task)
        return task

    def start_sprint(self, sprint_id: str):
        if self.active_sprint is not None:
            raise RuntimeError("Another sprint is already active.")
            
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            raise ValueError("Sprint not found.")
            
        sprint.start()
        self.active_sprint = sprint
```

4. **Capacity Boundary**: While recursive DFS cycle detection handles standard project DAGs, pathological graphs (e.g., thousands of deep dependencies) risk stack overflow. We mitigate this boundary by allowing fallback to iterative DFS or enforcing maximum dependency depth limits.

**Java (`TaskPlannerService.java`)**:
```java
    private boolean hasCycle(String fromTaskId, String toTaskId) {
        Set<String> visited = new HashSet<>();
        return dfs(toTaskId, fromTaskId, visited); // DFS depth limited by stack memory
    }
```
**Python (`task_planner_service.py`)**:
```python
    def _has_cycle(self, from_task_id: str, to_task_id: str) -> bool:
        visited: Set[str] = set()
        def dfs(current_id: str) -> bool:
            # ... recursive DFS limited by Python recursion limit
```
5. **Failure Rollback**: When `addDependency` detects a cycle, it throws an exception *before* appending the edge to the task's internal dependency list. This ensures an immediate failure rollback, preserving the system's prior valid DAG state.

**Java (`TaskPlannerService.java`)**:
```java
    public void addDependency(String taskId, String dependsOnId) {
        Task task = tasks.get(taskId);
        Task dependsOn = tasks.get(dependsOnId);
        if (task == null || dependsOn == null) {
            throw new IllegalArgumentException("Invalid task ID(s).");
        }
        
        if (hasCycle(taskId, dependsOnId)) {
            throw new IllegalStateException("Adding dependency " + taskId + " -> " + dependsOnId + " would create a cycle.");
        }
        
        task.addDependency(dependsOn);
    }
```

**Python (`task_planner_service.py`)**:
```python
    def add_dependency(self, task_id: str, depends_on_id: str):
        task = self.tasks.get(task_id)
        depends_on = self.tasks.get(depends_on_id)
        if not task or not depends_on:
            raise ValueError("Invalid task ID(s).")
            
        # Check for cycles
        if self._has_cycle(task_id, depends_on_id):
            raise RuntimeError(f"Adding dependency {task_id} -> {depends_on_id} would create a cycle.")
            
        task.add_dependency(depends_on)
```

## 5. Concurrency & Correctness (35-45 minutes)

**Say:** "Under high concurrency, operations like completing a sprint or modifying shared tasks can result in race conditions. We must ensure thread safety without creating deadlocks."

### Concurrency Discussion
If User A marks a `Story` as DONE while User B concurrently adds a new `Subtask` to that same Story, we risk a corrupted state where a DONE Story contains an OPEN Subtask.

- **Mitigation Strategy**: We use granular locking. In Java, this means using a `ReentrantReadWriteLock` on the `Story` entity, or making state mutations synchronized blocks. 
- **Alternative (Optimistic Concurrency)**: We can attach a `version` (ETag) to the Task. The client reads version `N`. When User A submits the DONE status, they pass `version=N`. If User B's subtask creation bumped the version to `N+1`, User A's update is rejected. This provides safety without heavy server-side locking, optimizing for read-heavy API workloads.

### Summary
By enforcing strict domain invariants (no cycles, no incomplete subtasks in done stories) within the encapsulated entity methods and orchestrating the sprint lifecycle rigidly in the service, this architecture provides a durable and correct model for a task planner.
