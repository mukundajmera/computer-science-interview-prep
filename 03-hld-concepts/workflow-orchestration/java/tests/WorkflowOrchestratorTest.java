/**
 * Lightweight tests for workflow orchestration primitives.
 */
public final class WorkflowOrchestratorTest {
    public static void main(String[] args) {
        WorkflowStateMachine machine = new WorkflowStateMachine();
        machine.create("wf-1");
        machine.markRunning("wf-1");
        assert machine.get("wf-1") == WorkflowStateMachine.WorkflowState.RUNNING;
        System.out.println("WorkflowOrchestratorTest passed");
    }
}
