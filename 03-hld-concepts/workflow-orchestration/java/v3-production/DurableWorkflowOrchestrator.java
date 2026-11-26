import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * v3-production: workflow registry with idempotent start and resume hooks.
 */
public final class DurableWorkflowOrchestrator {
    public interface WorkflowHandler {
        void resume(String workflowId, long lastCheckpoint);
    }

    private final Map<String, Long> checkpointByWorkflow = new ConcurrentHashMap<>();
    private final Map<String, String> idempotencyToWorkflow = new ConcurrentHashMap<>();

    public String start(String idempotencyKey, String workflowId) {
        String existing = idempotencyToWorkflow.putIfAbsent(idempotencyKey, workflowId);
        if (existing != null) {
            return existing;
        }
        checkpointByWorkflow.put(workflowId, 0L);
        return workflowId;
    }

    public void checkpoint(String workflowId, long checkpoint) {
        checkpointByWorkflow.put(workflowId, checkpoint);
    }

    public void resume(String workflowId, WorkflowHandler handler) {
        long checkpoint = checkpointByWorkflow.getOrDefault(workflowId, 0L);
        handler.resume(workflowId, checkpoint);
    }
}
