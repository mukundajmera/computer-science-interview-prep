package v3_optimized;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

enum TaskState {
    PENDING, SCHEDULED, RUNNING, COMPLETED, FAILED
}

class DAGTask {
    String taskId;
    volatile Callable<Object> action;
    List<String> dependencies;
    int priority;
    TaskState state = TaskState.PENDING;
    ReentrantLock stateLock = new ReentrantLock();
    Condition completionCondition = stateLock.newCondition();
    Object result;
    Exception error;

    public DAGTask(String taskId, Callable<Object> action, List<String> dependencies, int priority) {
        this.taskId = taskId;
        this.action = action;
        this.dependencies = dependencies != null ? dependencies : new ArrayList<>();
        this.priority = priority;
    }

    public boolean transitionState(TaskState expectedCurrent, TaskState nextState) {
        stateLock.lock();
        try {
            if (this.state == expectedCurrent) {
                this.state = nextState;
                if (nextState == TaskState.COMPLETED || nextState == TaskState.FAILED) {
                    completionCondition.signalAll();
                }
                return true;
            }
            return false;
        } finally {
            stateLock.unlock();
        }
    }

    public TaskState waitForCompletion(long timeoutMs) throws InterruptedException {
        long nanos = TimeUnit.MILLISECONDS.toNanos(timeoutMs);
        stateLock.lock();
        try {
            while (this.state != TaskState.COMPLETED && this.state != TaskState.FAILED) {
                if (nanos <= 0) break;
                nanos = completionCondition.awaitNanos(nanos);
            }
            return this.state;
        } finally {
            stateLock.unlock();
        }
    }
}

class ScheduledTask implements Comparable<ScheduledTask> {
    long executeAt;
    DAGTask task;

    public ScheduledTask(long executeAt, DAGTask task) {
        this.executeAt = executeAt;
        this.task = task;
    }

    @Override
    public int compareTo(ScheduledTask other) {
        if (this.executeAt == other.executeAt) {
            return Integer.compare(this.task.priority, other.task.priority);
        }
        return Long.compare(this.executeAt, other.executeAt);
    }
}

class PriorityBlockingQueue {
    private final PriorityQueue<ScheduledTask> heap = new PriorityQueue<>();
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notEmpty = lock.newCondition();
    private boolean shutdown = false;

    public void put(ScheduledTask item) {
        lock.lock();
        try {
            if (shutdown) return;
            heap.offer(item);
            if (heap.peek() == item) {
                notEmpty.signalAll();
            }
        } finally {
            lock.unlock();
        }
    }

    public ScheduledTask take(Long timeoutMs) throws InterruptedException {
        lock.lockInterruptibly();
        try {
            long remainingNanos = timeoutMs != null ? TimeUnit.MILLISECONDS.toNanos(timeoutMs) : 0;
            while (true) {
                if (shutdown && heap.isEmpty()) {
                    return null;
                }

                if (heap.isEmpty()) {
                    if (timeoutMs != null) {
                        if (remainingNanos <= 0) {
                            return null;
                        }
                        remainingNanos = notEmpty.awaitNanos(remainingNanos);
                    } else {
                        notEmpty.await();
                    }
                    continue;
                }

                long now = System.currentTimeMillis();
                ScheduledTask topItem = heap.peek();
                long delayMs = topItem.executeAt - now;

                if (delayMs <= 0) {
                    return heap.poll();
                } else {
                    if (timeoutMs != null) {
                        long waitNanos = Math.min(remainingNanos, TimeUnit.MILLISECONDS.toNanos(delayMs));
                        if (waitNanos <= 0) return null;
                        remainingNanos -= (waitNanos - notEmpty.awaitNanos(waitNanos));
                    } else {
                        notEmpty.await(delayMs, TimeUnit.MILLISECONDS);
                    }
                }
            }
        } finally {
            lock.unlock();
        }
    }

    public void shutdown() {
        lock.lock();
        try {
            shutdown = true;
            notEmpty.signalAll();
        } finally {
            lock.unlock();
        }
    }
}

class ScheduledThreadPoolExecutor {
    private final int maxWorkers;
    private final PriorityBlockingQueue queue = new PriorityBlockingQueue();
    private final List<Thread> threads = new ArrayList<>();
    private volatile boolean isRunning = false;

    public ScheduledThreadPoolExecutor(int maxWorkers) {
        this.maxWorkers = maxWorkers;
    }

    public void start() {
        isRunning = true;
        for (int i = 0; i < maxWorkers; i++) {
            Thread t = new Thread(() -> workerLoop(), "Worker-" + i);
            t.setDaemon(true);
            t.start();
            threads.add(t);
        }
    }

    public void stop() throws InterruptedException {
        isRunning = false;
        queue.shutdown();
        for (Thread t : threads) {
            t.join();
        }
    }

    public void schedule(DAGTask task, long delayMs) {
        if (task.transitionState(TaskState.PENDING, TaskState.SCHEDULED)) {
            long executeAt = System.currentTimeMillis() + delayMs;
            queue.put(new ScheduledTask(executeAt, task));
        }
    }

    private void workerLoop() {
        while (isRunning) {
            try {
                ScheduledTask scheduledTask = queue.take(null);
                if (scheduledTask == null) {
                    break;
                }

                DAGTask task = scheduledTask.task;
                if (task.transitionState(TaskState.SCHEDULED, TaskState.RUNNING)) {
                    try {
                        task.result = task.action.call();
                        task.transitionState(TaskState.RUNNING, TaskState.COMPLETED);
                    } catch (Exception e) {
                        task.error = e;
                        task.transitionState(TaskState.RUNNING, TaskState.FAILED);
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}

class CompletionBarrier {
    private final AtomicInteger count;
    private final Runnable onComplete;

    public CompletionBarrier(int count, Runnable onComplete) {
        this.count = new AtomicInteger(count);
        this.onComplete = onComplete;
    }

    public void countDown() {
        if (count.decrementAndGet() == 0) {
            onComplete.run();
        }
    }
}

class DAGScheduler {
    private final ScheduledThreadPoolExecutor executor;
    private final Map<String, DAGTask> tasks = new HashMap<>();
    private final Map<String, List<DAGTask>> dependents = new HashMap<>();
    private final Map<String, CompletionBarrier> barriers = new HashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public DAGScheduler(ScheduledThreadPoolExecutor executor) {
        this.executor = executor;
    }

    public void addTask(DAGTask task) {
        lock.lock();
        try {
            tasks.put(task.taskId, task);
            dependents.putIfAbsent(task.taskId, new ArrayList<>());

            for (String depId : task.dependencies) {
                dependents.putIfAbsent(depId, new ArrayList<>());
                dependents.get(depId).add(task);
            }
        } finally {
            lock.unlock();
        }
    }

    public void submitDag() {
        List<DAGTask> tasksList;
        lock.lock();
        try {
            tasksList = new ArrayList<>(tasks.values());
            
            // First pass: wrap actions so they trigger dependents
            for (DAGTask task : tasksList) {
                Callable<Object> originalAction = task.action;
                task.action = () -> {
                    try {
                        Object res = originalAction.call();
                        onTaskCompleted(task, true);
                        return res;
                    } catch (Exception e) {
                        onTaskCompleted(task, false);
                        throw e;
                    }
                };
            }
            
            // Second pass: setup barriers and schedule independent tasks
            for (DAGTask task : tasksList) {
                int inDegree = task.dependencies.size();
                if (inDegree == 0) {
                    scheduleTask(task);
                } else {
                    barriers.put(task.taskId, new CompletionBarrier(inDegree, () -> scheduleTask(task)));
                }
            }
        } finally {
            lock.unlock();
        }
    }

    private void scheduleTask(DAGTask task) {
        executor.schedule(task, 0);
    }

    private void onTaskCompleted(DAGTask task, boolean success) {
        if (!success) return;

        List<DAGTask> deps = new ArrayList<>();
        lock.lock();
        try {
            List<DAGTask> list = dependents.get(task.taskId);
            if (list != null) {
                deps.addAll(list);
            }
        } finally {
            lock.unlock();
        }

        for (DAGTask dep : deps) {
            barriers.get(dep.taskId).countDown();
        }
    }
}

/**
 * JobScheduler for job-scheduler (v3-optimized).
 */
public class JobScheduler {
    private final String id;
    public final ScheduledThreadPoolExecutor executor;
    public final DAGScheduler dagScheduler;

    public JobScheduler() {
        this.id = "JobScheduler";
        this.executor = new ScheduledThreadPoolExecutor(4);
        this.executor.start();
        this.dagScheduler = new DAGScheduler(this.executor);
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "JobScheduler:" + id;
    }
}
