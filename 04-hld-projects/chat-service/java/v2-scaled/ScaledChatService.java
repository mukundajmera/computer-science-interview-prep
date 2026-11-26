package chatservice.v2;

import java.util.*;
import java.time.Instant;
import java.util.concurrent.CompletableFuture;

/**
 * Chat Service - v2-scaled
 * 
 * Enhancements over v1:
 * - Message queue for reliable async delivery
 * - Group chat with fan-out
 * - Read receipts and delivery status
 * - Presence service
 * - Connection scaling across multiple servers
 */

// ============================================================================
// Infrastructure Interfaces
// ============================================================================

interface MessageQueue {
    void publish(String topic, byte[] message);
    void subscribe(String topic, MessageConsumer consumer);
}

interface MessageConsumer {
    void onMessage(byte[] message);
}

interface Cache {
    String get(String key);
    void set(String key, String value, int ttlSeconds);
    void delete(String key);
    void publish(String channel, String message);
    void subscribe(String channel, CacheSubscriber subscriber);
}

interface CacheSubscriber {
    void onMessage(String channel, String message);
}

// ============================================================================
// DTOs
// ============================================================================

class MessageStatus {
    public enum Status { SENT, DELIVERED, READ }

    private final UUID messageId;
    private final Map<UUID, Status> recipientStatus;
    private final Instant updatedAt;

    public MessageStatus(UUID messageId) {
        this.messageId = messageId;
        this.recipientStatus = new HashMap<>();
        this.updatedAt = Instant.now();
    }

    public UUID getMessageId() { return messageId; }
    public Map<UUID, Status> getRecipientStatus() { return recipientStatus; }
    
    public void markDelivered(UUID userId) {
        recipientStatus.put(userId, Status.DELIVERED);
    }
    
    public void markRead(UUID userId) {
        recipientStatus.put(userId, Status.READ);
    }
}

class DeliveryTask {
    private final UUID messageId;
    private final UUID conversationId;
    private final UUID senderId;
    private final List<UUID> recipientIds;
    private final String content;
    private final Instant createdAt;
    private int retryCount;

    public DeliveryTask(UUID messageId, UUID conversationId, UUID senderId,
                        List<UUID> recipientIds, String content) {
        this.messageId = messageId;
        this.conversationId = conversationId;
        this.senderId = senderId;
        this.recipientIds = recipientIds;
        this.content = content;
        this.createdAt = Instant.now();
        this.retryCount = 0;
    }

    public UUID getMessageId() { return messageId; }
    public UUID getConversationId() { return conversationId; }
    public UUID getSenderId() { return senderId; }
    public List<UUID> getRecipientIds() { return recipientIds; }
    public String getContent() { return content; }
    public Instant getCreatedAt() { return createdAt; }
    public int getRetryCount() { return retryCount; }
    public void incrementRetry() { retryCount++; }
}

class UserPresence {
    public enum Status { ONLINE, OFFLINE, AWAY }

    private final UUID userId;
    private Status status;
    private Instant lastSeen;
    private final Set<String> connectedDevices;
    private String wsServerId;

    public UserPresence(UUID userId) {
        this.userId = userId;
        this.status = Status.OFFLINE;
        this.lastSeen = Instant.now();
        this.connectedDevices = new HashSet<>();
    }

    public UUID getUserId() { return userId; }
    public Status getStatus() { return status; }
    public void setStatus(Status status) { this.status = status; }
    public Instant getLastSeen() { return lastSeen; }
    public void setLastSeen(Instant lastSeen) { this.lastSeen = lastSeen; }
    public Set<String> getConnectedDevices() { return connectedDevices; }
    public String getWsServerId() { return wsServerId; }
    public void setWsServerId(String wsServerId) { this.wsServerId = wsServerId; }
}

// ============================================================================
// Presence Service
// ============================================================================

interface PresenceService {
    void setOnline(UUID userId, String deviceId, String wsServerId);
    void setOffline(UUID userId, String deviceId);
    UserPresence getPresence(UUID userId);
    Map<UUID, UserPresence> getPresenceBulk(List<UUID> userIds);
    void heartbeat(UUID userId, String deviceId);
}

class RedisPresenceService implements PresenceService {
    private final Cache cache;
    private static final int PRESENCE_TTL = 300; // 5 minutes
    private static final String PRESENCE_KEY_PREFIX = "presence:";

    public RedisPresenceService(Cache cache) {
        this.cache = cache;
    }

    @Override
    public void setOnline(UUID userId, String deviceId, String wsServerId) {
        String key = PRESENCE_KEY_PREFIX + userId;
        // In production: use Redis hash or JSON
        String value = String.format("{\"status\":\"online\",\"wsServer\":\"%s\"}", wsServerId);
        cache.set(key, value, PRESENCE_TTL);
        
        // Notify subscribers about presence change
        cache.publish("presence_updates", userId + ":online");
    }

    @Override
    public void setOffline(UUID userId, String deviceId) {
        String key = PRESENCE_KEY_PREFIX + userId;
        String value = String.format("{\"status\":\"offline\",\"lastSeen\":\"%s\"}", Instant.now());
        cache.set(key, value, PRESENCE_TTL * 12); // Keep offline status longer
        
        cache.publish("presence_updates", userId + ":offline");
    }

    @Override
    public UserPresence getPresence(UUID userId) {
        String key = PRESENCE_KEY_PREFIX + userId;
        String value = cache.get(key);
        // Parse and return presence
        return parsePresence(userId, value);
    }

    @Override
    public Map<UUID, UserPresence> getPresenceBulk(List<UUID> userIds) {
        Map<UUID, UserPresence> result = new HashMap<>();
        for (UUID userId : userIds) {
            result.put(userId, getPresence(userId));
        }
        return result;
    }

    @Override
    public void heartbeat(UUID userId, String deviceId) {
        String key = PRESENCE_KEY_PREFIX + userId;
        // Extend TTL on heartbeat
        String existing = cache.get(key);
        if (existing != null) {
            cache.set(key, existing, PRESENCE_TTL);
        }
    }

    private UserPresence parsePresence(UUID userId, String value) {
        UserPresence presence = new UserPresence(userId);
        if (value != null && value.contains("online")) {
            presence.setStatus(UserPresence.Status.ONLINE);
        }
        return presence;
    }
}

// ============================================================================
// Async Message Service
// ============================================================================

class AsyncMessageService {
    private final MessageQueue messageQueue;
    private final PresenceService presenceService;
    private final Cache cache;
    
    private static final String DELIVERY_TOPIC = "message_delivery";
    private static final String FANOUT_TOPIC = "message_fanout";

    public AsyncMessageService(MessageQueue messageQueue, 
                               PresenceService presenceService,
                               Cache cache) {
        this.messageQueue = messageQueue;
        this.presenceService = presenceService;
        this.cache = cache;
    }

    /**
     * Send message with async delivery.
     */
    public CompletableFuture<UUID> sendMessage(UUID senderId, UUID conversationId,
                                                String content, List<UUID> recipientIds) {
        UUID messageId = UUID.randomUUID();
        
        // Create delivery task
        DeliveryTask task = new DeliveryTask(
            messageId,
            conversationId,
            senderId,
            recipientIds,
            content
        );
        
        // Enqueue for delivery
        messageQueue.publish(DELIVERY_TOPIC, serialize(task));
        
        // Update message status
        updateStatus(messageId, MessageStatus.Status.SENT);
        
        return CompletableFuture.completedFuture(messageId);
    }

    /**
     * Send group message with fan-out.
     */
    public CompletableFuture<UUID> sendGroupMessage(UUID senderId, UUID groupId,
                                                     String content, List<UUID> memberIds) {
        UUID messageId = UUID.randomUUID();
        
        // For large groups, use fan-out pattern
        if (memberIds.size() > 50) {
            // Publish to fan-out topic
            messageQueue.publish(FANOUT_TOPIC, serialize(new DeliveryTask(
                messageId, groupId, senderId, memberIds, content
            )));
        } else {
            // Direct delivery for small groups
            for (UUID memberId : memberIds) {
                if (!memberId.equals(senderId)) {
                    messageQueue.publish(DELIVERY_TOPIC, serialize(new DeliveryTask(
                        messageId, groupId, senderId, List.of(memberId), content
                    )));
                }
            }
        }
        
        return CompletableFuture.completedFuture(messageId);
    }

    /**
     * Mark message as delivered.
     */
    public void markDelivered(UUID messageId, UUID userId) {
        updateStatus(messageId, userId, MessageStatus.Status.DELIVERED);
        notifySender(messageId, "delivered", userId);
    }

    /**
     * Mark message as read.
     */
    public void markRead(UUID messageId, UUID userId) {
        updateStatus(messageId, userId, MessageStatus.Status.READ);
        notifySender(messageId, "read", userId);
    }

    private void updateStatus(UUID messageId, MessageStatus.Status status) {
        String key = "msg:" + messageId + ":status";
        cache.set(key, status.name(), 86400 * 7); // 7 days TTL
    }

    private void updateStatus(UUID messageId, UUID userId, MessageStatus.Status status) {
        String key = "msg:" + messageId + ":status:" + userId;
        cache.set(key, status.name(), 86400 * 7);
    }

    private void notifySender(UUID messageId, String status, UUID byUserId) {
        // Publish status update to sender via Redis pub/sub
        cache.publish("status_updates", 
            String.format("%s:%s:%s", messageId, status, byUserId));
    }

    private byte[] serialize(Object obj) {
        // In production: use proper serialization (JSON, Protobuf)
        return obj.toString().getBytes();
    }
}

// ============================================================================
// Delivery Worker
// ============================================================================

class DeliveryWorker implements MessageConsumer {
    private final PresenceService presenceService;
    private final ConnectionRegistry connectionRegistry;
    private final MessageQueue messageQueue;
    private final Cache cache;

    public DeliveryWorker(PresenceService presenceService,
                          ConnectionRegistry connectionRegistry,
                          MessageQueue messageQueue,
                          Cache cache) {
        this.presenceService = presenceService;
        this.connectionRegistry = connectionRegistry;
        this.messageQueue = messageQueue;
        this.cache = cache;
    }

    @Override
    public void onMessage(byte[] message) {
        DeliveryTask task = deserialize(message);
        
        for (UUID recipientId : task.getRecipientIds()) {
            deliverToUser(task, recipientId);
        }
    }

    private void deliverToUser(DeliveryTask task, UUID recipientId) {
        UserPresence presence = presenceService.getPresence(recipientId);
        
        if (presence.getStatus() == UserPresence.Status.ONLINE) {
            // User online - deliver immediately
            String wsServerId = presence.getWsServerId();
            boolean delivered = connectionRegistry.pushToUser(
                wsServerId, recipientId, task.getContent()
            );
            
            if (delivered) {
                // Mark as delivered
                cache.publish("status_updates", 
                    task.getMessageId() + ":delivered:" + recipientId);
            } else {
                // Retry or queue for offline
                handleDeliveryFailure(task, recipientId);
            }
        } else {
            // User offline - queue for later
            queueForOfflineUser(task, recipientId);
        }
    }

    private void handleDeliveryFailure(DeliveryTask task, UUID recipientId) {
        task.incrementRetry();
        if (task.getRetryCount() < 3) {
            // Retry with backoff
            messageQueue.publish("message_delivery_retry", serialize(task));
        } else {
            // Move to offline queue
            queueForOfflineUser(task, recipientId);
        }
    }

    private void queueForOfflineUser(DeliveryTask task, UUID recipientId) {
        String key = "offline_queue:" + recipientId;
        cache.set(key, task.getMessageId().toString(), 86400 * 30); // 30 days
    }

    private DeliveryTask deserialize(byte[] data) {
        // In production: proper deserialization
        return null;
    }

    private byte[] serialize(Object obj) {
        return obj.toString().getBytes();
    }
}

// ============================================================================
// Connection Registry
// ============================================================================

interface ConnectionRegistry {
    void register(UUID userId, String deviceId, String wsServerId);
    void unregister(UUID userId, String deviceId);
    String getWsServer(UUID userId);
    boolean pushToUser(String wsServerId, UUID userId, String message);
}

class RedisConnectionRegistry implements ConnectionRegistry {
    private final Cache cache;

    public RedisConnectionRegistry(Cache cache) {
        this.cache = cache;
    }

    @Override
    public void register(UUID userId, String deviceId, String wsServerId) {
        String key = "conn:" + userId;
        cache.set(key, wsServerId, 3600);
    }

    @Override
    public void unregister(UUID userId, String deviceId) {
        String key = "conn:" + userId;
        cache.delete(key);
    }

    @Override
    public String getWsServer(UUID userId) {
        return cache.get("conn:" + userId);
    }

    @Override
    public boolean pushToUser(String wsServerId, UUID userId, String message) {
        // In production: call WebSocket server via internal RPC
        // This would route through Redis pub/sub to correct WS server
        cache.publish("ws:" + wsServerId, userId + ":" + message);
        return true;
    }
}
