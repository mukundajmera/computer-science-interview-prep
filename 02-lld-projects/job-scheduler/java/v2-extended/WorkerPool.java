/**
 * WorkerPool for job-scheduler (v2-extended).
 */
public class WorkerPool {
    private final String id;

    public WorkerPool() {
        this.id = "WorkerPool";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "WorkerPool:" + id;
    }
}
