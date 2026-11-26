import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from task_planner_service import TaskPlannerService
from task import TaskType, TaskStatus
from sprint import SprintStatus

@pytest.fixture
def service():
    return TaskPlannerService()

def test_task_creation_and_transitions(service):
    bug = service.create_task("B-1", "Fix NPE", TaskType.BUG)
    assert bug.status == TaskStatus.OPEN

    service.change_task_status("B-1", TaskStatus.IN_PROGRESS)
    assert bug.status == TaskStatus.IN_PROGRESS

    service.change_task_status("B-1", TaskStatus.DONE)
    assert bug.status == TaskStatus.DONE

def test_story_subtask_completion_guard(service):
    story = service.create_task("S-1", "User Profile", TaskType.STORY)
    subtask1 = service.create_subtask("S-1-1", "Frontend", "S-1")
    subtask2 = service.create_subtask("S-1-2", "Backend", "S-1")

    service.change_task_status("S-1-1", TaskStatus.DONE)

    with pytest.raises(RuntimeError) as excinfo:
        service.change_task_status("S-1", TaskStatus.DONE)
    assert "pending Subtasks" in str(excinfo.value)
    assert story.status == TaskStatus.OPEN

    service.change_task_status("S-1-2", TaskStatus.DONE)
    service.change_task_status("S-1", TaskStatus.DONE)
    assert story.status == TaskStatus.DONE

def test_single_active_sprint_constraint(service):
    sprint1 = service.create_sprint("SP-1", "Sprint 1")
    sprint2 = service.create_sprint("SP-2", "Sprint 2")

    service.start_sprint("SP-1")
    assert sprint1.status == SprintStatus.ACTIVE

    with pytest.raises(RuntimeError) as excinfo:
        service.start_sprint("SP-2")
    assert "already active" in str(excinfo.value)
    
    service.complete_sprint("SP-1")
    assert sprint1.status == SprintStatus.COMPLETED
    
    service.start_sprint("SP-2")
    assert sprint2.status == SprintStatus.ACTIVE

def test_delayed_task_rollover(service):
    feature1 = service.create_task("F-1", "Feature 1", TaskType.FEATURE)
    feature2 = service.create_task("F-2", "Feature 2", TaskType.FEATURE)

    sprint1 = service.create_sprint("SP-1", "Sprint 1")
    service.add_task_to_sprint("F-1", "SP-1")
    service.add_task_to_sprint("F-2", "SP-1")

    service.start_sprint("SP-1")
    service.change_task_status("F-1", TaskStatus.DONE)
    
    service.complete_sprint("SP-1")

    delayed_tasks = service.get_delayed_tasks()
    assert len(delayed_tasks) == 1
    assert delayed_tasks[0].id == "F-2"
