import pytest
import sys
import os
import importlib

for mod in ['task_planner_service', 'task', 'sprint']:
    if mod in sys.modules:
        del sys.modules[mod]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

try:
    from task_planner_service import TaskPlannerService
    from task import TaskType, TaskStatus
    from sprint import SprintStatus
except ImportError:
    pass

@pytest.fixture
def service():
    return TaskPlannerService()

def test_v2_sprint_velocity(service):
    service.create_task("T-1", "Task 1", TaskType.FEATURE, story_points=3)
    service.create_task("T-2", "Task 2", TaskType.BUG, story_points=2)
    
    sprint = service.create_sprint("SP-1", "Sprint 1")
    service.add_task_to_sprint("T-1", "SP-1")
    service.add_task_to_sprint("T-2", "SP-1")
    
    service.start_sprint("SP-1")
    service.change_task_status("T-1", TaskStatus.DONE)
    
    # Velocity should only sum up DONE tasks
    assert sprint.get_velocity() == 3
    
    service.change_task_status("T-2", TaskStatus.DONE)
    assert sprint.get_velocity() == 5

def test_v2_sprint_rollover(service):
    service.create_task("T-1", "Task 1", TaskType.FEATURE, story_points=5)
    service.create_task("T-2", "Task 2", TaskType.BUG, story_points=2)
    
    sprint1 = service.create_sprint("SP-1", "Sprint 1")
    sprint2 = service.create_sprint("SP-2", "Sprint 2")
    
    service.add_task_to_sprint("T-1", "SP-1")
    service.add_task_to_sprint("T-2", "SP-1")
    
    service.start_sprint("SP-1")
    service.change_task_status("T-1", TaskStatus.DONE)
    
    # Complete SP-1 and rollover to SP-2
    service.complete_sprint("SP-1", rollover_sprint_id="SP-2")
    
    # T-1 is done in SP-1
    assert sprint1.status == SprintStatus.COMPLETED
    
    # T-2 should be in SP-2 now
    assert len(sprint2.tasks) == 1
    assert sprint2.tasks[0].id == "T-2"
