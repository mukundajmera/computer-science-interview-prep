import pytest
import sys
import os

for mod in ['task_planner_service', 'task', 'sprint']:
    if mod in sys.modules:
        del sys.modules[mod]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

try:
    from task_planner_service import TaskPlannerService
    from task import TaskType, TaskStatus
    from sprint import SprintStatus
except ImportError:
    pass

@pytest.fixture
def service():
    return TaskPlannerService()

def test_v3_epic_hierarchy(service):
    epic = service.create_task("E-1", "Epic 1", TaskType.EPIC)
    story = service.create_task("S-1", "Story 1", TaskType.STORY)
    bug = service.create_task("B-1", "Bug 1", TaskType.BUG)
    
    service.add_to_epic("E-1", "S-1")
    service.add_to_epic("E-1", "B-1")
    
    assert len(epic.children) == 2
    assert epic.children[0].id == "S-1"
    assert epic.children[1].id == "B-1"

def test_v3_dependency_cycle_detection(service):
    service.create_task("T-1", "Task 1", TaskType.FEATURE)
    service.create_task("T-2", "Task 2", TaskType.FEATURE)
    service.create_task("T-3", "Task 3", TaskType.FEATURE)
    
    # T-1 depends on T-2
    service.add_dependency("T-1", "T-2")
    # T-2 depends on T-3
    service.add_dependency("T-2", "T-3")
    
    # Adding T-3 depends on T-1 should cause a cycle
    with pytest.raises(RuntimeError) as excinfo:
        service.add_dependency("T-3", "T-1")
    assert "would create a cycle" in str(excinfo.value)

def test_v3_dependency_completion_guard(service):
    t1 = service.create_task("T-1", "Task 1", TaskType.FEATURE)
    t2 = service.create_task("T-2", "Task 2", TaskType.FEATURE)
    
    service.add_dependency("T-1", "T-2")
    
    # Cannot mark T-1 as done because T-2 is not done
    with pytest.raises(RuntimeError) as excinfo:
        service.change_task_status("T-1", TaskStatus.DONE)
    assert "Dependency T-2 is not DONE" in str(excinfo.value)
    
    # Mark T-2 as done, then T-1 can be done
    service.change_task_status("T-2", TaskStatus.DONE)
    service.change_task_status("T-1", TaskStatus.DONE)
    
    assert t1.status == TaskStatus.DONE
