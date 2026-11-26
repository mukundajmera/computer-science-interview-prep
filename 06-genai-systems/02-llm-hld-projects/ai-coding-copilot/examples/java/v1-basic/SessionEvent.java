public class SessionEvent {
    private final String eventType;
    private final String detail;

    public SessionEvent(String eventType, String detail) {
        this.eventType = eventType;
        this.detail = detail;
    }

    public String getEventType() {
        return eventType;
    }

    public String getDetail() {
        return detail;
    }
}
