import java.util.concurrent.*;
import java.util.*;

public class ScaledJobSchedulerService {

    public enum JobStatus {
        SCHEDULED, RUNNING, SUCCEEDED, FAILED, RETRYING, CANCELLED, PAUSED, DEAD_LETTER, WAITING_DEPENDENCIES
    }

    public static class Job {
        public String id;
        public Runnable task;
        public boolean periodic;
        public long periodMs;
        public int maxRetries;
        public long initialBackoffMs;
        public Set<String> dependencies;

        public JobStatus status;
        public int attempt;
        public String leaseOwner;
        public long leaseUntil;

        public Job(Runnable task, boolean periodic, long periodMs, int maxRetries, long initialBackoffMs, List<String> dependencies) {
            this.id = UUID.randomUUID().toString();
            this.task = task;
            this.periodic = periodic;
            this.periodMs = periodMs;
            this.maxRetries = maxRetries;
            this.initialBackoffMs = initialBackoffMs;
            this.dependencies = dependencies != null ? new HashSet<>(dependencies) : new HashSet<>();

            this.status = this.dependencies.isEmpty() ? JobStatus.SCHEDULED : JobStatus.WAITING_DEPENDENCIES;
            this.attempt = 0;
            this.leaseOwner = null;
            this.leaseUntil = 0;
        }
    }

    private static class JobExecution implements Comparable<JobExecution> {
        public Job job;
        public long scheduledTimeMs;

        public JobExecution(Job job, long scheduledTimeMs) {
            this.job = job;
            this.scheduledTimeMs = scheduledTimeMs;
        }

        @Override
        public int compareTo(JobExecution other) {
            return Long.compare(this.scheduledTimeMs, other.scheduledTimeMs);
        }
    }

    private final PriorityQueue<JobExecution> queue;
    private final Map<String, Job> jobs;
    private final Map<String, Long> workers;
    private volatile boolean isRunning;
    private final Object lock;
    private final long leaseDurationMs;
    private final List<String> deadLetterQueue;

    private Thread dispatcherThread;
    private Thread coordinatorThread;

    public ScaledJobSchedulerService() {
        this(5000);
    }

    public ScaledJobSchedulerService(long leaseDurationMs) {
        this.queue = new PriorityQueue<>();
        this.jobs = new HashMap<>();
        this.workers = new HashMap<>();
        this.isRunning = true;
        this.lock = new Object();
        this.leaseDurationMs = leaseDurationMs;
        this.deadLetterQueue = new ArrayList<>();

        this.dispatcherThread = new Thread(this::dispatchLoop);
        this.dispatcherThread.setDaemon(true);
        this.dispatcherThread.start();

        this.coordinatorThread = new Thread(this::coordinatorLoop);
        this.coordinatorThread.setDaemon(true);
        this.coordinatorThread.start();
    }

    public String submitOneOffJob(Runnable task, long delayMs, int maxRetries, long initialBackoffMs) {
        return submitOneOffJob(task, delayMs, maxRetries, initialBackoffMs, null);
    }

    public String submitOneOffJob(Runnable task, long delayMs, int maxRetries, long initialBackoffMs, List<String> dependencies) {
        Job job = new Job(task, false, 0, maxRetries, initialBackoffMs, dependencies);
        long scheduledTime = System.currentTimeMillis() + delayMs;
        synchronized (lock) {
            jobs.put(job.id, job);
            checkDependenciesAndSchedule(job, scheduledTime);
        }
        return job.id;
    }

    public String submitPeriodicJob(Runnable task, long initialDelayMs, long periodMs, int maxRetries, long initialBackoffMs) {
        Job job = new Job(task, true, periodMs, maxRetries, initialBackoffMs, null);
        long scheduledTime = System.currentTimeMillis() + initialDelayMs;
        synchronized (lock) {
            jobs.put(job.id, job);
            checkDependenciesAndSchedule(job, scheduledTime);
        }
        return job.id;
    }

    private void checkDependenciesAndSchedule(Job job, long scheduledTimeMs) {
        if (job.dependencies.isEmpty()) {
            if (job.status == JobStatus.WAITING_DEPENDENCIES) {
                job.status = JobStatus.SCHEDULED;
            }
            queue.add(new JobExecution(job, scheduledTimeMs));
            lock.notifyAll();
        } else {
            boolean allMet = true;
            for (String depId : job.dependencies) {
                Job depJob = jobs.get(depId);
                if (depJob == null || depJob.status != JobStatus.SUCCEEDED) {
                    allMet = false;
                    break;
                }
            }
            if (allMet) {
                job.status = JobStatus.SCHEDULED;
                queue.add(new JobExecution(job, scheduledTimeMs));
                lock.notifyAll();
            }
        }
    }

    public boolean cancelJob(String jobId) {
        synchronized (lock) {
            Job job = jobs.get(jobId);
            if (job != null && job.status != JobStatus.SUCCEEDED && job.status != JobStatus.FAILED && job.status != JobStatus.CANCELLED) {
                job.status = JobStatus.CANCELLED;
                return true;
            }
        }
        return false;
    }

    public boolean pauseJob(String jobId) {
        synchronized (lock) {
            Job job = jobs.get(jobId);
            if (job != null && (job.status == JobStatus.SCHEDULED || job.status == JobStatus.WAITING_DEPENDENCIES || job.status == JobStatus.RETRYING)) {
                job.status = JobStatus.PAUSED;
                return true;
            }
        }
        return false;
    }

    public boolean resumeJob(String jobId) {
        synchronized (lock) {
            Job job = jobs.get(jobId);
            if (job != null && job.status == JobStatus.PAUSED) {
                if (!job.dependencies.isEmpty()) {
                    job.status = JobStatus.WAITING_DEPENDENCIES;
                } else {
                    job.status = JobStatus.SCHEDULED;
                }
                checkDependenciesAndSchedule(job, System.currentTimeMillis());
                return true;
            }
        }
        return false;
    }

    public JobStatus getJobStatus(String jobId) {
        synchronized (lock) {
            Job job = jobs.get(jobId);
            return job != null ? job.status : null;
        }
    }

    public List<String> getDeadLetterQueue() {
        synchronized (lock) {
            return new ArrayList<>(deadLetterQueue);
        }
    }

    public void registerWorker(String workerId) {
        synchronized (lock) {
            workers.put(workerId, System.currentTimeMillis());
        }
    }

    public void heartbeat(String workerId) {
        synchronized (lock) {
            if (workers.containsKey(workerId)) {
                workers.put(workerId, System.currentTimeMillis());
            }
        }
    }

    private void coordinatorLoop() {
        while (isRunning) {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }

            long now = System.currentTimeMillis();
            synchronized (lock) {
                List<String> deadWorkers = new ArrayList<>();
                for (Map.Entry<String, Long> entry : workers.entrySet()) {
                    if (now - entry.getValue() > leaseDurationMs * 2) {
                        deadWorkers.add(entry.getKey());
                    }
                }

                for (String wid : deadWorkers) {
                    workers.remove(wid);
                }

                for (Job job : jobs.values()) {
                    if (job.status == JobStatus.RUNNING) {
                        if (deadWorkers.contains(job.leaseOwner) || job.leaseUntil < now) {
                            job.status = JobStatus.RETRYING;
                            job.leaseOwner = null;
                            queue.add(new JobExecution(job, now));
                            lock.notifyAll();
                        }
                    }
                }
            }
        }
    }

    private void dispatchLoop() {
        while (isRunning) {
            synchronized (lock) {
                if (queue.isEmpty()) {
                    try {
                        lock.wait();
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    continue;
                }

                long now = System.currentTimeMillis();
                JobExecution execution = queue.peek();

                if (execution.scheduledTimeMs <= now) {
                    queue.poll();
                    executeJob(execution.job);
                } else {
                    long timeToWait = execution.scheduledTimeMs - now;
                    try {
                        lock.wait(timeToWait);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }
        }
    }

    private void executeJob(Job job) {
        if (job.status == JobStatus.CANCELLED || job.status == JobStatus.PAUSED || job.status == JobStatus.DEAD_LETTER || job.status == JobStatus.SUCCEEDED || job.status == JobStatus.FAILED) {
            return;
        }

        String workerId = null;
        if (!workers.isEmpty()) {
            workerId = workers.keySet().iterator().next();
        }

        job.status = JobStatus.RUNNING;
        job.leaseOwner = workerId;
        job.leaseUntil = System.currentTimeMillis() + leaseDurationMs;

        Thread runner = new Thread(() -> {
            try {
                job.task.run();
                synchronized (lock) {
                    if (job.status == JobStatus.RUNNING) {
                        job.attempt = 0;
                        job.leaseOwner = null;
                        if (job.periodic) {
                            job.status = JobStatus.SCHEDULED;
                            long nextTime = System.currentTimeMillis() + job.periodMs;
                            checkDependenciesAndSchedule(job, nextTime);
                        } else {
                            job.status = JobStatus.SUCCEEDED;
                            for (Job depJob : jobs.values()) {
                                if (depJob.dependencies.contains(job.id) && depJob.status == JobStatus.WAITING_DEPENDENCIES) {
                                    checkDependenciesAndSchedule(depJob, System.currentTimeMillis());
                                }
                            }
                        }
                    }
                }
            } catch (Exception e) {
                synchronized (lock) {
                    if (job.status == JobStatus.RUNNING) {
                        job.attempt++;
                        job.leaseOwner = null;
                        if (job.attempt <= job.maxRetries) {
                            job.status = JobStatus.RETRYING;
                            long backoff = job.initialBackoffMs * (1L << (job.attempt - 1));
                            long nextTime = System.currentTimeMillis() + backoff;
                            checkDependenciesAndSchedule(job, nextTime);
                        } else {
                            job.status = JobStatus.DEAD_LETTER;
                            deadLetterQueue.add(job.id);
                        }
                    }
                }
            }
        });
        runner.setDaemon(true);
        runner.start();
    }

    public void shutdown() {
        isRunning = false;
        synchronized (lock) {
            lock.notifyAll();
        }
    }
}
