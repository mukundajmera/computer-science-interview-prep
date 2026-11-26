package v1_basic;

import java.util.ArrayList;
import java.util.List;

public class Job {
    private final String id;
    private final Runnable action;
    private final String cronExpression;
    private final RetryPolicy retryPolicy;
    private final List<String> dependencies;
    
    private JobStatus status = JobStatus.CREATED;
    private long nextExecutionTime = 0;
    private int retryCount = 0;
    private final List<String> executionHistory = new ArrayList<>();

    public Job() {
        this("job", () -> {}, null, null, null);
    }

    public Job(String id, Runnable action, String cronExpression, RetryPolicy retryPolicy) {
        this(id, action, cronExpression, retryPolicy, null);
    }

    public Job(String id, Runnable action, String cronExpression, RetryPolicy retryPolicy, List<String> dependencies) {
        this.id = id;
        this.action = action;
        this.cronExpression = cronExpression;
        this.retryPolicy = retryPolicy != null ? retryPolicy : new RetryPolicy(0, 1000, 2.0);
        this.dependencies = dependencies != null ? new ArrayList<>(dependencies) : new ArrayList<>();
    }

    public String getId() { return id; }
    public Runnable getAction() { return action; }
    public String getCronExpression() { return cronExpression; }
    public RetryPolicy getRetryPolicy() { return retryPolicy; }
    public List<String> getDependencies() { return new ArrayList<>(dependencies); }

    public synchronized JobStatus getStatus() { return status; }
    public synchronized void setStatus(JobStatus status) { this.status = status; }

    public synchronized long getNextExecutionTime() { return nextExecutionTime; }
    public synchronized void setNextExecutionTime(long nextExecutionTime) { this.nextExecutionTime = nextExecutionTime; }

    public synchronized int getRetryCount() { return retryCount; }
    public synchronized void incrementRetryCount() { this.retryCount++; }
    public synchronized void resetRetryCount() { this.retryCount = 0; }

    public synchronized long getBackoffDelayMs() {
        if (retryCount == 0) return 0;
        return (long) (retryPolicy.getInitialBackoffMs() * Math.pow(retryPolicy.getMultiplier(), retryCount - 1));
    }

    public synchronized void addHistory(String entry) { this.executionHistory.add(entry); }
    public synchronized List<String> getExecutionHistory() { return new ArrayList<>(executionHistory); }

    public String describe() {
        return "Job:" + id + " [status=" + getStatus() + "]";
    }
}
