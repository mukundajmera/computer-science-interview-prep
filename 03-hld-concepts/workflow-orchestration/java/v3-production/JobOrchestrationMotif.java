import java.util.ArrayList;
import java.util.List;

public class JobOrchestrationMotif {
    private final List<String> steps = new ArrayList<>();

    public void addStep(String stepName) {
        steps.add(stepName);
    }

    public List<String> getSteps() {
        return steps;
    }
}
