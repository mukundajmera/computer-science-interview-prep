import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

public class JobSchedulerService {

    public enum JobStatus {
        SCHEDULED, RUNNING, SUCCEEDED, FAILED, RETRYING, CANCELLED
    }

    public static class Job {
        private final String id;
        private final Runnable task;
        private final boolean periodic;
        private final long periodMs;
        private final int maxRetries;
        private final long initialBackoffMs;

        private final AtomicReference<JobStatus> status;
        private volatile int attempt = 0;

        public Job(Runnable task, boolean periodic, long periodMs, int maxRetries, long initialBackoffMs) {
            this.id = UUID.randomUUID().toString();
            this.task = task;
            this.periodic = periodic;
            this.periodMs = periodMs;
            this.maxRetries = maxRetries;
            this.initialBackoffMs = initialBackoffMs;
            this.status = new AtomicReference<>(JobStatus.SCHEDULED);
        }

        public String getId() { return id; }
        public JobStatus getStatus() { return status.get(); }
        public void setStatus(JobStatus newStatus) { this.status.set(newStatus); }
    }

    private static class JobExecution implements Comparable<JobExecution> {
        final Job job;
        final long scheduledTimeMs;

        JobExecution(Job job, long scheduledTimeMs) {
            this.job = job;
            this.scheduledTimeMs = scheduledTimeMs;
        }

        @Override
        public int compareTo(JobExecution o) {
            return Long.compare(this.scheduledTimeMs, o.scheduledTimeMs);
        }
    }

    private final PriorityBlockingQueue<JobExecution> queue = new PriorityBlockingQueue<>();
    private final ConcurrentHashMap<String, Job> jobs = new ConcurrentHashMap<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final AtomicBoolean isRunning = new AtomicBoolean(true);
    private final Thread dispatcher;
    private final Object lock = new Object();

    public JobSchedulerService() {
        dispatcher = new Thread(() -> {
            while (isRunning.get() && !Thread.currentThread().isInterrupted()) {
                JobExecution execution = queue.peek();
                long now = System.currentTimeMillis();

                if (execution != null && execution.scheduledTimeMs <= now) {
                    if (queue.remove(execution)) {
                        dispatch(execution);
                    }
                } else {
                    synchronized (lock) {
                        try {
                            execution = queue.peek();
                            if (execution != null) {
                                long timeToWait = execution.scheduledTimeMs - System.currentTimeMillis();
                                if (timeToWait > 0) {
                                    lock.wait(timeToWait);
                                }
                            } else {
                                lock.wait();
                            }
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                    }
                }
            }
        });
        dispatcher.start();
    }

    public String submitOneOffJob(Runnable task, long delayMs, int maxRetries, long initialBackoffMs) {
        Job job = new Job(task, false, 0, maxRetries, initialBackoffMs);
        return scheduleJob(job, System.currentTimeMillis() + delayMs);
    }

    public String submitPeriodicJob(Runnable task, long initialDelayMs, long periodMs, int maxRetries, long initialBackoffMs) {
        Job job = new Job(task, true, periodMs, maxRetries, initialBackoffMs);
        return scheduleJob(job, System.currentTimeMillis() + initialDelayMs);
    }

    private String scheduleJob(Job job, long timeMs) {
        jobs.put(job.getId(), job);
        queue.put(new JobExecution(job, timeMs));
        synchronized (lock) {
            lock.notifyAll();
        }
        return job.getId();
    }

    public boolean cancelJob(String jobId) {
        Job job = jobs.get(jobId);
        if (job != null) {
            JobStatus current = job.getStatus();
            if (current != JobStatus.SUCCEEDED && current != JobStatus.FAILED && current != JobStatus.CANCELLED) {
                job.setStatus(JobStatus.CANCELLED);
                return true;
            }
        }
        return false;
    }

    public JobStatus getJobStatus(String jobId) {
        Job job = jobs.get(jobId);
        return job != null ? job.getStatus() : null;
    }

    private void dispatch(JobExecution execution) {
        Job job = execution.job;
        if (job.getStatus() == JobStatus.CANCELLED) {
            return;
        }

        job.setStatus(JobStatus.RUNNING);
        executor.submit(() -> {
            if (job.getStatus() == JobStatus.CANCELLED) return;

            try {
                job.task.run();
                job.attempt = 0; // reset attempts on success

                if (job.periodic) {
                    if (job.getStatus() != JobStatus.CANCELLED) {
                        job.setStatus(JobStatus.SCHEDULED);
                        scheduleJob(job, System.currentTimeMillis() + job.periodMs);
                    }
                } else {
                    job.setStatus(JobStatus.SUCCEEDED);
                }
            } catch (Exception e) {
                job.attempt++;
                if (job.attempt <= job.maxRetries) {
                    if (job.getStatus() != JobStatus.CANCELLED) {
                        job.setStatus(JobStatus.RETRYING);
                        long backoff = job.initialBackoffMs * (1L << (job.attempt - 1)); // Exponential backoff
                        scheduleJob(job, System.currentTimeMillis() + backoff);
                    }
                } else {
                    job.setStatus(JobStatus.FAILED);
                }
            }
        });
    }

    public void shutdown() {
        isRunning.set(false);
        dispatcher.interrupt();
        executor.shutdown();
        try {
            if (!executor.awaitTermination(2, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
