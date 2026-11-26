
import java.util.Map;

public class Event {
    private final String topic;
    private final Map<String, Object> payload;

    public Event(String topic, Map<String, Object> payload) {
        this.topic = topic;
        this.payload = payload;
    }

    public String getTopic() { return topic; }
    public Map<String, Object> getPayload() { return payload; }
}
