import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v2_extended.*;

import static org.junit.jupiter.api.Assertions.*;

class TaskPlannerV2Test {
    private TaskPlannerService service;

    @BeforeEach
    void setUp() {
        service = new TaskPlannerService();
    }

    @Test
    void testSprintVelocity() {
        service.createTask("T-1", "Task 1", TaskType.FEATURE, 3);
        service.createTask("T-2", "Task 2", TaskType.BUG, 2);
        
        Sprint sprint = service.createSprint("SP-1", "Sprint 1");
        service.addTaskToSprint("T-1", "SP-1");
        service.addTaskToSprint("T-2", "SP-1");
        
        service.startSprint("SP-1");
        service.changeTaskStatus("T-1", TaskStatus.DONE);
        
        assertEquals(3, sprint.getVelocity());
        
        service.changeTaskStatus("T-2", TaskStatus.DONE);
        assertEquals(5, sprint.getVelocity());
    }

    @Test
    void testSprintRollover() {
        service.createTask("T-1", "Task 1", TaskType.FEATURE, 5);
        service.createTask("T-2", "Task 2", TaskType.BUG, 2);
        
        Sprint sprint1 = service.createSprint("SP-1", "Sprint 1");
        Sprint sprint2 = service.createSprint("SP-2", "Sprint 2");
        
        service.addTaskToSprint("T-1", "SP-1");
        service.addTaskToSprint("T-2", "SP-1");
        
        service.startSprint("SP-1");
        service.changeTaskStatus("T-1", TaskStatus.DONE);
        
        service.completeSprint("SP-1", "SP-2");
        
        assertEquals(SprintStatus.COMPLETED, sprint1.getStatus());
        assertEquals(1, sprint2.getTasks().size());
        assertEquals("T-2", sprint2.getTasks().get(0).getId());
    }
}
