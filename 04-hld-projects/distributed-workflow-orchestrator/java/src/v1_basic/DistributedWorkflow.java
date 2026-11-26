package v1_basic;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.locks.ReentrantLock;

public class DistributedWorkflow {

    public enum EventType {
        WORKFLOW_STARTED,
        ACTIVITY_SCHEDULED,
        ACTIVITY_COMPLETED,
        ACTIVITY_FAILED,
        WORKFLOW_COMPLETED,
        WORKFLOW_FAILED
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
    }

    public static class ActivityTask {
        public final String taskId;
        public final String activityName;
        public String status = "PENDING";
        public Object result = null;
        public Exception error = null;
        public Long leaseExpiresAt = null;

        public ActivityTask(String taskId, String activityName) {
            this.taskId = taskId;
            this.activityName = activityName;
        }
    }

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

        public boolean acquireLease(String taskId) {
            lock.lock();
            try {
                ActivityTask task = tasks.get(taskId);
                if (task == null) return false;
                long now = System.currentTimeMillis();
                if (task.status.equals("PENDING") || 
                   (task.status.equals("LEASED") && task.leaseExpiresAt != null && now > task.leaseExpiresAt)) {
                    task.status = "LEASED";
                    task.leaseExpiresAt = now + leaseTimeoutMs;
                    return true;
                }
                return false;
            } finally {
                lock.unlock();
            }
        }

        public boolean heartbeat(String taskId) {
            lock.lock();
            try {
                ActivityTask task = tasks.get(taskId);
                if (task == null || !task.status.equals("LEASED")) return false;
                long now = System.currentTimeMillis();
                if (task.leaseExpiresAt != null && now > task.leaseExpiresAt) return false;
                task.leaseExpiresAt = now + leaseTimeoutMs;
                return true;
            } finally {
                lock.unlock();
            }
        }

        public boolean complete(String taskId, Object result) {
            lock.lock();
            try {
                ActivityTask task = tasks.get(taskId);
                if (task == null || !task.status.equals("LEASED")) return false;
                long now = System.currentTimeMillis();
                if (task.leaseExpiresAt != null && now > task.leaseExpiresAt) return false;
                task.status = "COMPLETED";
                task.result = result;
                return true;
            } finally {
                lock.unlock();
            }
        }

        public boolean fail(String taskId, Exception error) {
            lock.lock();
            try {
                ActivityTask task = tasks.get(taskId);
                if (task == null || !task.status.equals("LEASED")) return false;
                long now = System.currentTimeMillis();
                if (task.leaseExpiresAt != null && now > task.leaseExpiresAt) return false;
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
        public final SagaCoordinator saga = new SagaCoordinator();
        public String workflowStatus = "PENDING";
        private final ReentrantLock lock = new ReentrantLock();

        public WorkflowOrchestrator(ActivityExecutor executor) {
            this.executor = executor;
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
                history.addEvent(new Event(EventType.ACTIVITY_SCHEDULED, taskId, activityName));
                executor.submit(taskId, activityName);
            } finally {
                lock.unlock();
            }
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
    }
}
