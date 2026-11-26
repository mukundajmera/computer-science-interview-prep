package v3_optimized;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.HashMap;

public class RingBuffer {
    
    public static class OptimizedPriceTracker {
        private final int windowSize;
        private final ReentrantLock lock = new ReentrantLock();
        
        private final Map<String, Map<String, PriceRingBuffer>> buffers = new HashMap<>();

        public OptimizedPriceTracker(int windowSize) {
            this.windowSize = windowSize;
        }

        private PriceRingBuffer getOrCreateBuffer(String productId, String merchantId) {
            lock.lock();
            try {
                buffers.putIfAbsent(productId, new HashMap<>());
                buffers.get(productId).putIfAbsent(merchantId, new PriceRingBuffer(windowSize));
                return buffers.get(productId).get(merchantId);
            } finally {
                lock.unlock();
            }
        }

        public boolean addTick(String productId, String merchantId, v2_extended.PriceRecord record) {
            PriceRingBuffer buffer = getOrCreateBuffer(productId, merchantId);
            return buffer.add(record);
        }
        
        public Map<String, Object> getStats(String productId, String merchantId) {
            lock.lock();
            try {
                if (!buffers.containsKey(productId) || !buffers.get(productId).containsKey(merchantId)) {
                    Map<String, Object> result = new HashMap<>();
                    result.put("moving_average", null);
                    result.put("all_time_low", null);
                    result.put("current_price", null);
                    return result;
                }
                PriceRingBuffer buffer = buffers.get(productId).get(merchantId);
                Map<String, Object> result = new HashMap<>();
                result.put("moving_average", buffer.getMovingAverage());
                result.put("all_time_low", buffer.getAllTimeLow());
                result.put("current_price", buffer.getCurrentPrice());
                return result;
            } finally {
                lock.unlock();
            }
        }
    }

    public static class OptimizedPriceHistoryStore implements v2_extended.PriceHistoryStore {
        private final OptimizedPriceTracker tracker;
        private final Map<String, Map<String, java.util.List<v2_extended.PriceRecord>>> history = new ConcurrentHashMap<>();
        private final long retentionSeconds;
        private final java.time.Clock clock;

        public OptimizedPriceHistoryStore(long retentionSeconds, java.time.Clock clock) {
            this.retentionSeconds = retentionSeconds;
            this.clock = clock;
            this.tracker = new OptimizedPriceTracker(1000);
        }

        @Override
        public void addPriceTick(String productId, String merchantId, v2_extended.PriceRecord record) {
            if (tracker.addTick(productId, merchantId, record)) {
                history.computeIfAbsent(productId, k -> new ConcurrentHashMap<>())
                       .computeIfAbsent(merchantId, k -> new java.util.ArrayList<>())
                       .add(record);
            }
            cleanup(productId, merchantId);
        }

        @Override
        public Integer getCurrentPrice(String productId, String merchantId) {
            Map<String, Object> stats = tracker.getStats(productId, merchantId);
            return (Integer) stats.get("current_price");
        }

        @Override
        public java.util.List<v2_extended.PriceRecord> getHistory(String productId, String merchantId) {
            return history.getOrDefault(productId, new ConcurrentHashMap<>())
                          .getOrDefault(merchantId, new java.util.ArrayList<>());
        }

        private void cleanup(String productId, String merchantId) {
            long cutoffTime = clock.instant().getEpochSecond() - retentionSeconds;
            java.util.List<v2_extended.PriceRecord> records = history.getOrDefault(productId, new ConcurrentHashMap<>()).get(merchantId);
            if (records != null) {
                records.removeIf(record -> record.timestamp < cutoffTime);
            }
        }
    }

    public static class PriceRingBuffer {
        private final int size;
        private final v2_extended.PriceRecord[] buffer;
        private int head = 0;
        private int count = 0;
        
        private long runningSum = 0;
        private Integer allTimeLow = null;
        private v2_extended.PriceRecord lastRecord = null;
        
        private final int bloomSize = 1024;
        private final boolean[] bloomFilter = new boolean[bloomSize];
        
        private final ReentrantLock lock = new ReentrantLock();

        public PriceRingBuffer(int size) {
            this.size = size;
            this.buffer = new v2_extended.PriceRecord[size];
        }

        private int[] hashFuncs(String val) {
            try {
                java.security.MessageDigest md = java.security.MessageDigest.getInstance("MD5");
                byte[] hash = md.digest(val.getBytes());
                int h1 = Math.abs(java.nio.ByteBuffer.wrap(hash, 0, 4).getInt()) % bloomSize;
                int h2 = Math.abs(java.nio.ByteBuffer.wrap(hash, 4, 4).getInt()) % bloomSize;
                int h3 = Math.abs(java.nio.ByteBuffer.wrap(hash, 8, 4).getInt()) % bloomSize;
                return new int[]{h1, h2, h3};
            } catch (Exception e) {
                return new int[]{0, 0, 0};
            }
        }

        public boolean add(v2_extended.PriceRecord record) {
            lock.lock();
            try {
                String recordKey = record.timestamp + ":" + record.priceCents;
                int[] hashes = hashFuncs(recordKey);
                
                boolean mightContain = true;
                for (int idx : hashes) {
                    if (!bloomFilter[idx]) {
                        mightContain = false;
                        break;
                    }
                }
                
                if (mightContain) {
                    boolean isExactDup = false;
                    if (lastRecord != null && lastRecord.timestamp == record.timestamp && lastRecord.priceCents == record.priceCents) {
                        isExactDup = true;
                    } else {
                        for (int i = 0; i < count; i++) {
                            int idx = (head - 1 - i + size) % size;
                            v2_extended.PriceRecord item = buffer[idx];
                            if (item != null && item.timestamp == record.timestamp && item.priceCents == record.priceCents) {
                                isExactDup = true;
                                break;
                            }
                        }
                    }
                    if (isExactDup) {
                        return false;
                    }
                }
                
                for (int idx : hashes) {
                    bloomFilter[idx] = true;
                }
                    
                lastRecord = record;

                if (allTimeLow == null || record.priceCents < allTimeLow) {
                    allTimeLow = record.priceCents;
                }

                if (count == size) {
                    v2_extended.PriceRecord oldest = buffer[head];
                    if (oldest != null) {
                        runningSum -= oldest.priceCents;
                    }
                } else {
                    count++;
                }

                buffer[head] = record;
                runningSum += record.priceCents;
                
                head = (head + 1) % size;
                return true;
            } finally {
                lock.unlock();
            }
        }

        public Double getMovingAverage() {
            lock.lock();
            try {
                if (count == 0) {
                    return null;
                }
                return (double) runningSum / count;
            } finally {
                lock.unlock();
            }
        }

        public Integer getAllTimeLow() {
            lock.lock();
            try {
                return allTimeLow;
            } finally {
                lock.unlock();
            }
        }
        
        public Integer getCurrentPrice() {
            lock.lock();
            try {
                if (lastRecord == null) {
                    return null;
                }
                return lastRecord.priceCents;
            } finally {
                lock.unlock();
            }
        }
    }
}
