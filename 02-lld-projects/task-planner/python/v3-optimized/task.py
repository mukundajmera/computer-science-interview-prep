from enum import Enum
from typing import List, Optional

class TaskType(Enum):
    EPIC = "EPIC"
    STORY = "STORY"
    FEATURE = "FEATURE"
    BUG = "BUG"
    SUBTASK = "SUBTASK"

    @property
    def value(self):
        return super().value

class TaskStatus(Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    IN_TESTING = "IN_TESTING"
    DONE = "DONE"

class Task:
    def __init__(self, id: str, title: str, type: TaskType, story_points: int = 0):
        self.id = id
        self.title = title
        self.type = type
        self.status = TaskStatus.OPEN
        self.assignee: Optional[str] = None
        self.story_points = story_points
        self.dependencies: List['Task'] = [] # Tasks this task depends on (must be finished before this)

    def set_status(self, status: TaskStatus):
        if status == TaskStatus.DONE:
            for dep in self.dependencies:
                if dep.status != TaskStatus.DONE:
                    raise RuntimeError(f"Cannot mark as DONE. Dependency {dep.id} is not DONE.")
        self.status = status

    def add_dependency(self, task: 'Task'):
        self.dependencies.append(task)

class Epic(Task):
    def __init__(self, id: str, title: str, story_points: int = 0):
        super().__init__(id, title, TaskType.EPIC, story_points)
        self.children: List[Task] = []

    def add_child(self, task: Task):
        if task.type in (TaskType.STORY, TaskType.FEATURE, TaskType.BUG):
            self.children.append(task)
        else:
            raise ValueError("Epic can only contain Story, Feature, or Bug.")

class Story(Task):
    def __init__(self, id: str, title: str, story_points: int = 0):
        super().__init__(id, title, TaskType.STORY, story_points)
        self.subtasks: List['Subtask'] = []

    def add_subtask(self, subtask: 'Subtask'):
        self.subtasks.append(subtask)

    def set_status(self, status: TaskStatus):
        if status == TaskStatus.DONE:
            for subtask in self.subtasks:
                if subtask.status != TaskStatus.DONE:
                    raise RuntimeError("Cannot mark Story as DONE while there are pending Subtasks.")
        super().set_status(status)

class Subtask(Task):
    def __init__(self, id: str, title: str, parent: Story, story_points: int = 0):
        super().__init__(id, title, TaskType.SUBTASK, story_points)
        self.parent = parent
