package v2_extended;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Semaphore;
import java.util.Map;

public class HostRateLimiter {
    private final int maxConcurrentPerHost;
    private final Map<String, Semaphore> hostSemaphores = new ConcurrentHashMap<>();

    public HostRateLimiter(int maxConcurrentPerHost) {
        this.maxConcurrentPerHost = maxConcurrentPerHost;
    }

    public boolean tryAcquire(String host) {
        return hostSemaphores.computeIfAbsent(host, k -> new Semaphore(maxConcurrentPerHost)).tryAcquire();
    }
    
    public void release(String host) {
        Semaphore sem = hostSemaphores.get(host);
        if (sem != null) {
            sem.release();
        }
    }
}
