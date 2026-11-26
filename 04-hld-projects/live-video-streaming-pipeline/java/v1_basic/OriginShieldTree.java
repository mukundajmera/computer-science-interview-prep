package v1_basic;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class OriginShieldTree {
    private final Map<String, String> l1Cache = new ConcurrentHashMap<>();
    private final Map<String, String> l2Cache = new ConcurrentHashMap<>();
    private final Map<String, String> origin = new ConcurrentHashMap<>();
    private final Lock lock = new ReentrantLock();

    public void writeToOrigin(String key, String value) {
        lock.lock();
        try {
            origin.put(key, value);
        } finally {
            lock.unlock();
        }
    }

    public String fetch(String key) {
        lock.lock();
        try {
            if (l1Cache.containsKey(key)) {
                return l1Cache.get(key);
            }
            if (l2Cache.containsKey(key)) {
                String val = l2Cache.get(key);
                l1Cache.put(key, val);
                return val;
            }
            if (origin.containsKey(key)) {
                String val = origin.get(key);
                l2Cache.put(key, val);
                l1Cache.put(key, val);
                return val;
            }
            return null;
        } finally {
            lock.unlock();
        }
    }
}
