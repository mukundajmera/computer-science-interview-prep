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
        # Memory constraint: shared int mapping if needed, but distinct string values are fine for basic enums
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

    def set_status(self, status: TaskStatus):
        self.status = status

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
