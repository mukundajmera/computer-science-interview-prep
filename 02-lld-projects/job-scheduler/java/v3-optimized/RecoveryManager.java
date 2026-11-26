/**
 * RecoveryManager for job-scheduler (v3-optimized).
 */
public class RecoveryManager {
    private final String id;

    public RecoveryManager() {
        this.id = "RecoveryManager";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "RecoveryManager:" + id;
    }
}
