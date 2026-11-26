/**
 * ShardManager for job-scheduler (v3-optimized).
 */
public class ShardManager {
    private final String id;

    public ShardManager() {
        this.id = "ShardManager";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "ShardManager:" + id;
    }
}
