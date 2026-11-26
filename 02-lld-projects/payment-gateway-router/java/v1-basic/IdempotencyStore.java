import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class IdempotencyStore {
    public enum State {
        IN_PROGRESS, COMPLETED, FAILED
    }

    private static class Record {
        State state;
        PaymentResponse response;

        Record(State state, PaymentResponse response) {
            this.state = state;
            this.response = response;
        }
    }

    private final Map<String, Record> store = new ConcurrentHashMap<>();

    public synchronized boolean lockOrCheck(String key) {
        if (!store.containsKey(key)) {
            store.put(key, new Record(State.IN_PROGRESS, null));
            return true; // Successfully locked
        }
        return false; // Already exists
    }

    public synchronized State getState(String key) {
        Record record = store.get(key);
        return record != null ? record.state : null;
    }

    public synchronized PaymentResponse getResponse(String key) {
        Record record = store.get(key);
        return record != null ? record.response : null;
    }

    public synchronized void update(String key, State state, PaymentResponse response) {
        store.put(key, new Record(state, response));
    }
}
