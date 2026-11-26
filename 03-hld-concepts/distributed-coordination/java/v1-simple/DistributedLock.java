package v1simple;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class DistributedLock {

    public static class LockServer {
        private static class LockInfo {
            String owner;
            long token;
            long expiresAt;

            LockInfo(String owner, long token, long expiresAt) {
                this.owner = owner;
                this.token = token;
                this.expiresAt = expiresAt;
            }
        }

        private final Map<String, LockInfo> locks = new ConcurrentHashMap<>();
        private long fencingToken = 0;
        private final ReentrantLock serverLock = new ReentrantLock();

        public Long acquire(String lockName, String clientId, long ttlMillis) {
            serverLock.lock();
            try {
                long now = System.currentTimeMillis();
                if (locks.containsKey(lockName)) {
                    LockInfo info = locks.get(lockName);
                    if (info.expiresAt > now && !info.owner.equals(clientId)) {
                        return null; // Held by someone else
                    }
                }

                fencingToken++;
                long token = fencingToken;

                locks.put(lockName, new LockInfo(clientId, token, now + ttlMillis));
                return token;
            } finally {
                serverLock.unlock();
            }
        }

        public boolean renew(String lockName, String clientId, long ttlMillis, long token) {
            serverLock.lock();
            try {
                long now = System.currentTimeMillis();
                if (!locks.containsKey(lockName)) {
                    return false;
                }

                LockInfo info = locks.get(lockName);
                if (!info.owner.equals(clientId) || info.token != token) {
                    return false;
                }

                if (info.expiresAt < now) {
                    return false; // Expired, need to re-acquire
                }

                info.expiresAt = now + ttlMillis;
                return true;
            } finally {
                serverLock.unlock();
            }
        }

        public boolean release(String lockName, String clientId, long token) {
            serverLock.lock();
            try {
                if (!locks.containsKey(lockName)) {
                    return false;
                }

                LockInfo info = locks.get(lockName);
                if (!info.owner.equals(clientId) || info.token != token) {
                    return false;
                }

                locks.remove(lockName);
                return true;
            } finally {
                serverLock.unlock();
            }
        }
    }

    private final LockServer server;
    private final String lockName;
    private final String clientId;
    private final long ttlMillis;
    private final long heartbeatIntervalMillis;

    private Long token = null;
    private ScheduledExecutorService heartbeatExecutor;
    private final ReentrantLock localLock = new ReentrantLock();

    public DistributedLock(LockServer server, String lockName, long ttlMillis, long heartbeatIntervalMillis) {
        this.server = server;
        this.lockName = lockName;
        this.clientId = UUID.randomUUID().toString();
        this.ttlMillis = ttlMillis;
        this.heartbeatIntervalMillis = heartbeatIntervalMillis;
    }

    public Long acquire(boolean blocking, Long timeoutMillis) {
        long startTime = System.currentTimeMillis();
        while (true) {
            Long acquiredToken = server.acquire(lockName, clientId, ttlMillis);
            if (acquiredToken != null) {
                localLock.lock();
                try {
                    this.token = acquiredToken;
                    startHeartbeat();
                    return this.token;
                } finally {
                    localLock.unlock();
                }
            }

            if (!blocking) {
                return null;
            }

            if (timeoutMillis != null && (System.currentTimeMillis() - startTime >= timeoutMillis)) {
                return null;
            }

            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return null;
            }
        }
    }

    private void startHeartbeat() {
        if (heartbeatExecutor != null && !heartbeatExecutor.isShutdown()) {
            heartbeatExecutor.shutdownNow();
        }
        heartbeatExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r);
            t.setDaemon(true);
            return t;
        });

        heartbeatExecutor.scheduleAtFixedRate(() -> {
            localLock.lock();
            try {
                if (token == null) {
                    return;
                }
                boolean success = server.renew(lockName, clientId, ttlMillis, token);
                if (!success) {
                    token = null; // Lost lease
                }
            } finally {
                localLock.unlock();
            }
        }, heartbeatIntervalMillis, heartbeatIntervalMillis, TimeUnit.MILLISECONDS);
    }

    public boolean release() {
        localLock.lock();
        try {
            if (token == null) {
                return false;
            }

            if (heartbeatExecutor != null) {
                heartbeatExecutor.shutdownNow();
            }

            boolean success = server.release(lockName, clientId, token);
            token = null;
            return success;
        } finally {
            localLock.unlock();
        }
    }

    public Long getToken() {
        localLock.lock();
        try {
            return token;
        } finally {
            localLock.unlock();
        }
    }
}
