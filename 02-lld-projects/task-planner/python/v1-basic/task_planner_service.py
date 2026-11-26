from typing import Dict, List, Optional
from task import Task, TaskType, TaskStatus, Story, Subtask
from sprint import Sprint, SprintStatus

class TaskPlannerService:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.active_sprint: Optional[Sprint] = None
        self.backlog: List[Task] = []

    def create_task(self, id: str, title: str, type: TaskType) -> Task:
        if id in self.tasks:
            raise ValueError(f"Task with id {id} already exists.")
        
        if type == TaskType.STORY:
            task = Story(id, title)
        else:
            task = Task(id, title, type)
            
        self.tasks[id] = task
        self.backlog.append(task)
        return task

    def create_subtask(self, id: str, title: str, story_id: str) -> Subtask:
        parent = self.tasks.get(story_id)
        if not isinstance(parent, Story):
            raise ValueError("Parent must be a Story.")
            
        subtask = Subtask(id, title, parent)
        self.tasks[id] = subtask
        parent.add_subtask(subtask)
        return subtask

    def create_sprint(self, id: str, name: str) -> Sprint:
        if id in self.sprints:
            raise ValueError(f"Sprint with id {id} already exists.")
            
        sprint = Sprint(id, name)
        self.sprints[id] = sprint
        return sprint

    def add_task_to_sprint(self, task_id: str, sprint_id: str):
        task = self.tasks.get(task_id)
        sprint = self.sprints.get(sprint_id)
        
        if not task or not sprint:
            raise ValueError("Invalid task or sprint ID.")
            
        sprint.add_task(task)
        if task in self.backlog:
            self.backlog.remove(task)

    def start_sprint(self, sprint_id: str):
        if self.active_sprint is not None:
            raise RuntimeError("Another sprint is already active.")
            
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            raise ValueError("Sprint not found.")
            
        if sprint.status != SprintStatus.CREATED:
            raise RuntimeError("Can only start a created sprint.")
            
        sprint.status = SprintStatus.ACTIVE
        self.active_sprint = sprint

    def complete_sprint(self, sprint_id: str):
        sprint = self.sprints.get(sprint_id)
        if not sprint or sprint != self.active_sprint:
            raise ValueError("Sprint is not active.")
            
        sprint.status = SprintStatus.COMPLETED
        self.active_sprint = None
        
        unfinished_tasks = [t for t in sprint.tasks if t.status != TaskStatus.DONE]
        self.backlog.extend(unfinished_tasks)

    def change_task_status(self, task_id: str, status: TaskStatus):
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError("Task not found.")
        task.set_status(status)

    def get_delayed_tasks(self) -> List[Task]:
        delayed_tasks = []
        for sprint in self.sprints.values():
            if sprint.status == SprintStatus.COMPLETED:
                for task in sprint.tasks:
                    if task.status != TaskStatus.DONE:
                        delayed_tasks.append(task)
        return delayed_tasks
