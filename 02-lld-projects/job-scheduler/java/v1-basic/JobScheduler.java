package v1_basic;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public class JobScheduler {
    private final JobStore jobStore;
    private final JobExecutor executor;
    private final Clock clock;
    
    // Reverse dependency map
    private final Map<String, List<String>> dependentJobs = new ConcurrentHashMap<>();
    private final Object lock = new Object();

    public JobScheduler() {
        this(new InMemoryJobStore(), new SystemClock(), 1000, 1);
    }

    public JobScheduler(JobStore jobStore, Clock clock, int executorCapacity, int maxWorkers) {
        this(jobStore, clock, new JobExecutor(jobStore, clock, executorCapacity, maxWorkers));
    }

    public JobScheduler(JobStore jobStore, Clock clock, JobExecutor executor) {
        this.jobStore = jobStore;
        this.clock = clock;
        this.executor = executor;
        this.executor.setJobCompletionCallback(this::onJobCompleted);
    }

    public void start() {
        executor.start();
    }

    public void stop() {
        executor.stop();
    }

    public boolean cancelJob(String jobId) {
        synchronized (lock) {
            Job job = jobStore.getJob(jobId);
            if (job == null) return false;
            
            JobStatus status = job.getStatus();
            if (status == JobStatus.CREATED || status == JobStatus.SCHEDULED || status == JobStatus.RETRYING) {
                job.setStatus(JobStatus.CANCELLED);
                job.addHistory("Cancelled at " + clock.now());
                jobStore.saveJob(job);
                return true;
            }
            return false;
        }
    }

    public void scheduleJob(Job job) {
        synchronized (lock) {
            for (String depId : job.getDependencies()) {
                if (jobStore.getJob(depId) == null) {
                    throw new IllegalArgumentException("Missing dependency: " + depId);
                }
            }

            jobStore.saveJob(job);
            if (hasCycle(job.getId())) {
                jobStore.removeJob(job.getId());
                throw new IllegalArgumentException("Cycle detected in job dependencies");
            }

            for (String depId : job.getDependencies()) {
                dependentJobs.computeIfAbsent(depId, k -> new CopyOnWriteArrayList<>()).add(job.getId());
            }

            if (job.getCronExpression() != null && !job.getCronExpression().isEmpty()) {
                job.setNextExecutionTime(CronParser.getNextExecutionTime(job.getCronExpression(), clock.now()));
            } else if (job.getNextExecutionTime() == 0) {
                job.setNextExecutionTime(clock.now());
            }

            if (areDependenciesMet(job)) {
                job.setStatus(JobStatus.SCHEDULED);
                jobStore.saveJob(job);
                executor.submit(job);
            } else {
                job.setStatus(JobStatus.CREATED);
                jobStore.saveJob(job);
            }
        }
    }

    private boolean hasCycle(String startJobId) {
        Set<String> visited = new HashSet<>();
        Set<String> stack = new HashSet<>();

        for (Job job : jobStore.getAllJobs()) {
            if (dfs(job.getId(), visited, stack)) {
                return true;
            }
        }
        return false;
    }

    private boolean dfs(String jobId, Set<String> visited, Set<String> stack) {
        if (stack.contains(jobId)) return true;
        if (visited.contains(jobId)) return false;

        visited.add(jobId);
        stack.add(jobId);

        Job job = jobStore.getJob(jobId);
        if (job != null) {
            for (String depId : job.getDependencies()) {
                if (dfs(depId, visited, stack)) {
                    return true;
                }
            }
        }

        stack.remove(jobId);
        return false;
    }

    private boolean areDependenciesMet(Job job) {
        for (String depId : job.getDependencies()) {
            Job depJob = jobStore.getJob(depId);
            if (depJob == null || depJob.getStatus() != JobStatus.SUCCEEDED) {
                return false;
            }
        }
        return true;
    }

    private void onJobCompleted(Job completedJob) {
        if (completedJob.getStatus() == JobStatus.SUCCEEDED) {
            synchronized (lock) {
                List<String> dependents = dependentJobs.getOrDefault(completedJob.getId(), Collections.emptyList());
                for (String childId : dependents) {
                    Job childJob = jobStore.getJob(childId);
                    if (childJob != null && childJob.getStatus() == JobStatus.CREATED) {
                        if (areDependenciesMet(childJob)) {
                            childJob.setStatus(JobStatus.SCHEDULED);
                            jobStore.saveJob(childJob);
                            executor.submit(childJob);
                        }
                    }
                }
            }
        }
    }

    public Job getJob(String jobId) {
        return jobStore.getJob(jobId);
    }
    
    public JobExecutor getExecutor() {
        return executor;
    }

    public String describe() {
        return "JobScheduler: [store=" + ((InMemoryJobStore)jobStore).describe() + ", executor=" + executor.describe() + "]";
    }
    
    // Expose for id verification in tests
    public String getId() {
        return "JobScheduler";
    }
}
