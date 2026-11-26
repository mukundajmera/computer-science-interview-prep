from enum import Enum
from typing import List, Optional

class TaskType(Enum):
    EPIC = 1
    STORY = 2
    FEATURE = 3
    BUG = 4
    SUBTASK = 5

class TaskStatus(Enum):
    OPEN = 1
    IN_PROGRESS = 2
    IN_TESTING = 3
    DONE = 4

class Task:
    def __init__(self, id: str, title: str, type: TaskType):
        self.id = id
        self.title = title
        self.type = type
        self.status = TaskStatus.OPEN
        self.assignee: Optional[str] = None

    def set_status(self, status: TaskStatus):
        self.status = status

class Story(Task):
    def __init__(self, id: str, title: str):
        super().__init__(id, title, TaskType.STORY)
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
    def __init__(self, id: str, title: str, parent: Story):
        super().__init__(id, title, TaskType.SUBTASK)
        self.parent = parent
