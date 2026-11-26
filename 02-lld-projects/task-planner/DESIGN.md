# Task Planner - Design

## System Architecture
The Task Planner consists of three main layers:
1. **Domain Entities**: `Task`, `Story`, `Subtask`, `Sprint`
2. **Business Logic Layer**: `TaskPlannerService` which enforces constraints.
3. **Data/State Layer**: In-memory data structures keeping track of tasks and sprints.

## Class Diagram

```mermaid
classDiagram
    class TaskType {
        <<enumeration>>
        EPIC, STORY, FEATURE, BUG, SUBTASK
    }
    class TaskStatus {
        <<enumeration>>
        OPEN, IN_PROGRESS, DONE
    }
    class SprintStatus {
        <<enumeration>>
        CREATED, ACTIVE, COMPLETED
    }
    class Task {
        +String id
        +String title
        +TaskType type
        +TaskStatus status
        +String assignee
        +changeStatus()
    }
    class Story {
        +List~Subtask~ subtasks
        +addSubtask()
        +changeStatus()
    }
    class Subtask {
        +Story parent
    }
    class Sprint {
        +String id
        +SprintStatus status
        +List~Task~ tasks
        +start()
        +complete()
    }
    class TaskPlannerService {
        +createTask()
        +createSprint()
        +startSprint()
        +completeSprint()
        +changeTaskStatus()
    }

    Task <|-- Story
    Task <|-- Subtask
    Story "1" *-- "*" Subtask
    Sprint "1" o-- "*" Task
    TaskPlannerService --> Sprint
    TaskPlannerService --> Task
```

## Sequence Diagrams

### Sprint Start Validation

```mermaid
sequenceDiagram
    actor User
    participant TaskPlannerService
    participant Sprint

    User->>TaskPlannerService: startSprint(sprintId)
    TaskPlannerService->>TaskPlannerService: checkActiveSprintExists()
    alt Active sprint exists
        TaskPlannerService-->>User: Throw Exception
    else No active sprint
        TaskPlannerService->>Sprint: setStatus(ACTIVE)
        Sprint-->>TaskPlannerService: OK
        TaskPlannerService-->>User: Success
    end
```

### Story Status Change (Checking Subtasks)

```mermaid
sequenceDiagram
    actor User
    participant TaskPlannerService
    participant Story
    participant Subtask

    User->>TaskPlannerService: changeTaskStatus(storyId, DONE)
    TaskPlannerService->>Story: changeStatus(DONE)
    Story->>Subtask: checkStatus()
    alt Subtasks not DONE
        Story-->>TaskPlannerService: Throw Exception
        TaskPlannerService-->>User: Error: Pending Subtasks
    else All Subtasks DONE
        Story->>Story: setStatus(DONE)
        Story-->>TaskPlannerService: Success
        TaskPlannerService-->>User: OK
    end
```
