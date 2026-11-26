public class Notification implements Comparable<Notification> {
    private String userId;
    private String message;
    private String channelType;
    private int priority;
    private long timestamp;
    private int attempts;
    private long nextRetryTime;

    public Notification(String userId, String message, String channelType, int priority) {
        this.userId = userId;
        this.message = message;
        this.channelType = channelType;
        this.priority = priority;
        this.timestamp = System.nanoTime();
        this.attempts = 0;
        this.nextRetryTime = 0;
    }

    public String getUserId() { return userId; }
    public String getMessage() { return message; }
    public String getChannelType() { return channelType; }
    public int getPriority() { return priority; }
    public long getTimestamp() { return timestamp; }
    public int getAttempts() { return attempts; }
    public void incrementAttempts() { this.attempts++; }
    public long getNextRetryTime() { return nextRetryTime; }
    public void setNextRetryTime(long nextRetryTime) { this.nextRetryTime = nextRetryTime; }

    @Override
    public int compareTo(Notification other) {
        if (this.priority != other.priority) {
            return Integer.compare(this.priority, other.priority);
        }
        return Long.compare(this.timestamp, other.timestamp);
    }
}
