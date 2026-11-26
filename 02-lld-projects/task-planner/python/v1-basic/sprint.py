from enum import Enum
from typing import List
from task import Task

class SprintStatus(Enum):
    CREATED = 1
    ACTIVE = 2
    COMPLETED = 3

class Sprint:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.status = SprintStatus.CREATED
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        if self.status == SprintStatus.COMPLETED:
            raise RuntimeError("Cannot add task to a completed sprint.")
        self.tasks.append(task)

    def remove_task(self, task: Task):
        self.tasks.remove(task)
