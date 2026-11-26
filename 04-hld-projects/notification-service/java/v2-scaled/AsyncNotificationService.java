/**
 * Notification Service - V2 Scaled
 * 
 * Priority queue-based notification service with async processing.
 */

import java.time.Instant;
import java.util.Map;
import java.util.Queue;
import java.util.concurrent.*;

/**
 * Message queue interface for async notification processing.
 */
interface NotificationQueue {
    void enqueue(NotificationMessage message);
    NotificationMessage poll(long timeout, TimeUnit unit) throws InterruptedException;
    int size();
}

/**
 * Message wrapper for queue.
 */
class NotificationMessage {
    private final Notification notification;
    private final UserPreferences preferences;
    private final Instant enqueuedAt;
    private int retryCount;
    
    public NotificationMessage(Notification notification, UserPreferences preferences) {
        this.notification = notification;
        this.preferences = preferences;
        this.enqueuedAt = Instant.now();
        this.retryCount = 0;
    }
    
    public Notification getNotification() { return notification; }
    public UserPreferences getPreferences() { return preferences; }
    public Instant getEnqueuedAt() { return enqueuedAt; }
    public int getRetryCount() { return retryCount; }
    public void incrementRetry() { retryCount++; }
}

/**
 * Priority-based queue implementation.
 */
class PriorityNotificationQueue implements NotificationQueue {
    
    private final BlockingQueue<NotificationMessage> queue;
    
    public PriorityNotificationQueue() {
        this.queue = new PriorityBlockingQueue<>(100, (a, b) -> {
            // Critical first, then by enqueue time
            int priorityCompare = a.getNotification().getPriority().ordinal() - 
                                  b.getNotification().getPriority().ordinal();
            if (priorityCompare != 0) return priorityCompare;
            return a.getEnqueuedAt().compareTo(b.getEnqueuedAt());
        });
    }
    
    @Override
    public void enqueue(NotificationMessage message) {
        queue.offer(message);
    }
    
    @Override
    public NotificationMessage poll(long timeout, TimeUnit unit) 
            throws InterruptedException {
        return queue.poll(timeout, unit);
    }
    
    @Override
    public int size() {
        return queue.size();
    }
}

/**
 * Dead letter queue for failed notifications.
 */
class DeadLetterQueue {
    private final Queue<NotificationMessage> dlq = new ConcurrentLinkedQueue<>();
    
    public void add(NotificationMessage message) {
        dlq.offer(message);
    }
    
    public NotificationMessage poll() {
        return dlq.poll();
    }
    
    public int size() {
        return dlq.size();
    }
}

/**
 * Async notification service with worker pool.
 */
class AsyncNotificationService implements NotificationService {
    
    private static final int MAX_RETRY_COUNT = 6;
    private static final long[] RETRY_DELAYS_MS = {
        0, 60_000, 300_000, 900_000, 3_600_000, 14_400_000
    };
    
    private final TemplateService templateService;
    private final TemplateRenderer renderer;
    private final ChannelRouter channelRouter;
    private final PreferenceService preferenceService;
    private final NotificationRepository repository;
    private final NotificationQueue mainQueue;
    private final DeadLetterQueue dlq;
    private final ExecutorService workerPool;
    private final ScheduledExecutorService scheduler;
    private volatile boolean running = true;
    
    public AsyncNotificationService(TemplateService templateService,
                                    ChannelRouter channelRouter,
                                    PreferenceService preferenceService,
                                    NotificationRepository repository,
                                    int workerCount) {
        this.templateService = templateService;
        this.renderer = new TemplateRenderer();
        this.channelRouter = channelRouter;
        this.preferenceService = preferenceService;
        this.repository = repository;
        this.mainQueue = new PriorityNotificationQueue();
        this.dlq = new DeadLetterQueue();
        this.workerPool = Executors.newFixedThreadPool(workerCount);
        this.scheduler = Executors.newScheduledThreadPool(2);
        
        // Start workers
        for (int i = 0; i < workerCount; i++) {
            workerPool.submit(this::processLoop);
        }
    }
    
    @Override
    public SendNotificationResponse send(SendNotificationRequest request) {
        // Check user preferences
        UserPreferences prefs = preferenceService.getPreferences(request.getUserId());
        if (!prefs.isChannelEnabled(request.getChannel())) {
            throw new UserOptedOutException(
                "User has disabled " + request.getChannel() + " notifications");
        }
        
        // Get and render template
        NotificationTemplate template = templateService
            .getTemplate(request.getTemplateId())
            .orElseThrow(() -> new TemplateNotFoundException(request.getTemplateId()));
        
        RenderedContent content = renderer.render(template, request.getVariables());
        
        // Create notification
        Notification notification = new Notification(
            request.getUserId(),
            request.getTemplateId(),
            request.getChannel(),
            request.getPriority(),
            request.getVariables(),
            content.getBody()
        );
        
        repository.save(notification);
        
        // Enqueue for async processing
        NotificationMessage message = new NotificationMessage(notification, prefs);
        mainQueue.enqueue(message);
        
        return new SendNotificationResponse(
            notification.getNotificationId(),
            NotificationStatus.QUEUED,
            estimateDelivery(request.getPriority())
        );
    }
    
    /**
     * Worker loop for processing notifications.
     */
    private void processLoop() {
        while (running) {
            try {
                NotificationMessage message = mainQueue.poll(1, TimeUnit.SECONDS);
                if (message != null) {
                    processMessage(message);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                System.err.println("Worker error: " + e.getMessage());
            }
        }
    }
    
    /**
     * Process a single notification message.
     */
    private void processMessage(NotificationMessage message) {
        Notification notification = message.getNotification();
        
        try {
            ChannelProvider provider = channelRouter.getProvider(notification.getChannel());
            ProviderResult result = provider.send(notification, message.getPreferences());
            
            if (result.isSuccess()) {
                notification.markSent();
                notification.markDelivered();
                repository.save(notification);
            } else {
                handleFailure(message, result.getErrorMessage());
            }
            
        } catch (Exception e) {
            handleFailure(message, e.getMessage());
        }
    }
    
    /**
     * Handle delivery failure with retry logic.
     */
    private void handleFailure(NotificationMessage message, String error) {
        Notification notification = message.getNotification();
        notification.incrementAttempt();
        
        if (message.getRetryCount() < MAX_RETRY_COUNT) {
            // Schedule retry with exponential backoff
            message.incrementRetry();
            long delay = RETRY_DELAYS_MS[message.getRetryCount()];
            
            scheduler.schedule(() -> mainQueue.enqueue(message), 
                              delay, TimeUnit.MILLISECONDS);
            
            repository.save(notification);
        } else {
            // Max retries exceeded - move to DLQ
            notification.markFailed(error);
            repository.save(notification);
            dlq.add(message);
        }
    }
    
    private Instant estimateDelivery(NotificationPriority priority) {
        long delaySeconds = switch (priority) {
            case CRITICAL -> 1;
            case HIGH -> 30;
            case NORMAL -> 300;
            case LOW -> 3600;
        };
        return Instant.now().plusSeconds(delaySeconds);
    }
    
    @Override
    public java.util.Optional<Notification> getStatus(String notificationId) {
        return repository.findById(notificationId);
    }
    
    @Override
    public boolean cancel(String notificationId) {
        return false; // Cannot cancel once queued in v2
    }
    
    public void shutdown() {
        running = false;
        workerPool.shutdown();
        scheduler.shutdown();
    }
    
    public int getQueueSize() {
        return mainQueue.size();
    }
    
    public int getDlqSize() {
        return dlq.size();
    }
}
