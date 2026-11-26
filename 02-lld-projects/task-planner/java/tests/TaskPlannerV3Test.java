import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v3_optimized.*;

import static org.junit.jupiter.api.Assertions.*;

class TaskPlannerV3Test {
    private TaskPlannerService service;

    @BeforeEach
    void setUp() {
        service = new TaskPlannerService();
    }

    @Test
    void testEpicHierarchy() {
        Task epic = service.createTask("E-1", "Epic 1", TaskType.EPIC, 0);
        Task story = service.createTask("S-1", "Story 1", TaskType.STORY, 3);
        Task bug = service.createTask("B-1", "Bug 1", TaskType.BUG, 1);
        
        service.addToEpic("E-1", "S-1");
        service.addToEpic("E-1", "B-1");
        
        assertTrue(epic instanceof Epic);
        Epic castedEpic = (Epic) epic;
        assertEquals(2, castedEpic.getChildren().size());
        assertEquals("S-1", castedEpic.getChildren().get(0).getId());
        assertEquals("B-1", castedEpic.getChildren().get(1).getId());
    }

    @Test
    void testDependencyCycleDetection() {
        service.createTask("T-1", "Task 1", TaskType.FEATURE, 2);
        service.createTask("T-2", "Task 2", TaskType.FEATURE, 3);
        service.createTask("T-3", "Task 3", TaskType.FEATURE, 1);
        
        service.addDependency("T-1", "T-2");
        service.addDependency("T-2", "T-3");
        
        IllegalStateException exception = assertThrows(IllegalStateException.class, () -> {
            service.addDependency("T-3", "T-1");
        });
        assertTrue(exception.getMessage().contains("would create a cycle"));
    }

    @Test
    void testDependencyCompletionGuard() {
        Task t1 = service.createTask("T-1", "Task 1", TaskType.FEATURE, 2);
        service.createTask("T-2", "Task 2", TaskType.FEATURE, 3);
        
        service.addDependency("T-1", "T-2");
        
        IllegalStateException exception = assertThrows(IllegalStateException.class, () -> {
            service.changeTaskStatus("T-1", TaskStatus.DONE);
        });
        assertTrue(exception.getMessage().contains("Dependency T-2 is not DONE"));
        
        service.changeTaskStatus("T-2", TaskStatus.DONE);
        service.changeTaskStatus("T-1", TaskStatus.DONE);
        
        assertEquals(TaskStatus.DONE, t1.getStatus());
    }
}
