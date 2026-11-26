import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * v1-simple: run steps and compensate in reverse on failure.
 */
public final class SagaStepRunner {
    public interface WorkflowStep {
        String name();
        void execute();
        void compensate();
    }

    public ExecutionResult run(List<WorkflowStep> steps) {
        List<WorkflowStep> completed = new ArrayList<>();
        try {
            for (WorkflowStep step : steps) {
                step.execute();
                completed.add(step);
            }
            return new ExecutionResult(true, "completed", List.of());
        } catch (RuntimeException ex) {
            Collections.reverse(completed);
            for (WorkflowStep step : completed) {
                step.compensate();
            }
            return new ExecutionResult(false, ex.getMessage(), stepNames(completed));
        }
    }

    private List<String> stepNames(List<WorkflowStep> steps) {
        List<String> names = new ArrayList<>();
        for (WorkflowStep step : steps) {
            names.add(step.name());
        }
        return names;
    }

    public static final class ExecutionResult {
        public final boolean success;
        public final String message;
        public final List<String> compensatedSteps;

        public ExecutionResult(boolean success, String message, List<String> compensatedSteps) {
            this.success = success;
            this.message = message;
            this.compensatedSteps = compensatedSteps;
        }
    }
}
