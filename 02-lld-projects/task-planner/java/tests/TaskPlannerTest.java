import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class TaskPlannerTest {
    private TaskPlannerService service;

    @BeforeEach
    void setUp() {
        service = new TaskPlannerService();
    }

    @Test
    void testTaskCreationAndTransitions() {
        Task bug = service.createTask("B-1", "Fix NPE", TaskType.BUG);
        assertEquals(TaskStatus.OPEN, bug.getStatus());

        service.changeTaskStatus("B-1", TaskStatus.IN_PROGRESS);
        assertEquals(TaskStatus.IN_PROGRESS, bug.getStatus());

        service.changeTaskStatus("B-1", TaskStatus.DONE);
        assertEquals(TaskStatus.DONE, bug.getStatus());
    }

    @Test
    void testStorySubtaskCompletionGuard() {
        Task story = service.createTask("S-1", "User Profile", TaskType.STORY);
        Task subtask1 = service.createSubtask("S-1-1", "Frontend", "S-1");
        Task subtask2 = service.createSubtask("S-1-2", "Backend", "S-1");

        service.changeTaskStatus("S-1-1", TaskStatus.DONE);

        IllegalStateException exception = assertThrows(IllegalStateException.class, () -> {
            service.changeTaskStatus("S-1", TaskStatus.DONE);
        });
        assertEquals("Cannot mark Story as DONE while there are pending Subtasks.", exception.getMessage());
        assertEquals(TaskStatus.OPEN, story.getStatus()); // remains unchanged

        service.changeTaskStatus("S-1-2", TaskStatus.DONE);
        service.changeTaskStatus("S-1", TaskStatus.DONE);
        assertEquals(TaskStatus.DONE, story.getStatus());
    }

    @Test
    void testSingleActiveSprintConstraint() {
        Sprint sprint1 = service.createSprint("SP-1", "Sprint 1");
        Sprint sprint2 = service.createSprint("SP-2", "Sprint 2");

        service.startSprint("SP-1");
        assertEquals(SprintStatus.ACTIVE, sprint1.getStatus());

        IllegalStateException exception = assertThrows(IllegalStateException.class, () -> {
            service.startSprint("SP-2");
        });
        assertEquals("Another sprint is already active.", exception.getMessage());
        
        service.completeSprint("SP-1");
        assertEquals(SprintStatus.COMPLETED, sprint1.getStatus());
        
        service.startSprint("SP-2");
        assertEquals(SprintStatus.ACTIVE, sprint2.getStatus());
    }

    @Test
    void testDelayedTaskRollover() {
        Task feature1 = service.createTask("F-1", "Feature 1", TaskType.FEATURE);
        Task feature2 = service.createTask("F-2", "Feature 2", TaskType.FEATURE);

        Sprint sprint1 = service.createSprint("SP-1", "Sprint 1");
        service.addTaskToSprint("F-1", "SP-1");
        service.addTaskToSprint("F-2", "SP-1");

        service.startSprint("SP-1");
        service.changeTaskStatus("F-1", TaskStatus.DONE);
        
        // F-2 is still OPEN
        service.completeSprint("SP-1");

        var delayedTasks = service.getDelayedTasks();
        assertEquals(1, delayedTasks.size());
        assertEquals("F-2", delayedTasks.get(0).getId());
    }
}
