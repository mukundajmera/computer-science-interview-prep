package v3;

import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

public class DistributedWebCrawler {

    public static class Coordinator {
        private final Map<String, Boolean> globalDedup = new ConcurrentHashMap<>();
        private final NavigableMap<Integer, String> hashRing = new ConcurrentSkipListMap<>();
        private final Map<String, Long> lastHeartbeat = new ConcurrentHashMap<>();
        private final Map<String, Map<String, TokenBucket>> globalRateLimits = new ConcurrentHashMap<>();

        public synchronized void registerWorker(String workerId) {
            int hash = hash(workerId);
            hashRing.put(hash, workerId);
            lastHeartbeat.put(workerId, System.currentTimeMillis());
            globalRateLimits.putIfAbsent(workerId, new ConcurrentHashMap<>());
        }

        public synchronized void removeWorker(String workerId) {
            hashRing.entrySet().removeIf(entry -> entry.getValue().equals(workerId));
            lastHeartbeat.remove(workerId);
            globalRateLimits.remove(workerId);
        }

        public void heartbeat(String workerId) {
            lastHeartbeat.put(workerId, System.currentTimeMillis());
        }

        public String getWorkerForHost(String host) {
            if (hashRing.isEmpty()) return null;
            int hash = hash(host);
            Map.Entry<Integer, String> entry = hashRing.ceilingEntry(hash);
            if (entry == null) {
                entry = hashRing.firstEntry();
            }
            return entry.getValue();
        }

        public boolean checkAndSetGlobalDedup(String hash) {
            return globalDedup.putIfAbsent(hash, true) == null;
        }

        public void unsetGlobalDedup(String hash) {
            globalDedup.remove(hash);
        }

        public List<String> getDeadWorkers(long timeoutMs) {
            long now = System.currentTimeMillis();
            List<String> dead = new ArrayList<>();
            for (Map.Entry<String, Long> entry : lastHeartbeat.entrySet()) {
                if (now - entry.getValue() > timeoutMs) {
                    dead.add(entry.getKey());
                }
            }
            return dead;
        }

        public Map<String, Map<String, TokenBucket>> getRateLimits() {
             return globalRateLimits;
        }

        private int hash(String key) {
            try {
                MessageDigest md = MessageDigest.getInstance("MD5");
                byte[] digest = md.digest(key.getBytes(StandardCharsets.UTF_8));
                return ((digest[3] & 0xFF) << 24) |
                       ((digest[2] & 0xFF) << 16) |
                       ((digest[1] & 0xFF) << 8) |
                       (digest[0] & 0xFF);
            } catch (NoSuchAlgorithmException e) {
                return key.hashCode();
            }
        }
    }

    public static class TokenBucket {
        private final int capacity;
        private final int refillRatePerSecond;
        private double tokens;
        private long lastRefillTimestamp;

        public TokenBucket(int capacity, int refillRatePerSecond) {
            this.capacity = capacity;
            this.refillRatePerSecond = refillRatePerSecond;
            this.tokens = capacity;
            this.lastRefillTimestamp = System.currentTimeMillis();
        }

        public synchronized boolean tryConsume() {
            refill();
            if (tokens >= 1.0) {
                tokens -= 1.0;
                return true;
            }
            return false;
        }

        private void refill() {
            long now = System.currentTimeMillis();
            double timePassedSeconds = (now - lastRefillTimestamp) / 1000.0;
            double tokensToAdd = timePassedSeconds * refillRatePerSecond;
            tokens = Math.min(capacity, tokens + tokensToAdd);
            lastRefillTimestamp = now;
        }
    }

    public static class LocalBloomFilter {
        private final BitSet bitSet;
        private final int size;
        private final int numHashes;

        public LocalBloomFilter(int expectedElements, double falsePositiveRate) {
            this.size = (int) Math.ceil(-(expectedElements * Math.log(falsePositiveRate)) / (Math.log(2) * Math.log(2)));
            this.numHashes = (int) Math.ceil((size / (double) expectedElements) * Math.log(2));
            this.bitSet = new BitSet(size);
        }

        private int[] getHashes(String val) {
            int[] hashes = new int[numHashes];
            int h1 = val.hashCode();
            int h2 = h1 >>> 16;
            for(int i = 0; i < numHashes; i++) {
                hashes[i] = Math.abs((h1 + i * h2) % size);
            }
            return hashes;
        }

        public synchronized void add(String val) {
            int[] hashes = getHashes(val);
            for (int h : hashes) {
                bitSet.set(h);
            }
        }

        public synchronized boolean mightContain(String val) {
            int[] hashes = getHashes(val);
            for (int h : hashes) {
                if (!bitSet.get(h)) {
                    return false;
                }
            }
            return true;
        }
    }

    public static class WorkerNode {
        private final String workerId;
        private final Coordinator coordinator;
        private final PriorityBlockingQueue<String> localFrontier = new PriorityBlockingQueue<>();
        private final LocalBloomFilter localDedup = new LocalBloomFilter(10000, 0.01);
        private final Map<String, TokenBucket> rateLimits = new ConcurrentHashMap<>();

        private boolean isRunning = true;

        public WorkerNode(String workerId, Coordinator coordinator) {
            this.workerId = workerId;
            this.coordinator = coordinator;
            this.coordinator.registerWorker(workerId);
        }

        public void submitUrl(String url) {
            String host = getHost(url);
            if (host == null) return;
            String targetWorker = coordinator.getWorkerForHost(host);
            if (targetWorker != null && targetWorker.equals(workerId)) {
                if (isUnique(url)) {
                    localFrontier.add(url);
                }
            }
        }

        public void forceSubmitLocal(String url) {
             localFrontier.add(url);
        }

        public String fetchNext() {
            String url = localFrontier.poll();
            if (url == null) return null;

            String host = getHost(url);
            if(host != null) {
                 TokenBucket bucket = rateLimits.computeIfAbsent(host, k -> new TokenBucket(5, 1));
                 if(!bucket.tryConsume()) {
                      localFrontier.add(url);
                      return null;
                 }
            }

            return url;
        }

        public void heartbeat() {
             if (isRunning) {
                 coordinator.heartbeat(workerId);
             }
        }

        public void stop() {
            isRunning = false;
        }

        public PriorityBlockingQueue<String> getLocalFrontier() {
             return localFrontier;
        }

        private boolean isUnique(String url) {
             String hash = hash(url);
             if (localDedup.mightContain(hash)) {
                  return coordinator.checkAndSetGlobalDedup(hash);
             } else {
                  localDedup.add(hash);
                  coordinator.checkAndSetGlobalDedup(hash);
                  return true;
             }
        }

        public String getHost(String urlStr) {
            try {
                URI uri = new URI(urlStr);
                return uri.getHost();
            } catch (URISyntaxException e) {
                return null;
            }
        }

        public String hash(String input) {
            try {
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
                StringBuilder hexString = new StringBuilder();
                for (byte b : hash) {
                    String hex = Integer.toHexString(0xff & b);
                    if (hex.length() == 1) hexString.append('0');
                    hexString.append(hex);
                }
                return hexString.toString();
            } catch (NoSuchAlgorithmException e) {
                 return String.valueOf(input.hashCode());
            }
        }

        public String getWorkerId() { return workerId; }
    }

    private final Coordinator coordinator = new Coordinator();
    private final Map<String, WorkerNode> workers = new ConcurrentHashMap<>();

    public Coordinator getCoordinator() {
         return coordinator;
    }

    public WorkerNode addWorker(String workerId) {
        WorkerNode worker = new WorkerNode(workerId, coordinator);
        workers.put(workerId, worker);
        return worker;
    }

    public void submitToCluster(String url) {
         try {
            URI uri = new URI(url);
            String host = uri.getHost();
            if (host == null) return;
            String workerId = coordinator.getWorkerForHost(host);
            if (workerId != null) {
                 WorkerNode worker = workers.get(workerId);
                 if (worker != null) {
                      worker.submitUrl(url);
                 }
            }
         } catch (URISyntaxException e) {
         }
    }

    public void removeWorker(String workerId) {
        WorkerNode worker = workers.remove(workerId);
        if (worker != null) {
            worker.stop();
        }
        coordinator.removeWorker(workerId);
    }

    public void detectAndRecoverFailures(long timeoutMs) {
         List<String> deadWorkers = coordinator.getDeadWorkers(timeoutMs);
         for (String deadWorkerId : deadWorkers) {
              WorkerNode deadWorker = workers.remove(deadWorkerId);
              coordinator.removeWorker(deadWorkerId);

              if (deadWorker != null) {
                   PriorityBlockingQueue<String> orphanedFrontier = deadWorker.getLocalFrontier();
                   String url;
                   while ((url = orphanedFrontier.poll()) != null) {
                        coordinator.unsetGlobalDedup(deadWorker.hash(url));
                        String host = deadWorker.getHost(url);
                        if (host != null) {
                            String targetWorkerId = coordinator.getWorkerForHost(host);
                            if (targetWorkerId != null) {
                                WorkerNode targetWorker = workers.get(targetWorkerId);
                                if (targetWorker != null) {
                                    targetWorker.forceSubmitLocal(url);
                                }
                            }
                        }
                   }
              }
         }
    }
}
