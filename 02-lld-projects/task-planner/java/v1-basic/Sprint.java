import java.util.ArrayList;
import java.util.List;

public class Sprint {
    private final String id;
    private final String name;
    private SprintStatus status;
    private final List<Task> tasks;

    public Sprint(String id, String name) {
        this.id = id;
        this.name = name;
        this.status = SprintStatus.CREATED;
        this.tasks = new ArrayList<>();
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public SprintStatus getStatus() {
        return status;
    }

    public void setStatus(SprintStatus status) {
        this.status = status;
    }

    public List<Task> getTasks() {
        return tasks;
    }

    public void addTask(Task task) {
        if (status == SprintStatus.COMPLETED) {
            throw new IllegalStateException("Cannot add task to a completed sprint.");
        }
        tasks.add(task);
    }

    public void removeTask(Task task) {
        tasks.remove(task);
    }
}
