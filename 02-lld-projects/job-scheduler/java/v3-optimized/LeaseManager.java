/**
 * LeaseManager for job-scheduler (v3-optimized).
 */
public class LeaseManager {
    private final String id;

    public LeaseManager() {
        this.id = "LeaseManager";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "LeaseManager:" + id;
    }
}
