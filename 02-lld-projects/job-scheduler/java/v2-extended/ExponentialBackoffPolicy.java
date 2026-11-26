/**
 * ExponentialBackoffPolicy for job-scheduler (v2-extended).
 */
public class ExponentialBackoffPolicy {
    private final String id;

    public ExponentialBackoffPolicy() {
        this.id = "ExponentialBackoffPolicy";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "ExponentialBackoffPolicy:" + id;
    }
}
