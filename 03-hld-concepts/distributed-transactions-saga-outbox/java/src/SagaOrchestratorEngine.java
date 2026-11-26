import java.util.List;
import java.util.ArrayList;

public class SagaOrchestratorEngine {
    
    private final List<SagaModels.SagaStep> steps;

    public SagaOrchestratorEngine(List<SagaModels.SagaStep> steps) {
        this.steps = new ArrayList<>(steps);
    }

    public SagaModels.SagaContext executeSaga(String sagaId) {
        SagaModels.SagaContext context = new SagaModels.SagaContext(sagaId);
        
        for (int i = 0; i < steps.size(); i++) {
            SagaModels.SagaStep step = steps.get(i);
            
            boolean success = step.execute(context);
            if (success) {
                context.completedSteps.add(step.name);
                if (step.isPivot) {
                    // Pivot successful, must succeed eventually, no rollbacks past this point
                }
            } else {
                // If a step fails, check if we already successfully passed a pivot step
                boolean passedPivot = context.completedSteps.stream().anyMatch(name -> {
                    return steps.stream().anyMatch(s -> s.name.equals(name) && s.isPivot);
                });
                // If we passed the pivot, then we require retry.
                // Note: If the pivot itself fails, we haven't passed the pivot (completedSteps does not contain it)
                // So failure of the pivot itself triggers compensation.
                if (passedPivot) {
                    context.finalStatus = "FAILED_REQUIRES_RETRY";
                    return context;
                } else {
                    // Pre-pivot failure (or pivot failure) -> trigger compensation
                    context.isCompensating = true;
                    compensate(context, i - 1);
                    return context;
                }
            }
        }
        
        context.finalStatus = "COMPLETED";
        return context;
    }

    private void compensate(SagaModels.SagaContext context, int lastSuccessfulStepIndex) {
        for (int i = lastSuccessfulStepIndex; i >= 0; i--) {
            SagaModels.SagaStep step = steps.get(i);
            boolean compSuccess = step.compensate(context);
            if (!compSuccess) {
                // If compensation fails, system requires manual intervention or infinite retries
                context.finalStatus = "COMPENSATION_FAILED";
                return;
            }
        }
        context.finalStatus = "CANCELLED";
    }
}
