
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;

public class WebhookDispatcher {
    private final HttpClient httpClient;
    private final Map<String, Subscriber> subscribers = new ConcurrentHashMap<>();
    
    private final PersistentDlq dlq = new PersistentDlq(7);
    private final ConcurrentMap<String, CircuitBreaker> circuitBreakers = new ConcurrentHashMap<>();
    
    private final ExecutorService workerPool;
    private final ScheduledExecutorService retryScheduler;
    
    private final ConcurrentMap<String, Semaphore> hostSemaphores = new ConcurrentHashMap<>();
    private final int defaultMaxConcurrentPerHost;
    private final Map<String, Integer> hostLimits;

    public WebhookDispatcher(HttpClient httpClient, int numWorkers, int defaultMaxConcurrentPerHost, Map<String, Integer> hostLimits) {
        this.httpClient = httpClient;
        this.defaultMaxConcurrentPerHost = defaultMaxConcurrentPerHost;
        this.hostLimits = hostLimits != null ? hostLimits : Map.of();
        this.workerPool = Executors.newFixedThreadPool(numWorkers);
        this.retryScheduler = Executors.newScheduledThreadPool(2);
    }

    public void addSubscriber(Subscriber sub) {
        subscribers.put(sub.getId(), sub);
        int limit = hostLimits.getOrDefault(sub.getHost(), defaultMaxConcurrentPerHost);
        hostSemaphores.putIfAbsent(sub.getHost(), new Semaphore(limit));
        circuitBreakers.putIfAbsent(sub.getEndpoint(), new CircuitBreaker(5, 5000));
    }

    public void removeSubscriber(String subId) {
        subscribers.remove(subId);
    }

    public void publish(Event event) {
        for (Subscriber sub : subscribers.values()) {
            if (sub.getTopicRegex().matcher(event.getTopic()).matches()) {
                WebhookTask task = new WebhookTask(event, sub, this);
                workerPool.submit(task);
            }
        }
    }

    void acquireSemaphore(String host) throws InterruptedException {
        int limit = hostLimits.getOrDefault(host, defaultMaxConcurrentPerHost);
        hostSemaphores.computeIfAbsent(host, k -> new Semaphore(limit)).acquire();
    }

    void releaseSemaphore(String host) {
        Semaphore sem = hostSemaphores.get(host);
        if (sem != null) {
            sem.release();
        }
    }
    
    public CircuitBreaker getCircuitBreaker(String endpoint) {
        return circuitBreakers.computeIfAbsent(endpoint, k -> new CircuitBreaker(5, 5000));
    }

    void scheduleRetry(WebhookTask task, long delayMs) {
        retryScheduler.schedule(() -> workerPool.submit(task), delayMs, TimeUnit.MILLISECONDS);
    }

    void addToDlq(WebhookTask task) {
        dlq.add(task);
    }
    
    public void replayDlq() {
        List<WebhookTask> tasks = dlq.getItems();
        dlq.clear();
        for (WebhookTask task : tasks) {
            task.resetAttempt();
            workerPool.submit(task);
        }
    }

    public HttpClient getHttpClient() {
        return httpClient;
    }

    public PersistentDlq getDlq() {
        return dlq;
    }

    public void stop() {
        workerPool.shutdown();
        retryScheduler.shutdown();
        try {
            if (!workerPool.awaitTermination(2, TimeUnit.SECONDS)) {
                workerPool.shutdownNow();
            }
            if (!retryScheduler.awaitTermination(2, TimeUnit.SECONDS)) {
                retryScheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            workerPool.shutdownNow();
            retryScheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
