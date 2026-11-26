/**
 * JobScheduler for job-scheduler (v2-extended).
 */
public class JobScheduler {
    private final String id;

    public JobScheduler() {
        this.id = "JobScheduler";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "JobScheduler:" + id;
    }
}
