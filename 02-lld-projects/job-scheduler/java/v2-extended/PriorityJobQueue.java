/**
 * PriorityJobQueue for job-scheduler (v2-extended).
 */
public class PriorityJobQueue {
    private final String id;

    public PriorityJobQueue() {
        this.id = "PriorityJobQueue";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "PriorityJobQueue:" + id;
    }
}
