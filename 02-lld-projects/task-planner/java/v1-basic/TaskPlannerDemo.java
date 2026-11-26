public class TaskPlannerDemo {
    public static void main(String[] args) {
        TaskPlannerService service = new TaskPlannerService();

        Task story1 = service.createTask("T-1", "Build Login Page", TaskType.STORY);
        Task subtask1 = service.createSubtask("T-2", "UI Design", "T-1");
        Task subtask2 = service.createSubtask("T-3", "API Integration", "T-1");

        Sprint sprint1 = service.createSprint("S-1", "Sprint 1");
        service.addTaskToSprint("T-1", "S-1");
        
        service.startSprint("S-1");
        
        service.changeTaskStatus("T-2", TaskStatus.DONE);
        
        try {
            service.changeTaskStatus("T-1", TaskStatus.DONE);
        } catch (Exception e) {
            System.out.println("Expected failure: " + e.getMessage());
        }
        
        service.changeTaskStatus("T-3", TaskStatus.DONE);
        service.changeTaskStatus("T-1", TaskStatus.DONE);
        
        System.out.println("Story status: " + story1.getStatus());
        
        service.completeSprint("S-1");
        
        System.out.println("Delayed tasks count: " + service.getDelayedTasks().size());
    }
}
