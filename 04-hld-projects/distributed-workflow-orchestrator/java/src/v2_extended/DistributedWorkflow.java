package v2_extended;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

/**
 * v2-extended workflow orchestrator. The event-sourced history, lease
 * lifecycle, saga compensation and wait loop are v1 behavior; the
 * step-ups are the ones the project's own docs call for:
 *
 * 1. Task tokens against zombie workers (FOLLOW-UPS.md #2, PITFALLS.md
 *    #4): every lease acquisition issues a fresh task token and the
 *    orchestrator only accepts complete/fail/heartbeat calls carrying
 *    the currently valid token. A hung worker whose lease expired and
 *    was re-acquired by another worker is rejected when it wakes up.
 * 2. Durable timers (FOLLOW-UPS.md #3/#4): timers are persisted rows
 *    with an expiration; a poll scan turns expired rows into TimerFired
 *    events that wake the workflow - workers never block a thread
 *    sleeping.
 * 3. Continue-As-New with a history limit (FOLLOW-UPS.md #1, PITFALLS.md
 *    #3): histories cannot grow forever. Scheduling past the configured
 *    event limit fails loudly, and continueAsNew closes the run and
 *    spawns a fresh execution with an empty history seeded from the
 *    workflow's logical state.
 */
public class DistributedWorkflow {

    public enum EventType {
        WORKFLOW_STARTED,
        ACTIVITY_SCHEDULED,
        ACTIVITY_COMPLETED,
        ACTIVITY_FAILED,
        TIMER_STARTED,
        TIMER_FIRED,
        WORKFLOW_COMPLETED,
        WORKFLOW_FAILED,
        WORKFLOW_CONTINUED_AS_NEW
    }

    public static class Event {
        public final EventType eventType;
        public final String eventId;
        public final Object payload;

        public Event(EventType eventType, String eventId, Object payload) {
            this.eventType = eventType;
            this.eventId = eventId;
            this.payload = payload;
        }

        public Event(EventType eventType, String eventId) {
            this(eventType, eventId, null);
        }
    }

    public static class EventHistory {
        private final List<Event> events = new ArrayList<>();
        private final ReentrantLock lock = new ReentrantLock();

        public void addEvent(Event event) {
            lock.lock();
            try {
                events.add(event);
            } finally {
                lock.unlock();
            }
        }

        public List<Event> getEvents() {
            lock.lock();
            try {
                return new ArrayList<>(events);
            } finally {
                lock.unlock();
            }
        }

        public List<Event> replay() {
            return getEvents();
        }

        public int size() {
            lock.lock();
            try {
                return events.size();
            } finally {
                lock.unlock();
            }
        }
    }

    public static class ActivityTask {
        public final String taskId;
        public final String activityName;
        public String status = "PENDING";
        public Object result = null;
        public Exception error = null;
        public Long leaseExpiresAt = null;
        public long leaseVersion = 0;
        public String leaseToken = null;

        public ActivityTask(String taskId, String activityName) {
            this.taskId = taskId;
            this.activityName = activityName;
        }
    }

    /**
     * v1 lease lifecycle plus task tokens (FOLLOW-UPS.md #2).
     * acquireLease returns the token the worker must present on every
     * later call; a new acquisition invalidates every older token.
     */
    public static class ActivityExecutor {
        private final long leaseTimeoutMs;
        private final Map<String, ActivityTask> tasks = new ConcurrentHashMap<>();
        private final ReentrantLock lock = new ReentrantLock();

        public ActivityExecutor(long leaseTimeoutMs) {
            this.leaseTimeoutMs = leaseTimeoutMs;
        }

        public ActivityTask submit(String taskId, String activityName) {
            lock.lock();
            try {
                ActivityTask task = new ActivityTask(taskId, activityName);
                tasks.put(taskId, task);
                return task;
            } finally {
                lock.unlock();
            }
        }

        /** Lease the task and return its task token; null if not leasable. */
        public String acquireLease(String taskId) {
            lock.lock();
            try {
                ActivityTask task = tasks.get(taskId);
                if (task == null) return null;
                long now = System.currentTimeMillis();
                if (task.status.equals("PENDING") ||
                   (task.status.equals("LEASED") && task.leaseExpiresAt != null && now > task.leaseExpiresAt)) {
                    task.status = "LEASED";
                    task.leaseExpiresAt = now + leaseTimeoutMs;
                    task.leaseVersion += 1;
                    task.leaseToken = taskId + "-lease-" + task.leaseVersion;
                    return task.leaseToken;
                }
                return null;
            } finally {
                lock.unlock();
            }
        }

        private boolean checkToken(ActivityTask task, String token) {
            if (task == null || !task.status.equals("LEASED")) return false;
            if (token == null || !token.equals(task.leaseToken)) return false;
            long now = System.currentTimeMillis();
            return task.leaseExpiresAt == null || now <= task.leaseExpiresAt;
        }

        public boolean heartbeat(String taskId, String token) {
            lock.lock();
            try {
                if (!checkToken(tasks.get(taskId), token)) return false;
                tasks.get(taskId).leaseExpiresAt = System.currentTimeMillis() + leaseTimeoutMs;
                return true;
            } finally {
                lock.unlock();
            }
        }

        public boolean complete(String taskId, String token, Object result) {
            lock.lock();
            try {
                ActivityTask task = tasks.get(taskId);
                if (!checkToken(task, token)) return false;
                task.status = "COMPLETED";
                task.result = result;
                return true;
            } finally {
                lock.unlock();
            }
        }

        public boolean fail(String taskId, String token, Exception error) {
            lock.lock();
            try {
                ActivityTask task = tasks.get(taskId);
                if (!checkToken(task, token)) return false;
                task.status = "FAILED";
                task.error = error;
                return true;
            } finally {
                lock.unlock();
            }
        }

        public ActivityTask getTask(String taskId) {
            lock.lock();
            try {
                return tasks.get(taskId);
            } finally {
                lock.unlock();
            }
        }
    }

    /**
     * Durable timer rows plus an expiry scan (FOLLOW-UPS.md #3/#4). A
     * fired timer is marked, so a poll never emits the same timer twice.
     */
    public static class TimerService {
        private final Map<String, Long> timers = new HashMap<>();
        private final Set<String> fired = new HashSet<>();
        private final ReentrantLock lock = new ReentrantLock();

        public void startTimer(String timerId, long fireAtMs) {
            lock.lock();
            try {
                timers.put(timerId, fireAtMs);
            } finally {
                lock.unlock();
            }
        }

        /** Timer ids that expired since the last poll, in fire-time order. */
        public List<String> pollExpired(long nowMs) {
            lock.lock();
            try {
                List<String> expired = new ArrayList<>();
                for (Map.Entry<String, Long> entry : timers.entrySet()) {
                    if (entry.getValue() <= nowMs && !fired.contains(entry.getKey())) {
                        expired.add(entry.getKey());
                    }
                }
                expired.sort(Comparator.comparingLong(timers::get));
                fired.addAll(expired);
                return expired;
            } finally {
                lock.unlock();
            }
        }

        public boolean isFired(String timerId) {
            lock.lock();
            try {
                return fired.contains(timerId);
            } finally {
                lock.unlock();
            }
        }
    }

    public static class SagaCoordinator {
        private final Stack<Runnable> compensations = new Stack<>();
        private final ReentrantLock lock = new ReentrantLock();

        public void addCompensation(Runnable compensation) {
            lock.lock();
            try {
                compensations.push(compensation);
            } finally {
                lock.unlock();
            }
        }

        public void compensate() {
            lock.lock();
            try {
                while (!compensations.isEmpty()) {
                    Runnable comp = compensations.pop();
                    try {
                        comp.run();
                    } catch (Exception e) {
                        // Log exception and continue
                    }
                }
            } finally {
                lock.unlock();
            }
        }
    }

    public static class WorkflowOrchestrator {
        public final EventHistory history = new EventHistory();
        public final ActivityExecutor executor;
        public final TimerService timerService;
        public final SagaCoordinator saga = new SagaCoordinator();
        public String workflowStatus = "PENDING";
        public final long maxHistoryEvents;
        public final long runId;
        /** Logical state handed over by the previous run (Continue-As-New). */
        public final Object carriedState;
        private final ReentrantLock lock = new ReentrantLock();

        public WorkflowOrchestrator(ActivityExecutor executor) {
            this(executor, new TimerService(), 50000, 1, null);
        }

        public WorkflowOrchestrator(ActivityExecutor executor, TimerService timerService,
                                    long maxHistoryEvents, long runId, Object carriedState) {
            this.executor = executor;
            this.timerService = timerService;
            this.maxHistoryEvents = maxHistoryEvents;
            this.runId = runId;
            this.carriedState = carriedState;
        }

        private void enforceHistoryLimit() {
            if (history.size() >= maxHistoryEvents) {
                throw new IllegalStateException(
                        "history limit " + maxHistoryEvents + " reached; continueAsNew required");
            }
        }

        public void startWorkflow(String workflowId) {
            lock.lock();
            try {
                history.addEvent(new Event(EventType.WORKFLOW_STARTED, workflowId));
                workflowStatus = "RUNNING";
            } finally {
                lock.unlock();
            }
        }

        public void scheduleActivity(String taskId, String activityName) {
            lock.lock();
            try {
                enforceHistoryLimit();
                history.addEvent(new Event(EventType.ACTIVITY_SCHEDULED, taskId, activityName));
                executor.submit(taskId, activityName);
            } finally {
                lock.unlock();
            }
        }

        /**
         * Persist a durable timer and record it; the workflow suspends
         * instead of blocking a thread (FOLLOW-UPS.md #4).
         */
        public void startTimer(String timerId, long fireAtMs) {
            lock.lock();
            try {
                enforceHistoryLimit();
                timerService.startTimer(timerId, fireAtMs);
                history.addEvent(new Event(EventType.TIMER_STARTED, timerId, fireAtMs));
            } finally {
                lock.unlock();
            }
        }

        /** Turn expired timer rows into TimerFired events (FOLLOW-UPS.md #3). */
        public List<String> pollTimers(long nowMs) {
            List<String> firedTimers = timerService.pollExpired(nowMs);
            lock.lock();
            try {
                for (String timerId : firedTimers) {
                    history.addEvent(new Event(EventType.TIMER_FIRED, timerId));
                }
            } finally {
                lock.unlock();
            }
            return firedTimers;
        }

        public Object waitForActivity(String taskId, Runnable compensation) throws Exception {
            while (true) {
                ActivityTask task = executor.getTask(taskId);
                if (task != null && task.status.equals("COMPLETED")) {
                    lock.lock();
                    try {
                        history.addEvent(new Event(EventType.ACTIVITY_COMPLETED, taskId, task.result));
                        if (compensation != null) {
                            saga.addCompensation(compensation);
                        }
                    } finally {
                        lock.unlock();
                    }
                    return task.result;
                } else if (task != null && task.status.equals("FAILED")) {
                    lock.lock();
                    try {
                        history.addEvent(new Event(EventType.ACTIVITY_FAILED, taskId, task.error.toString()));
                    } finally {
                        lock.unlock();
                    }
                    throw task.error;
                }
                Thread.sleep(10);
            }
        }

        public Object waitForActivity(String taskId) throws Exception {
            return waitForActivity(taskId, null);
        }

        public void completeWorkflow(String workflowId) {
            lock.lock();
            try {
                history.addEvent(new Event(EventType.WORKFLOW_COMPLETED, workflowId));
                workflowStatus = "COMPLETED";
            } finally {
                lock.unlock();
            }
        }

        public void failWorkflow(String workflowId, Exception error) {
            lock.lock();
            try {
                history.addEvent(new Event(EventType.WORKFLOW_FAILED, workflowId, error.toString()));
                workflowStatus = "FAILED";
                saga.compensate();
            } finally {
                lock.unlock();
            }
        }

        /**
         * Close this run and spawn a fresh execution with an empty
         * history seeded from the workflow's logical state
         * (FOLLOW-UPS.md #1).
         */
        public WorkflowOrchestrator continueAsNew(String workflowId, Object state) {
            lock.lock();
            try {
                history.addEvent(new Event(EventType.WORKFLOW_CONTINUED_AS_NEW, workflowId, state));
                workflowStatus = "CONTINUED_AS_NEW";
            } finally {
                lock.unlock();
            }
            WorkflowOrchestrator newRun = new WorkflowOrchestrator(
                    executor, timerService, maxHistoryEvents, runId + 1, state);
            newRun.startWorkflow(workflowId);
            return newRun;
        }
    }
}
