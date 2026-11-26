public class Notification {
    private String userId;
    private String message;
    private String channelType;

    public Notification(String userId, String message, String channelType) {
        this.userId = userId;
        this.message = message;
        this.channelType = channelType;
    }

    public String getUserId() { return userId; }
    public String getMessage() { return message; }
    public String getChannelType() { return channelType; }
}
