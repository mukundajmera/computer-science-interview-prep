import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;

public class WebhookDispatcher {
    private final HttpClient httpClient;
    private final Map<String, Subscriber> subscribers = new ConcurrentHashMap<>();
    private final List<WebhookTask> dlq = new CopyOnWriteArrayList<>();
    
    private final ExecutorService workerPool;
    private final ScheduledExecutorService retryScheduler;
    
    private final ConcurrentMap<String, Semaphore> destinationSemaphores = new ConcurrentHashMap<>();
    private final int maxConcurrentPerDest;

    public WebhookDispatcher(HttpClient httpClient, int numWorkers, int maxConcurrentPerDest) {
        this.httpClient = httpClient;
        this.maxConcurrentPerDest = maxConcurrentPerDest;
        this.workerPool = Executors.newFixedThreadPool(numWorkers);
        this.retryScheduler = Executors.newScheduledThreadPool(2); // separate thread for delayed execution
    }

    public void addSubscriber(Subscriber sub) {
        subscribers.put(sub.getId(), sub);
        destinationSemaphores.putIfAbsent(sub.getEndpoint(), new Semaphore(maxConcurrentPerDest));
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

    void acquireSemaphore(String endpoint) throws InterruptedException {
        destinationSemaphores.computeIfAbsent(endpoint, k -> new Semaphore(maxConcurrentPerDest)).acquire();
    }

    void releaseSemaphore(String endpoint) {
        Semaphore sem = destinationSemaphores.get(endpoint);
        if (sem != null) {
            sem.release();
        }
    }

    void scheduleRetry(WebhookTask task, long delayMs) {
        retryScheduler.schedule(() -> workerPool.submit(task), delayMs, TimeUnit.MILLISECONDS);
    }

    void addToDlq(WebhookTask task) {
        dlq.add(task);
    }

    public HttpClient getHttpClient() {
        return httpClient;
    }

    public List<WebhookTask> getDlq() {
        return new ArrayList<>(dlq);
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
