/**
 * OneTimeTrigger for job-scheduler (v2-extended).
 */
public class OneTimeTrigger {
    private final String id;

    public OneTimeTrigger() {
        this.id = "OneTimeTrigger";
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "OneTimeTrigger:" + id;
    }
}
