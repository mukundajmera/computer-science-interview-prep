package v3_optimized;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class TaskPlannerService {
    private final Map<String, Task> tasks;
    private final Map<String, Sprint> sprints;
    private Sprint activeSprint;
    private final List<Task> backlog;

    public TaskPlannerService() {
        this.tasks = new HashMap<>();
        this.sprints = new HashMap<>();
        this.activeSprint = null;
        this.backlog = new ArrayList<>();
    }

    public Task createTask(String id, String title, TaskType type, int storyPoints) {
        if (tasks.containsKey(id)) {
            throw new IllegalArgumentException("Task with id " + id + " already exists.");
        }
        Task task;
        if (type == TaskType.EPIC) {
            task = new Epic(id, title, storyPoints);
        } else if (type == TaskType.STORY) {
            task = new Story(id, title, storyPoints);
        } else if (type == TaskType.SUBTASK) {
            throw new IllegalArgumentException("Subtasks must be created using createSubtask.");
        } else {
            task = new Task(id, title, type, storyPoints) {};
        }
        tasks.put(id, task);
        backlog.add(task);
        return task;
    }

    public void addToEpic(String epicId, String childId) {
        Task epicTask = tasks.get(epicId);
        Task child = tasks.get(childId);
        if (!(epicTask instanceof Epic)) {
            throw new IllegalArgumentException("Parent must be an Epic.");
        }
        if (child == null) {
            throw new IllegalArgumentException("Child task not found.");
        }
        ((Epic) epicTask).addChild(child);
    }

    public Subtask createSubtask(String id, String title, String storyId, int storyPoints) {
        Task parent = tasks.get(storyId);
        if (!(parent instanceof Story)) {
            throw new IllegalArgumentException("Parent must be a Story.");
        }
        Story story = (Story) parent;
        Subtask subtask = new Subtask(id, title, story, storyPoints);
        tasks.put(id, subtask);
        story.addSubtask(subtask);
        return subtask;
    }

    public void addDependency(String taskId, String dependsOnId) {
        Task task = tasks.get(taskId);
        Task dependsOn = tasks.get(dependsOnId);
        if (task == null || dependsOn == null) {
            throw new IllegalArgumentException("Invalid task ID(s).");
        }
        
        if (hasCycle(taskId, dependsOnId)) {
            throw new IllegalStateException("Adding dependency " + taskId + " -> " + dependsOnId + " would create a cycle.");
        }
        
        task.addDependency(dependsOn);
    }

    private boolean hasCycle(String fromTaskId, String toTaskId) {
        Set<String> visited = new HashSet<>();
        return dfs(toTaskId, fromTaskId, visited);
    }

    private boolean dfs(String currentId, String targetId, Set<String> visited) {
        if (currentId.equals(targetId)) {
            return true;
        }
        if (visited.contains(currentId)) {
            return false;
        }
        visited.add(currentId);
        Task currentTask = tasks.get(currentId);
        if (currentTask != null) {
            for (Task dep : currentTask.getDependencies()) {
                if (dfs(dep.getId(), targetId, visited)) {
                    return true;
                }
            }
        }
        return false;
    }

    public Sprint createSprint(String id, String name) {
        if (sprints.containsKey(id)) {
            throw new IllegalArgumentException("Sprint with id " + id + " already exists.");
        }
        Sprint sprint = new Sprint(id, name);
        sprints.put(id, sprint);
        return sprint;
    }

    public void addTaskToSprint(String taskId, String sprintId) {
        Task task = tasks.get(taskId);
        Sprint sprint = sprints.get(sprintId);
        if (task == null || sprint == null) {
            throw new IllegalArgumentException("Invalid task or sprint ID.");
        }
        
        sprint.addTask(task);
        backlog.remove(task);
    }

    public void startSprint(String sprintId) {
        if (activeSprint != null) {
            throw new IllegalStateException("Another sprint is already active.");
        }
        Sprint sprint = sprints.get(sprintId);
        if (sprint == null) {
            throw new IllegalArgumentException("Sprint not found.");
        }
        if (sprint.getStatus() != SprintStatus.CREATED) {
            throw new IllegalStateException("Can only start a created sprint.");
        }
        sprint.setStatus(SprintStatus.ACTIVE);
        activeSprint = sprint;
    }

    public void completeSprint(String sprintId, String rolloverSprintId) {
        Sprint sprint = sprints.get(sprintId);
        if (sprint == null || sprint != activeSprint) {
            throw new IllegalArgumentException("Sprint is not active.");
        }
        
        sprint.setStatus(SprintStatus.COMPLETED);
        activeSprint = null;
        
        List<Task> unfinishedTasks = sprint.getTasks().stream()
            .filter(t -> t.getStatus() != TaskStatus.DONE)
            .collect(Collectors.toList());
            
        if (rolloverSprintId != null) {
            Sprint nextSprint = sprints.get(rolloverSprintId);
            if (nextSprint == null) {
                throw new IllegalArgumentException("Rollover sprint not found.");
            }
            for (Task t : unfinishedTasks) {
                nextSprint.addTask(t);
            }
        } else {
            backlog.addAll(unfinishedTasks);
        }
    }

    public void changeTaskStatus(String taskId, TaskStatus status) {
        Task task = tasks.get(taskId);
        if (task == null) {
            throw new IllegalArgumentException("Task not found.");
        }
        task.setStatus(status);
    }

    public List<Task> getDelayedTasks() {
        List<Task> delayedTasks = new ArrayList<>();
        for (Sprint sprint : sprints.values()) {
            if (sprint.getStatus() == SprintStatus.COMPLETED) {
                for (Task task : sprint.getTasks()) {
                    if (task.getStatus() != TaskStatus.DONE) {
                        delayedTasks.add(task);
                    }
                }
            }
        }
        return delayedTasks;
    }
}
