from typing import Dict, List, Optional, Set
from task import Task, TaskType, TaskStatus, Story, Subtask, Epic
from sprint import Sprint, SprintStatus

class TaskPlannerService:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.active_sprint: Optional[Sprint] = None
        self.backlog: List[Task] = []

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

    def add_to_epic(self, epic_id: str, child_id: str):
        epic = self.tasks.get(epic_id)
        child = self.tasks.get(child_id)
        if not isinstance(epic, Epic):
            raise ValueError("Parent must be an Epic.")
        if not child:
            raise ValueError("Child task not found.")
        epic.add_child(child)

    def create_subtask(self, id: str, title: str, story_id: str, story_points: int = 0) -> Subtask:
        parent = self.tasks.get(story_id)
        if not isinstance(parent, Story):
            raise ValueError("Parent must be a Story.")
            
        subtask = Subtask(id, title, parent, story_points)
        self.tasks[id] = subtask
        parent.add_subtask(subtask)
        return subtask

    def add_dependency(self, task_id: str, depends_on_id: str):
        task = self.tasks.get(task_id)
        depends_on = self.tasks.get(depends_on_id)
        if not task or not depends_on:
            raise ValueError("Invalid task ID(s).")
            
        # Check for cycles
        if self._has_cycle(task_id, depends_on_id):
            raise RuntimeError(f"Adding dependency {task_id} -> {depends_on_id} would create a cycle.")
            
        task.add_dependency(depends_on)

    def _has_cycle(self, from_task_id: str, to_task_id: str) -> bool:
        # Check if adding from_task_id -> to_task_id creates a cycle.
        # This means there is already a path from to_task_id to from_task_id.
        visited: Set[str] = set()
        
        def dfs(current_id: str) -> bool:
            if current_id == from_task_id:
                return True
            if current_id in visited:
                return False
            visited.add(current_id)
            current_task = self.tasks.get(current_id)
            if current_task:
                for dep in current_task.dependencies:
                    if dfs(dep.id):
                        return True
            return False
            
        return dfs(to_task_id)

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

    def complete_sprint(self, sprint_id: str, rollover_sprint_id: Optional[str] = None):
        sprint = self.sprints.get(sprint_id)
        if not sprint or sprint != self.active_sprint:
            raise ValueError("Sprint is not active.")
            
        sprint.status = SprintStatus.COMPLETED
        self.active_sprint = None
        
        unfinished_tasks = [t for t in sprint.tasks if t.status != TaskStatus.DONE]
        
        if rollover_sprint_id:
            next_sprint = self.sprints.get(rollover_sprint_id)
            if not next_sprint:
                raise ValueError("Rollover sprint not found.")
            for t in unfinished_tasks:
                next_sprint.add_task(t)
        else:
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
