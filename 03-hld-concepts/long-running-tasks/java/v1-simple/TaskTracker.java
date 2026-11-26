import java.util.concurrent.*;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

public class TaskTracker {
    public enum TaskStatus {
        QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    }

    public static class TaskInfo {
        private final String taskId;
        private volatile TaskStatus status;
        private volatile int progress; // 0-100
        private volatile String result;
        private volatile String error;

        public TaskInfo(String taskId) {
            this.taskId = taskId;
            this.status = TaskStatus.QUEUED;
            this.progress = 0;
        }

        public String getTaskId() { return taskId; }
        public TaskStatus getStatus() { return status; }
        public int getProgress() { return progress; }
        public String getResult() { return result; }
        public String getError() { return error; }
    }

    private final Map<String, TaskInfo> tasks = new ConcurrentHashMap<>();
    private final Map<String, Future<?>> futures = new ConcurrentHashMap<>();
    private final ExecutorService executorService;

    public TaskTracker(int numWorkers) {
        this.executorService = Executors.newFixedThreadPool(numWorkers);
    }

    public interface TaskAction {
        String execute(TaskContext context) throws Exception;
    }

    public static class TaskContext {
        private final TaskInfo taskInfo;

        public TaskContext(TaskInfo taskInfo) {
            this.taskInfo = taskInfo;
        }

        public void setProgress(int progress) {
            if (progress < 0 || progress > 100) {
                throw new IllegalArgumentException("Progress must be between 0 and 100");
            }
            this.taskInfo.progress = progress;
        }

        public boolean isCancelled() {
            return Thread.currentThread().isInterrupted() || this.taskInfo.status == TaskStatus.CANCELLED;
        }

        public TaskInfo getTaskInfo() {
            return this.taskInfo;
        }
    }

    public String submitTask(TaskAction action, Consumer<TaskInfo> callback) {
        String taskId = UUID.randomUUID().toString();
        TaskInfo taskInfo = new TaskInfo(taskId);
        tasks.put(taskId, taskInfo);

        Future<?> future = executorService.submit(() -> {
            try {
                if (taskInfo.status == TaskStatus.CANCELLED) {
                    return;
                }
                taskInfo.status = TaskStatus.RUNNING;
                TaskContext context = new TaskContext(taskInfo);

                String result = action.execute(context);

                if (taskInfo.status == TaskStatus.CANCELLED || Thread.currentThread().isInterrupted()) {
                    taskInfo.status = TaskStatus.CANCELLED;
                } else {
                    taskInfo.result = result;
                    taskInfo.progress = 100;
                    taskInfo.status = TaskStatus.COMPLETED;
                }
            } catch (InterruptedException e) {
                taskInfo.status = TaskStatus.CANCELLED;
                Thread.currentThread().interrupt(); // Restore interrupted status
            } catch (Exception e) {
                taskInfo.error = e.getMessage();
                taskInfo.status = TaskStatus.FAILED;
            } finally {
                futures.remove(taskId);
                if (callback != null) {
                    callback.accept(taskInfo);
                }
            }
        });

        futures.put(taskId, future);
        return taskId;
    }

    public TaskInfo getTaskInfo(String taskId) {
        return tasks.get(taskId);
    }

    public boolean cancelTask(String taskId) {
        TaskInfo info = tasks.get(taskId);
        if (info == null) return false;

        Future<?> future = futures.get(taskId);
        if (future != null) {
            info.status = TaskStatus.CANCELLED;
            boolean cancelled = future.cancel(true);
            return cancelled;
        }
        return false;
    }

    public void shutdown() {
        executorService.shutdownNow();
    }
}