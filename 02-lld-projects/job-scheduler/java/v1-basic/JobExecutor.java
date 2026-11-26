package v1_basic;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

class QueueItem implements Comparable<QueueItem> {
    private final Job job;
    private final long executionTimeMs;

    public QueueItem(Job job, long executionTimeMs) {
        this.job = job;
        this.executionTimeMs = executionTimeMs;
    }

    public Job getJob() { return job; }
    public long getExecutionTimeMs() { return executionTimeMs; }

    @Override
    public int compareTo(QueueItem o) {
        int cmp = Long.compare(this.executionTimeMs, o.executionTimeMs);
        if (cmp == 0) {
            return this.job.getId().compareTo(o.job.getId());
        }
        return cmp;
    }
}

public class JobExecutor {
    private final JobStore jobStore;
    private final Clock clock;
    private final PriorityBlockingQueue<QueueItem> queue;
    private final int capacity;
    private final int maxWorkers;
    private volatile boolean running = false;
    private final List<Thread> workerThreads = new ArrayList<>();
    private Consumer<Job> jobCompletionCallback;
    private final Object lock = new Object();

    public JobExecutor() {
        this(new InMemoryJobStore(), new SystemClock(), 1000, 1);
    }

    public JobExecutor(JobStore jobStore, Clock clock, int capacity, int maxWorkers) {
        this.jobStore = jobStore;
        this.clock = clock;
        this.capacity = capacity;
        this.maxWorkers = maxWorkers;
        this.queue = new PriorityBlockingQueue<>();
    }

    public void start() {
        synchronized (lock) {
            if (running) return;
            running = true;
            for (int i = 0; i < maxWorkers; i++) {
                Thread workerThread = new Thread(this::workerLoop, "Worker-" + i);
                workerThread.setDaemon(true);
                workerThread.start();
                workerThreads.add(workerThread);
            }
        }
    }

    public void stop() {
        synchronized (lock) {
            running = false;
            lock.notifyAll();
            for (Thread t : workerThreads) {
                t.interrupt();
            }
        }
        for (Thread t : workerThreads) {
            try {
                t.join(5000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        workerThreads.clear();
    }

    public void submit(Job job) {
        synchronized (lock) {
            if (queue.size() >= capacity) {
                throw new IllegalStateException("Queue is full");
            }
            QueueItem item = new QueueItem(job, job.getNextExecutionTime());
            queue.offer(item);
            
            QueueItem peek = queue.peek();
            if (peek != null && peek.getJob().getId().equals(job.getId())) {
                lock.notify();
            }
        }
    }

    public void setJobCompletionCallback(Consumer<Job> callback) {
        this.jobCompletionCallback = callback;
    }

    private void workerLoop() {
        while (running) {
            Job jobToExecute = null;
            synchronized (lock) {
                if (!running) break;

                QueueItem peek = queue.peek();
                if (peek == null) {
                    try {
                        lock.wait(100);
                    } catch (InterruptedException e) {
                        continue;
                    }
                    continue;
                }

                long now = clock.now();
                if (peek.getExecutionTimeMs() > now) {
                    try {
                        long delay = peek.getExecutionTimeMs() - now;
                        lock.wait(Math.min(delay, 100)); // wait up to 100ms or delay
                    } catch (InterruptedException e) {
                        continue;
                    }
                    continue;
                }

                // Ready to execute
                QueueItem item = queue.poll();
                if (item != null) {
                    Job job = item.getJob();
                    if (job.getStatus() == JobStatus.CANCELLED) {
                        continue; // drop cancelled
                    }
                    if (job.getStatus() != JobStatus.SCHEDULED && job.getStatus() != JobStatus.RETRYING) {
                        continue; // prevent concurrent execution
                    }
                    
                    job.setStatus(JobStatus.RUNNING);
                    job.addHistory("Started execution at " + clock.now());
                    jobStore.saveJob(job);
                    jobToExecute = job;
                }
            }

            if (jobToExecute != null) {
                executeJob(jobToExecute);
            }
        }
    }

    private void executeJob(Job job) {
        try {
            job.getAction().run();
            synchronized (lock) {
                job.setStatus(JobStatus.SUCCEEDED);
                job.addHistory("Execution succeeded at " + clock.now());
                job.resetRetryCount();
            }
        } catch (Exception e) {
            synchronized (lock) {
                job.incrementRetryCount();
                if (job.getRetryCount() <= job.getRetryPolicy().getMaxRetries()) {
                    job.setStatus(JobStatus.RETRYING);
                    job.addHistory("Execution failed at " + clock.now() + ", retrying");
                    long delay = job.getBackoffDelayMs();
                    job.setNextExecutionTime(clock.now() + delay);
                    jobStore.saveJob(job);
                    try {
                        submit(job);
                    } catch (IllegalStateException ise) {
                        // queue full, drop retry for basic version
                    }
                    return;
                } else {
                    job.setStatus(JobStatus.FAILED);
                    job.addHistory("Execution failed permanently at " + clock.now());
                }
            }
        }

        jobStore.saveJob(job);

        if (job.getCronExpression() != null && (job.getStatus() == JobStatus.SUCCEEDED || job.getStatus() == JobStatus.FAILED)) {
            try {
                long nextTime = CronParser.getNextExecutionTime(job.getCronExpression(), clock.now());
                job.setNextExecutionTime(nextTime);
                job.setStatus(JobStatus.SCHEDULED);
                jobStore.saveJob(job);
                submit(job);
            } catch (Exception e) {
                // Invalid cron
            }
        }

        if (jobCompletionCallback != null && (job.getStatus() == JobStatus.SUCCEEDED || job.getStatus() == JobStatus.FAILED)) {
            jobCompletionCallback.accept(job);
        }
    }

    public String describe() {
        return "JobExecutor: [running=" + running + ", queue_size=" + queue.size() + "]";
    }
}
