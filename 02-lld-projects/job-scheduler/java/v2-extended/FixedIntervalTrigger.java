/**
 * FixedIntervalTrigger for job-scheduler (v2-extended).
 */
public class FixedIntervalTrigger {
    private final String id;

    public FixedIntervalTrigger() {
        this.id = "FixedIntervalTrigger";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "FixedIntervalTrigger:" + id;
    }
}
