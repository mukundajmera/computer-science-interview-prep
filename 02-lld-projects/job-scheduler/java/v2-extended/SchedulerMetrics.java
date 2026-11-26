/**
 * SchedulerMetrics for job-scheduler (v2-extended).
 */
public class SchedulerMetrics {
    private final String id;

    public SchedulerMetrics() {
        this.id = "SchedulerMetrics";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "SchedulerMetrics:" + id;
    }
}
