/**
 * Notification Service - V1 Basic
 * 
 * Core notification service interfaces and DTOs.
 */

import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/**
 * Notification channel types.
 */
enum NotificationChannel {
    EMAIL,
    SMS,
    PUSH
}

/**
 * Notification priority levels.
 */
enum NotificationPriority {
    CRITICAL,  // < 1 second SLA
    HIGH,      // < 30 seconds SLA
    NORMAL,    // < 5 minutes SLA
    LOW        // < 1 hour SLA
}

/**
 * Notification delivery status.
 */
enum NotificationStatus {
    QUEUED,
    PROCESSING,
    SENT,
    DELIVERED,
    FAILED,
    BOUNCED
}

/**
 * Request to send a notification.
 */
class SendNotificationRequest {
    private final String userId;
    private final String templateId;
    private final NotificationChannel channel;
    private final NotificationPriority priority;
    private final Map<String, String> variables;
    private final Instant scheduledAt;
    private final String idempotencyKey;
    
    public SendNotificationRequest(String userId, String templateId,
                                   NotificationChannel channel,
                                   NotificationPriority priority,
                                   Map<String, String> variables,
                                   Instant scheduledAt,
                                   String idempotencyKey) {
        this.userId = userId;
        this.templateId = templateId;
        this.channel = channel;
        this.priority = priority != null ? priority : NotificationPriority.NORMAL;
        this.variables = variables;
        this.scheduledAt = scheduledAt;
        this.idempotencyKey = idempotencyKey;
    }
    
    // Getters
    public String getUserId() { return userId; }
    public String getTemplateId() { return templateId; }
    public NotificationChannel getChannel() { return channel; }
    public NotificationPriority getPriority() { return priority; }
    public Map<String, String> getVariables() { return variables; }
    public Instant getScheduledAt() { return scheduledAt; }
    public String getIdempotencyKey() { return idempotencyKey; }
}

/**
 * Response after sending notification.
 */
class SendNotificationResponse {
    private final String notificationId;
    private final NotificationStatus status;
    private final Instant estimatedDelivery;
    
    public SendNotificationResponse(String notificationId, 
                                    NotificationStatus status,
                                    Instant estimatedDelivery) {
        this.notificationId = notificationId;
        this.status = status;
        this.estimatedDelivery = estimatedDelivery;
    }
    
    public String getNotificationId() { return notificationId; }
    public NotificationStatus getStatus() { return status; }
    public Instant getEstimatedDelivery() { return estimatedDelivery; }
}

/**
 * Notification entity.
 */
class Notification {
    private final String notificationId;
    private final String userId;
    private final String templateId;
    private final NotificationChannel channel;
    private final NotificationPriority priority;
    private NotificationStatus status;
    private final Map<String, String> variables;
    private final String renderedContent;
    private final Instant createdAt;
    private Instant sentAt;
    private Instant deliveredAt;
    private int attemptCount;
    private String lastError;
    
    public Notification(String userId, String templateId,
                       NotificationChannel channel, NotificationPriority priority,
                       Map<String, String> variables, String renderedContent) {
        this.notificationId = UUID.randomUUID().toString();
        this.userId = userId;
        this.templateId = templateId;
        this.channel = channel;
        this.priority = priority;
        this.status = NotificationStatus.QUEUED;
        this.variables = variables;
        this.renderedContent = renderedContent;
        this.createdAt = Instant.now();
        this.attemptCount = 0;
    }
    
    public void markSent() {
        this.status = NotificationStatus.SENT;
        this.sentAt = Instant.now();
    }
    
    public void markDelivered() {
        this.status = NotificationStatus.DELIVERED;
        this.deliveredAt = Instant.now();
    }
    
    public void markFailed(String error) {
        this.status = NotificationStatus.FAILED;
        this.lastError = error;
    }
    
    public void incrementAttempt() {
        this.attemptCount++;
    }
    
    // Getters
    public String getNotificationId() { return notificationId; }
    public String getUserId() { return userId; }
    public String getTemplateId() { return templateId; }
    public NotificationChannel getChannel() { return channel; }
    public NotificationPriority getPriority() { return priority; }
    public NotificationStatus getStatus() { return status; }
    public Map<String, String> getVariables() { return variables; }
    public String getRenderedContent() { return renderedContent; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getSentAt() { return sentAt; }
    public Instant getDeliveredAt() { return deliveredAt; }
    public int getAttemptCount() { return attemptCount; }
    public String getLastError() { return lastError; }
}

/**
 * Main notification service interface.
 */
interface NotificationService {
    /**
     * Send a notification.
     */
    SendNotificationResponse send(SendNotificationRequest request);
    
    /**
     * Get notification status.
     */
    Optional<Notification> getStatus(String notificationId);
    
    /**
     * Cancel a scheduled notification.
     */
    boolean cancel(String notificationId);
}

/**
 * Template for notifications.
 */
class NotificationTemplate {
    private final String templateId;
    private final NotificationChannel channel;
    private final String name;
    private final String subject;  // For email
    private final String body;
    private final java.util.List<String> requiredVariables;
    private final int version;
    private final boolean active;
    
    public NotificationTemplate(String templateId, NotificationChannel channel,
                               String name, String subject, String body,
                               java.util.List<String> requiredVariables) {
        this.templateId = templateId;
        this.channel = channel;
        this.name = name;
        this.subject = subject;
        this.body = body;
        this.requiredVariables = requiredVariables;
        this.version = 1;
        this.active = true;
    }
    
    // Getters
    public String getTemplateId() { return templateId; }
    public NotificationChannel getChannel() { return channel; }
    public String getName() { return name; }
    public String getSubject() { return subject; }
    public String getBody() { return body; }
    public java.util.List<String> getRequiredVariables() { return requiredVariables; }
    public int getVersion() { return version; }
    public boolean isActive() { return active; }
}

/**
 * User notification preferences.
 */
class UserPreferences {
    private final String userId;
    private boolean emailEnabled;
    private boolean smsEnabled;
    private boolean pushEnabled;
    private String emailAddress;
    private String phoneNumber;
    private java.util.List<String> deviceTokens;
    
    public UserPreferences(String userId) {
        this.userId = userId;
        this.emailEnabled = true;
        this.smsEnabled = true;
        this.pushEnabled = true;
        this.deviceTokens = new java.util.ArrayList<>();
    }
    
    public boolean isChannelEnabled(NotificationChannel channel) {
        switch (channel) {
            case EMAIL: return emailEnabled;
            case SMS: return smsEnabled;
            case PUSH: return pushEnabled;
            default: return false;
        }
    }
    
    // Getters and setters
    public String getUserId() { return userId; }
    public boolean isEmailEnabled() { return emailEnabled; }
    public void setEmailEnabled(boolean enabled) { this.emailEnabled = enabled; }
    public boolean isSmsEnabled() { return smsEnabled; }
    public void setSmsEnabled(boolean enabled) { this.smsEnabled = enabled; }
    public boolean isPushEnabled() { return pushEnabled; }
    public void setPushEnabled(boolean enabled) { this.pushEnabled = enabled; }
    public String getEmailAddress() { return emailAddress; }
    public void setEmailAddress(String email) { this.emailAddress = email; }
    public String getPhoneNumber() { return phoneNumber; }
    public void setPhoneNumber(String phone) { this.phoneNumber = phone; }
    public java.util.List<String> getDeviceTokens() { return deviceTokens; }
}
