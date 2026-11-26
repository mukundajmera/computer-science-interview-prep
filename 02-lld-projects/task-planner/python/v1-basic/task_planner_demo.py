from task_planner_service import TaskPlannerService
from task import TaskType, TaskStatus

def main():
    service = TaskPlannerService()

    story1 = service.create_task("T-1", "Build Login Page", TaskType.STORY)
    subtask1 = service.create_subtask("T-2", "UI Design", "T-1")
    subtask2 = service.create_subtask("T-3", "API Integration", "T-1")

    sprint1 = service.create_sprint("S-1", "Sprint 1")
    service.add_task_to_sprint("T-1", "S-1")
    
    service.start_sprint("S-1")
    
    service.change_task_status("T-2", TaskStatus.DONE)
    
    try:
        service.change_task_status("T-1", TaskStatus.DONE)
    except Exception as e:
        print(f"Expected failure: {e}")
        
    service.change_task_status("T-3", TaskStatus.DONE)
    service.change_task_status("T-1", TaskStatus.DONE)
    
    print(f"Story status: {story1.status.name}")
    
    service.complete_sprint("S-1")
    
    print(f"Delayed tasks count: {len(service.get_delayed_tasks())}")

if __name__ == "__main__":
    main()
