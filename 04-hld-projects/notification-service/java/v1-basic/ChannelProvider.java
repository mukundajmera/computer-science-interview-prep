/**
 * Notification Service - V1 Basic
 * 
 * Channel providers for sending notifications.
 */

/**
 * Result of sending via a provider.
 */
class ProviderResult {
    private final boolean success;
    private final String messageId;
    private final String errorMessage;
    
    private ProviderResult(boolean success, String messageId, String errorMessage) {
        this.success = success;
        this.messageId = messageId;
        this.errorMessage = errorMessage;
    }
    
    public static ProviderResult success(String messageId) {
        return new ProviderResult(true, messageId, null);
    }
    
    public static ProviderResult failure(String errorMessage) {
        return new ProviderResult(false, null, errorMessage);
    }
    
    public boolean isSuccess() { return success; }
    public String getMessageId() { return messageId; }
    public String getErrorMessage() { return errorMessage; }
}

/**
 * Interface for notification channel providers.
 */
interface ChannelProvider {
    /**
     * Send a notification via this channel.
     */
    ProviderResult send(Notification notification, UserPreferences preferences);
    
    /**
     * Get the channel this provider handles.
     */
    NotificationChannel getChannel();
    
    /**
     * Check if provider is healthy.
     */
    boolean isHealthy();
}

/**
 * Email provider implementation (simulated).
 * In production: Use SendGrid, AWS SES, etc.
 */
class EmailProvider implements ChannelProvider {
    
    private final String providerName;
    private boolean healthy = true;
    
    public EmailProvider(String providerName) {
        this.providerName = providerName;
    }
    
    @Override
    public ProviderResult send(Notification notification, UserPreferences preferences) {
        String email = preferences.getEmailAddress();
        
        if (email == null || email.isEmpty()) {
            return ProviderResult.failure("No email address configured");
        }
        
        // Simulated send - in production, call provider API
        System.out.println("[" + providerName + "] Sending email to: " + email);
        System.out.println("  Subject: " + notification.getRenderedContent());
        
        // Simulate success
        String messageId = "msg-" + System.currentTimeMillis();
        return ProviderResult.success(messageId);
    }
    
    @Override
    public NotificationChannel getChannel() {
        return NotificationChannel.EMAIL;
    }
    
    @Override
    public boolean isHealthy() {
        return healthy;
    }
    
    public void setHealthy(boolean healthy) {
        this.healthy = healthy;
    }
}

/**
 * SMS provider implementation (simulated).
 * In production: Use Twilio, Vonage, etc.
 */
class SmsProvider implements ChannelProvider {
    
    private final String providerName;
    private boolean healthy = true;
    
    public SmsProvider(String providerName) {
        this.providerName = providerName;
    }
    
    @Override
    public ProviderResult send(Notification notification, UserPreferences preferences) {
        String phone = preferences.getPhoneNumber();
        
        if (phone == null || phone.isEmpty()) {
            return ProviderResult.failure("No phone number configured");
        }
        
        // Simulated send
        System.out.println("[" + providerName + "] Sending SMS to: " + phone);
        System.out.println("  Message: " + notification.getRenderedContent());
        
        String messageId = "sms-" + System.currentTimeMillis();
        return ProviderResult.success(messageId);
    }
    
    @Override
    public NotificationChannel getChannel() {
        return NotificationChannel.SMS;
    }
    
    @Override
    public boolean isHealthy() {
        return healthy;
    }
}

/**
 * Push notification provider implementation (simulated).
 * In production: Use Firebase FCM, APNs, etc.
 */
class PushProvider implements ChannelProvider {
    
    private final String providerName;
    private boolean healthy = true;
    
    public PushProvider(String providerName) {
        this.providerName = providerName;
    }
    
    @Override
    public ProviderResult send(Notification notification, UserPreferences preferences) {
        java.util.List<String> tokens = preferences.getDeviceTokens();
        
        if (tokens == null || tokens.isEmpty()) {
            return ProviderResult.failure("No device tokens registered");
        }
        
        // Simulated send to all devices
        for (String token : tokens) {
            System.out.println("[" + providerName + "] Sending push to token: " + 
                token.substring(0, Math.min(10, token.length())) + "...");
        }
        
        String messageId = "push-" + System.currentTimeMillis();
        return ProviderResult.success(messageId);
    }
    
    @Override
    public NotificationChannel getChannel() {
        return NotificationChannel.PUSH;
    }
    
    @Override
    public boolean isHealthy() {
        return healthy;
    }
}

/**
 * Channel router that selects appropriate provider.
 */
class ChannelRouter {
    
    private final java.util.Map<NotificationChannel, java.util.List<ChannelProvider>> 
        providers = new java.util.EnumMap<>(NotificationChannel.class);
    
    /**
     * Register a provider for a channel.
     */
    public void registerProvider(ChannelProvider provider) {
        providers.computeIfAbsent(provider.getChannel(), k -> new java.util.ArrayList<>())
                 .add(provider);
    }
    
    /**
     * Get a healthy provider for a channel.
     */
    public ChannelProvider getProvider(NotificationChannel channel) {
        java.util.List<ChannelProvider> channelProviders = providers.get(channel);
        
        if (channelProviders == null || channelProviders.isEmpty()) {
            throw new IllegalStateException("No providers for channel: " + channel);
        }
        
        // Return first healthy provider
        for (ChannelProvider provider : channelProviders) {
            if (provider.isHealthy()) {
                return provider;
            }
        }
        
        // All unhealthy - return first anyway
        return channelProviders.get(0);
    }
}
