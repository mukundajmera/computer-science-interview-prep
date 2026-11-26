import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class SagaModels {

    public static class SagaContext {
        public final String sagaId;
        public final List<String> completedSteps;
        public boolean isCompensating;
        public String finalStatus; // COMPLETED, CANCELLED, FAILED

        public SagaContext(String sagaId) {
            this.sagaId = sagaId;
            this.completedSteps = new ArrayList<>();
            this.isCompensating = false;
            this.finalStatus = "PENDING";
        }
    }

    public static abstract class SagaStep {
        public final String name;
        public final boolean isPivot;

        public SagaStep(String name, boolean isPivot) {
            this.name = name;
            this.isPivot = isPivot;
        }

        // Returns true if forward action succeeds
        public abstract boolean execute(SagaContext context);

        // Returns true if compensation succeeds
        public abstract boolean compensate(SagaContext context);
    }
}
