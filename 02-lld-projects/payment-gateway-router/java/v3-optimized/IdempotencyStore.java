

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class IdempotencyStore {
    public enum State {
        IN_PROGRESS, COMPLETED, FAILED
    }

    private static class Record {
        State state;
        PaymentResponse response;
        long timestamp;
        final ReentrantLock lock = new ReentrantLock();

        Record(State state, PaymentResponse response) {
            this.state = state;
            this.response = response;
            this.timestamp = System.currentTimeMillis();
        }
    }

    private final Map<String, Record> store = new ConcurrentHashMap<>();
    private final long ttlMillis;

    public IdempotencyStore(long ttlMillis) {
        this.ttlMillis = ttlMillis;
    }

    public IdempotencyStore() {
        this(3600000); // 1 hour default
    }

    private void cleanupExpired(long currentTime) {
        store.entrySet().removeIf(entry -> currentTime - entry.getValue().timestamp > ttlMillis);
    }

    public boolean lockOrCheck(String key) {
        long currentTime = System.currentTimeMillis();
        cleanupExpired(currentTime);

        Record record = store.computeIfAbsent(key, k -> new Record(State.IN_PROGRESS, null));
        
        record.lock.lock();
        try {
            if (record.state == State.IN_PROGRESS && record.timestamp == currentTime) {
                 // newly created by computeIfAbsent since timestamp is exactly now, but could be slightly off...
                 // better check if response is null and state is in_progress
                 return true;
            }
            // if we are here and computeIfAbsent didn't create it, we need to check if we can lock it
            // actually computeIfAbsent is atomic, so we can use a slightly different pattern
        } finally {
            record.lock.unlock();
        }
        return false;
    }
    
    // Improved lockOrCheck
    public boolean lockOrCheckAtomic(String key) {
        long currentTime = System.currentTimeMillis();
        cleanupExpired(currentTime);
        
        Record[] newRec = new Record[1];
        Record record = store.compute(key, (k, existing) -> {
            if (existing == null) {
                newRec[0] = new Record(State.IN_PROGRESS, null);
                return newRec[0];
            }
            return existing;
        });
        
        return newRec[0] != null;
    }

    public State getState(String key) {
        Record record = store.get(key);
        if (record == null) return null;
        if (System.currentTimeMillis() - record.timestamp > ttlMillis) return null;
        
        record.lock.lock();
        try {
            return record.state;
        } finally {
            record.lock.unlock();
        }
    }

    public PaymentResponse getResponse(String key) {
        Record record = store.get(key);
        if (record == null) return null;
        if (System.currentTimeMillis() - record.timestamp > ttlMillis) return null;

        record.lock.lock();
        try {
            return record.response;
        } finally {
            record.lock.unlock();
        }
    }

    public void update(String key, State state, PaymentResponse response) {
        Record record = store.get(key);
        if (record != null) {
            record.lock.lock();
            try {
                record.state = state;
                record.response = response;
                record.timestamp = System.currentTimeMillis();
            } finally {
                record.lock.unlock();
            }
        } else {
            store.put(key, new Record(state, response));
        }
    }
}
