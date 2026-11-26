public class Subtask extends Task {
    private final Story parent;

    public Subtask(String id, String title, Story parent) {
        super(id, title, TaskType.SUBTASK);
        this.parent = parent;
    }

    public Story getParent() {
        return parent;
    }
}
