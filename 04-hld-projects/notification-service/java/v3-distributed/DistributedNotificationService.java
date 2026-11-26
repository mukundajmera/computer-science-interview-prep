/**
 * Notification Service - V3 Distributed
 * 
 * Multi-region notification service with advanced routing.
 */

import java.util.*;
import java.util.concurrent.*;

/**
 * Multi-region notification coordinator.
 */
class DistributedNotificationService {
    
    private final String localRegion;
    private final Map<String, RegionalNotificationService> regionalServices;
    private final GlobalLoadBalancer loadBalancer;
    private final CrossRegionReplicator replicator;
    
    public DistributedNotificationService(String localRegion,
                                          Map<String, RegionalNotificationService> regionalServices,
                                          GlobalLoadBalancer loadBalancer) {
        this.localRegion = localRegion;
        this.regionalServices = regionalServices;
        this.loadBalancer = loadBalancer;
        this.replicator = new CrossRegionReplicator(regionalServices);
    }
    
    /**
     * Send notification, routing to best region.
     */
    public SendNotificationResponse send(SendNotificationRequest request, 
                                         String userRegion) {
        // Determine best region to handle request
        String targetRegion = loadBalancer.getBestRegion(userRegion);
        
        RegionalNotificationService service = regionalServices.get(targetRegion);
        SendNotificationResponse response = service.send(request);
        
        // Async replication for audit/analytics
        replicator.replicateAsync(response.getNotificationId(), 
                                  request, targetRegion);
        
        return response;
    }
    
    /**
     * Get notification status from any region.
     */
    public Optional<Notification> getStatus(String notificationId) {
        // Try local first
        RegionalNotificationService local = regionalServices.get(localRegion);
        Optional<Notification> result = local.getStatus(notificationId);
        
        if (result.isPresent()) {
            return result;
        }
        
        // Fan out to other regions
        for (Map.Entry<String, RegionalNotificationService> entry : 
             regionalServices.entrySet()) {
            if (!entry.getKey().equals(localRegion)) {
                result = entry.getValue().getStatus(notificationId);
                if (result.isPresent()) {
                    return result;
                }
            }
        }
        
        return Optional.empty();
    }
}

/**
 * Regional notification service wrapper.
 */
interface RegionalNotificationService {
    SendNotificationResponse send(SendNotificationRequest request);
    Optional<Notification> getStatus(String notificationId);
    String getRegion();
}

/**
 * Global load balancer for region selection.
 */
class GlobalLoadBalancer {
    
    private final Map<String, List<String>> regionPreferences;
    private final Map<String, RegionHealth> regionHealth;
    
    public GlobalLoadBalancer(Map<String, List<String>> regionPreferences) {
        this.regionPreferences = regionPreferences;
        this.regionHealth = new ConcurrentHashMap<>();
    }
    
    public String getBestRegion(String userRegion) {
        List<String> preferences = regionPreferences.getOrDefault(
            userRegion, List.of("us-east-1"));
        
        for (String region : preferences) {
            RegionHealth health = regionHealth.get(region);
            if (health == null || health.isHealthy()) {
                return region;
            }
        }
        
        return preferences.get(0);
    }
    
    public void updateHealth(String region, boolean healthy) {
        regionHealth.computeIfAbsent(region, RegionHealth::new)
                    .update(healthy);
    }
    
    static class RegionHealth {
        private final String region;
        private boolean healthy = true;
        private int consecutiveFailures = 0;
        
        RegionHealth(String region) {
            this.region = region;
        }
        
        void update(boolean success) {
            if (success) {
                consecutiveFailures = 0;
                healthy = true;
            } else {
                consecutiveFailures++;
                if (consecutiveFailures >= 3) {
                    healthy = false;
                }
            }
        }
        
        boolean isHealthy() {
            return healthy;
        }
    }
}

/**
 * Cross-region replicator for data consistency.
 */
class CrossRegionReplicator {
    
    private final Map<String, RegionalNotificationService> regionalServices;
    private final ExecutorService executor;
    
    public CrossRegionReplicator(Map<String, RegionalNotificationService> regionalServices) {
        this.regionalServices = regionalServices;
        this.executor = Executors.newFixedThreadPool(4);
    }
    
    public void replicateAsync(String notificationId, 
                               SendNotificationRequest request,
                               String sourceRegion) {
        executor.submit(() -> {
            for (Map.Entry<String, RegionalNotificationService> entry : 
                 regionalServices.entrySet()) {
                if (!entry.getKey().equals(sourceRegion)) {
                    try {
                        // Store notification metadata for analytics
                        // In production: Use Kafka or similar
                    } catch (Exception e) {
                        System.err.println("Replication failed to " + 
                            entry.getKey() + ": " + e.getMessage());
                    }
                }
            }
        });
    }
    
    public void shutdown() {
        executor.shutdown();
    }
}

/**
 * Bulk notification processor for campaigns.
 */
class BulkNotificationProcessor {
    
    private final NotificationService notificationService;
    private final ExecutorService executor;
    private final int batchSize;
    
    public BulkNotificationProcessor(NotificationService notificationService,
                                     int workerCount, int batchSize) {
        this.notificationService = notificationService;
        this.executor = Executors.newFixedThreadPool(workerCount);
        this.batchSize = batchSize;
    }
    
    /**
     * Process bulk notification to many users.
     */
    public BulkResult processBulk(BulkNotificationRequest request) {
        List<String> userIds = request.getUserIds();
        int total = userIds.size();
        AtomicInteger sent = new AtomicInteger();
        AtomicInteger failed = new AtomicInteger();
        
        // Process in batches
        List<CompletableFuture<Void>> futures = new ArrayList<>();
        
        for (int i = 0; i < userIds.size(); i += batchSize) {
            int end = Math.min(i + batchSize, userIds.size());
            List<String> batch = userIds.subList(i, end);
            
            CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
                for (String userId : batch) {
                    try {
                        SendNotificationRequest sendRequest = new SendNotificationRequest(
                            userId,
                            request.getTemplateId(),
                            request.getChannel(),
                            request.getPriority(),
                            request.getVariables(),
                            request.getScheduledAt(),
                            null
                        );
                        
                        notificationService.send(sendRequest);
                        sent.incrementAndGet();
                        
                    } catch (Exception e) {
                        failed.incrementAndGet();
                    }
                }
            }, executor);
            
            futures.add(future);
        }
        
        // Wait for all batches
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        
        return new BulkResult(total, sent.get(), failed.get());
    }
    
    public void shutdown() {
        executor.shutdown();
    }
}

class AtomicInteger {
    private int value = 0;
    
    public synchronized int incrementAndGet() {
        return ++value;
    }
    
    public synchronized int get() {
        return value;
    }
}

/**
 * Bulk notification request.
 */
class BulkNotificationRequest {
    private final List<String> userIds;
    private final String templateId;
    private final NotificationChannel channel;
    private final NotificationPriority priority;
    private final Map<String, String> variables;
    private final java.time.Instant scheduledAt;
    
    public BulkNotificationRequest(List<String> userIds, String templateId,
                                   NotificationChannel channel, 
                                   NotificationPriority priority,
                                   Map<String, String> variables,
                                   java.time.Instant scheduledAt) {
        this.userIds = userIds;
        this.templateId = templateId;
        this.channel = channel;
        this.priority = priority;
        this.variables = variables;
        this.scheduledAt = scheduledAt;
    }
    
    public List<String> getUserIds() { return userIds; }
    public String getTemplateId() { return templateId; }
    public NotificationChannel getChannel() { return channel; }
    public NotificationPriority getPriority() { return priority; }
    public Map<String, String> getVariables() { return variables; }
    public java.time.Instant getScheduledAt() { return scheduledAt; }
}

/**
 * Bulk processing result.
 */
class BulkResult {
    private final int total;
    private final int sent;
    private final int failed;
    
    public BulkResult(int total, int sent, int failed) {
        this.total = total;
        this.sent = sent;
        this.failed = failed;
    }
    
    public int getTotal() { return total; }
    public int getSent() { return sent; }
    public int getFailed() { return failed; }
}

// ============================================================================
// Pattern Integration Hooks (Real-time transport, contention, workflow durability)
// ============================================================================

enum DeliveryMode {
    POLLING,
    LONG_POLLING,
    SSE,
    WEBSOCKET
    // WebRTC can be layered for device-to-device delivery in niche cases.
}

enum ContentionPolicy {
    OPTIMISTIC,
    PESSIMISTIC,
    SERIAL_QUEUE,
    DISTRIBUTED_LOCK
}

class ExecutionResult {
    private final boolean success;
    private final String checkpointId;
    private final String errorMessage;
    private final boolean retryable;

    private ExecutionResult(boolean success, String checkpointId, String errorMessage, boolean retryable) {
        this.success = success;
        this.checkpointId = checkpointId;
        this.errorMessage = errorMessage;
        this.retryable = retryable;
    }

    public static ExecutionResult success(String checkpointId) {
        return new ExecutionResult(true, checkpointId, null, false);
    }

    public static ExecutionResult failure(String checkpointId, String errorMessage, boolean retryable) {
        return new ExecutionResult(false, checkpointId, errorMessage, retryable);
    }

    public boolean isSuccess() { return success; }
    public String getCheckpointId() { return checkpointId; }
    public String getErrorMessage() { return errorMessage; }
    public boolean isRetryable() { return retryable; }
}

interface WorkflowStep {
    String name();
    ExecutionResult execute();
}

interface CompensationStep {
    String name();
    void compensate(String checkpointId);
}

interface WorkflowOrchestrator {
    ExecutionResult runStep(WorkflowStep step, String idempotencyKey, IdempotencyStore store);
    void registerCompensation(String checkpointId, CompensationStep compensationStep);
}

interface IdempotencyStore {
    boolean hasProcessed(String key);
    void markProcessed(String key, ExecutionResult result);
    Optional<ExecutionResult> getResult(String key);
}
