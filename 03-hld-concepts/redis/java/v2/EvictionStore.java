package v2;

import java.util.*;

public class EvictionStore {
    private final int capacity;
    private final String policy;
    private final Map<String, Object> store;
    private final Map<String, Long> ttls;
    private final List<String> lruOrder;

    public EvictionStore(int capacity, String policy) {
        this.capacity = capacity;
        this.policy = policy;
        this.store = new HashMap<>();
        this.ttls = new HashMap<>();
        this.lruOrder = new ArrayList<>();
    }

    public void set(String key, Object value, Long ttl) {
        boolean isNew = !store.containsKey(key);
        if (isNew) {
            enforceCapacity();
        }
        store.put(key, value);
        if (ttl != null) {
            ttls.put(key, System.currentTimeMillis() + ttl);
        }

        lruOrder.remove(key);
        lruOrder.add(key);
    }

    public Object get(String key) {
        if (!store.containsKey(key)) {
            return null;
        }

        if (ttls.containsKey(key) && System.currentTimeMillis() > ttls.get(key)) {
            delete(key);
            return null;
        }

        if (lruOrder.remove(key)) {
            lruOrder.add(key);
        }

        return store.get(key);
    }

    private void enforceCapacity() {
        long now = System.currentTimeMillis();
        List<String> expired = new ArrayList<>();
        for (Map.Entry<String, Long> entry : ttls.entrySet()) {
            if (now > entry.getValue()) {
                expired.add(entry.getKey());
            }
        }
        for (String k : expired) {
            delete(k);
        }

        while (store.size() >= capacity) {
            if ("allkeys-lru".equals(policy)) {
                evictAllkeysLru();
            } else if ("volatile-lru".equals(policy)) {
                boolean success = evictVolatileLru();
                if (!success) {
                    throw new OutOfMemoryError("OOM command not allowed when used memory > 'maxmemory'.");
                }
            } else {
                throw new IllegalArgumentException("Unknown policy: " + policy);
            }
        }
    }

    private void evictAllkeysLru() {
        if (lruOrder.isEmpty()) {
            return;
        }
        String lruKey = lruOrder.get(0);
        delete(lruKey);
    }

    private boolean evictVolatileLru() {
        for (String key : lruOrder) {
            if (ttls.containsKey(key)) {
                delete(key);
                return true;
            }
        }
        return false;
    }

    private void delete(String key) {
        store.remove(key);
        ttls.remove(key);
        lruOrder.remove(key);
    }
}
