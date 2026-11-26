import java.util.HashSet;
import java.util.Set;
import java.util.ArrayList;
import java.util.List;

public class InboxConsumer {
    
    // Mocking an inbox table with a unique constraint
    private final Set<String> inboxTable = new HashSet<>();
    private final List<String> processedBusinessLogic = new ArrayList<>();

    public boolean consumeEvent(String eventId, String payload) {
        // Start local transaction (mocked)
        if (inboxTable.contains(eventId)) {
            // Duplicate detected (unique constraint violation in DB)
            // Ignore safely (idempotent)
            return false;
        }

        // 1. Insert into inbox
        inboxTable.add(eventId);

        // 2. Process business logic
        processedBusinessLogic.add(payload);

        // Commit transaction (mocked)
        return true;
    }

    public List<String> getProcessedItems() {
        return new ArrayList<>(processedBusinessLogic);
    }
}
