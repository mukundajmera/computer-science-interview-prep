package v3_optimized;

import java.util.ArrayList;
import java.util.List;

public class CheckpointManager {
    private List<String> savedState = new ArrayList<>();

    public synchronized void saveCheckpoint(List<String> queueState) {
        this.savedState = new ArrayList<>(queueState);
    }

    public synchronized List<String> loadCheckpoint() {
        return new ArrayList<>(savedState);
    }
}
