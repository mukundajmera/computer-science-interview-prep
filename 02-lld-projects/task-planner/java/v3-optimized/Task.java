package v3_optimized;

import java.util.ArrayList;
import java.util.List;

public abstract class Task {
    private String id;
    private String title;
    private TaskType type;
    private TaskStatus status;
    private String assignee;
    private int storyPoints;
    private final List<Task> dependencies;

    public Task(String id, String title, TaskType type, int storyPoints) {
        this.id = id;
        this.title = title;
        this.type = type;
        this.storyPoints = storyPoints;
        this.status = TaskStatus.OPEN;
        this.dependencies = new ArrayList<>();
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public TaskType getType() {
        return type;
    }

    public TaskStatus getStatus() {
        return status;
    }

    public void setStatus(TaskStatus status) {
        if (status == TaskStatus.DONE) {
            for (Task dep : dependencies) {
                if (dep.getStatus() != TaskStatus.DONE) {
                    throw new IllegalStateException("Cannot mark as DONE. Dependency " + dep.getId() + " is not DONE.");
                }
            }
        }
        this.status = status;
    }

    public String getAssignee() {
        return assignee;
    }

    public void setAssignee(String assignee) {
        this.assignee = assignee;
    }

    public int getStoryPoints() {
        return storyPoints;
    }

    public void setStoryPoints(int storyPoints) {
        this.storyPoints = storyPoints;
    }
    
    public List<Task> getDependencies() {
        return dependencies;
    }
    
    public void addDependency(Task task) {
        this.dependencies.add(task);
    }
}
