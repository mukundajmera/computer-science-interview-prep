/**
 * DeadLetterQueue for job-scheduler (v3-optimized).
 */
public class DeadLetterQueue {
    private final String id;

    public DeadLetterQueue() {
        this.id = "DeadLetterQueue";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "DeadLetterQueue:" + id;
    }
}
