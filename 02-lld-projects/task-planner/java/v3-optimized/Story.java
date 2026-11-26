package v3_optimized;

import java.util.ArrayList;
import java.util.List;

public class Story extends Task {
    private final List<Subtask> subtasks;

    public Story(String id, String title, int storyPoints) {
        super(id, title, TaskType.STORY, storyPoints);
        this.subtasks = new ArrayList<>();
    }

    public void addSubtask(Subtask subtask) {
        subtasks.add(subtask);
    }

    public List<Subtask> getSubtasks() {
        return subtasks;
    }

    @Override
    public void setStatus(TaskStatus status) {
        if (status == TaskStatus.DONE) {
            for (Subtask subtask : subtasks) {
                if (subtask.getStatus() != TaskStatus.DONE) {
                    throw new IllegalStateException("Cannot mark Story as DONE while there are pending Subtasks.");
                }
            }
        }
        super.setStatus(status);
    }
}
