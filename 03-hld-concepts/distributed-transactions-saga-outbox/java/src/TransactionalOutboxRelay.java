import java.util.ArrayList;
import java.util.List;

public class TransactionalOutboxRelay {

    public static class OutboxEvent {
        public final String eventId;
        public final String aggregateType;
        public final String payload;

        public OutboxEvent(String eventId, String aggregateType, String payload) {
            this.eventId = eventId;
            this.aggregateType = aggregateType;
            this.payload = payload;
        }
    }

    // Mocking the database tables
    private final List<OutboxEvent> outboxTable = new ArrayList<>();
    private final List<OutboxEvent> publishedLog = new ArrayList<>();

    // Called within a local transaction
    public void insertEvent(OutboxEvent event) {
        outboxTable.add(event);
    }

    // Called by a CDC tool (e.g. Debezium) asynchronously
    public void relayEvents() {
        for (OutboxEvent event : outboxTable) {
            // Mock publishing to broker
            publishToBroker(event);
        }
        // In CDC, the tool tails the log and doesn't delete, but we clear it for testing mock
        outboxTable.clear();
    }

    private void publishToBroker(OutboxEvent event) {
        publishedLog.add(event);
    }

    public List<OutboxEvent> getPublishedEvents() {
        return new ArrayList<>(publishedLog);
    }
}
