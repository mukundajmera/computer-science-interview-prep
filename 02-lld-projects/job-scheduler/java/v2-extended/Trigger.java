/**
 * Trigger for job-scheduler (v2-extended).
 */
public class Trigger {
    private final String id;

    public Trigger() {
        this.id = "Trigger";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "Trigger:" + id;
    }
}
