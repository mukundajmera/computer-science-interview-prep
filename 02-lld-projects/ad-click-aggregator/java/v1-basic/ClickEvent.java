package v1_basic;

public class ClickEvent {
    private final String eventId;
    private final String adId;
    private final String userId;
    private final long timestamp;

    public ClickEvent(String eventId, String adId, String userId, long timestamp) {
        this.eventId = eventId;
        this.adId = adId;
        this.userId = userId;
        this.timestamp = timestamp;
    }

    public String getEventId() { return eventId; }
    public String getAdId() { return adId; }
    public String getUserId() { return userId; }
    public long getTimestamp() { return timestamp; }
}
