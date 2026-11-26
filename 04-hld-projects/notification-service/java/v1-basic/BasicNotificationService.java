/**
 * Notification Service - V1 Basic
 * 
 * Basic notification service implementation.
 */

import java.time.Instant;
import java.util.Map;
import java.util.Optional;

/**
 * Basic implementation of notification service.
 * Single-threaded, synchronous processing.
 */
class BasicNotificationService implements NotificationService {
    
    private final TemplateService templateService;
    private final TemplateRenderer renderer;
    private final ChannelRouter channelRouter;
    private final PreferenceService preferenceService;
    private final NotificationRepository repository;
    
    public BasicNotificationService(TemplateService templateService,
                                    ChannelRouter channelRouter,
                                    PreferenceService preferenceService,
                                    NotificationRepository repository) {
        this.templateService = templateService;
        this.renderer = new TemplateRenderer();
        this.channelRouter = channelRouter;
        this.preferenceService = preferenceService;
        this.repository = repository;
    }
    
    @Override
    public SendNotificationResponse send(SendNotificationRequest request) {
        // Validate request
        validateRequest(request);
        
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
        
        // Create notification record
        Notification notification = new Notification(
            request.getUserId(),
            request.getTemplateId(),
            request.getChannel(),
            request.getPriority(),
            request.getVariables(),
            content.getBody()
        );
        
        // Save to repository
        repository.save(notification);
        
        // Send synchronously in v1 (async in v2+)
        try {
            ChannelProvider provider = channelRouter.getProvider(request.getChannel());
            ProviderResult result = provider.send(notification, prefs);
            
            if (result.isSuccess()) {
                notification.markSent();
                notification.markDelivered();
            } else {
                notification.markFailed(result.getErrorMessage());
            }
            
            repository.save(notification);
            
        } catch (Exception e) {
            notification.markFailed(e.getMessage());
            repository.save(notification);
        }
        
        return new SendNotificationResponse(
            notification.getNotificationId(),
            notification.getStatus(),
            Instant.now()
        );
    }
    
    @Override
    public Optional<Notification> getStatus(String notificationId) {
        return repository.findById(notificationId);
    }
    
    @Override
    public boolean cancel(String notificationId) {
        Optional<Notification> notification = repository.findById(notificationId);
        
        if (notification.isEmpty()) {
            return false;
        }
        
        // Can only cancel if still queued
        if (notification.get().getStatus() == NotificationStatus.QUEUED) {
            notification.get().markFailed("Cancelled by user");
            repository.save(notification.get());
            return true;
        }
        
        return false;
    }
    
    private void validateRequest(SendNotificationRequest request) {
        if (request.getUserId() == null || request.getUserId().isEmpty()) {
            throw new IllegalArgumentException("User ID is required");
        }
        if (request.getTemplateId() == null || request.getTemplateId().isEmpty()) {
            throw new IllegalArgumentException("Template ID is required");
        }
        if (request.getChannel() == null) {
            throw new IllegalArgumentException("Channel is required");
        }
    }
}

/**
 * Preference service interface.
 */
interface PreferenceService {
    UserPreferences getPreferences(String userId);
    void savePreferences(UserPreferences preferences);
}

/**
 * In-memory preference service.
 */
class InMemoryPreferenceService implements PreferenceService {
    
    private final Map<String, UserPreferences> store = 
        new java.util.concurrent.ConcurrentHashMap<>();
    
    @Override
    public UserPreferences getPreferences(String userId) {
        return store.computeIfAbsent(userId, UserPreferences::new);
    }
    
    @Override
    public void savePreferences(UserPreferences preferences) {
        store.put(preferences.getUserId(), preferences);
    }
}

/**
 * Notification repository interface.
 */
interface NotificationRepository {
    void save(Notification notification);
    Optional<Notification> findById(String notificationId);
    java.util.List<Notification> findByUserId(String userId);
}

/**
 * In-memory notification repository.
 */
class InMemoryNotificationRepository implements NotificationRepository {
    
    private final Map<String, Notification> store = 
        new java.util.concurrent.ConcurrentHashMap<>();
    
    @Override
    public void save(Notification notification) {
        store.put(notification.getNotificationId(), notification);
    }
    
    @Override
    public Optional<Notification> findById(String notificationId) {
        return Optional.ofNullable(store.get(notificationId));
    }
    
    @Override
    public java.util.List<Notification> findByUserId(String userId) {
        java.util.List<Notification> result = new java.util.ArrayList<>();
        for (Notification n : store.values()) {
            if (n.getUserId().equals(userId)) {
                result.add(n);
            }
        }
        return result;
    }
}

/**
 * Custom exceptions.
 */
class TemplateNotFoundException extends RuntimeException {
    public TemplateNotFoundException(String templateId) {
        super("Template not found: " + templateId);
    }
}

class UserOptedOutException extends RuntimeException {
    public UserOptedOutException(String message) {
        super(message);
    }
}
