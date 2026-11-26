package v3_optimized;

public class SnapshotReplayManager {
    private int snapshotVersion = 0;

    public void takeSnapshot() {
        snapshotVersion++;
    }
}
