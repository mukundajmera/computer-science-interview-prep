import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * v2-realistic: durable-ish state transitions for workflow lifecycle.
 */
public final class WorkflowStateMachine {
    public enum WorkflowState {
        CREATED,
        RUNNING,
        COMPENSATING,
        SUCCEEDED,
        FAILED
    }

    private final Map<String, WorkflowState> stateByWorkflow = new ConcurrentHashMap<>();

    public void create(String workflowId) {
        stateByWorkflow.put(workflowId, WorkflowState.CREATED);
    }

    public void markRunning(String workflowId) {
        stateByWorkflow.put(workflowId, WorkflowState.RUNNING);
    }

    public void markCompensating(String workflowId) {
        stateByWorkflow.put(workflowId, WorkflowState.COMPENSATING);
    }

    public void markSucceeded(String workflowId) {
        stateByWorkflow.put(workflowId, WorkflowState.SUCCEEDED);
    }

    public void markFailed(String workflowId) {
        stateByWorkflow.put(workflowId, WorkflowState.FAILED);
    }

    public WorkflowState get(String workflowId) {
        return stateByWorkflow.get(workflowId);
    }
}
