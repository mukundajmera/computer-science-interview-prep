package v3_optimized;

public class Subtask extends Task {
    private final Story parent;

    public Subtask(String id, String title, Story parent, int storyPoints) {
        super(id, title, TaskType.SUBTASK, storyPoints);
        this.parent = parent;
    }

    public Story getParent() {
        return parent;
    }
}
