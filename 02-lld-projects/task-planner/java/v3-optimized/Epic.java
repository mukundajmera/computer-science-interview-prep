package v3_optimized;

import java.util.ArrayList;
import java.util.List;

public class Epic extends Task {
    private final List<Task> children;

    public Epic(String id, String title, int storyPoints) {
        super(id, title, TaskType.EPIC, storyPoints);
        this.children = new ArrayList<>();
    }

    public void addChild(Task task) {
        if (task.getType() == TaskType.STORY || task.getType() == TaskType.FEATURE || task.getType() == TaskType.BUG) {
            this.children.add(task);
        } else {
            throw new IllegalArgumentException("Epic can only contain Story, Feature, or Bug.");
        }
    }

    public List<Task> getChildren() {
        return children;
    }
}
