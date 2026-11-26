package v1_basic;

import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

public class CdnSimulator {
    public static class CustomerOrigin {
        private Map<String, String> dataStore = new HashMap<>();
        public int fetchCount = 0;

        public void put(String path, String data) {
            dataStore.put(path, data);
        }

        public String fetch(String path) {
            fetchCount++;
            return dataStore.get(path);
        }
    }

    public static class OriginShield {
        private CustomerOrigin origin;
        private Map<String, String> cache = new HashMap<>();
        private Map<String, List<Object>> inFlightRequests = new HashMap<>();
        public int cacheHitCount = 0;
        public int fetchCount = 0;

        public OriginShield(CustomerOrigin origin) {
            this.origin = origin;
        }

        public String fetch(String path) {
            fetchCount++;
            if (cache.containsKey(path)) {
                cacheHitCount++;
                return cache.get(path);
            }

            // Simulate Request Coalescing (Thundering Herd protection)
            if (inFlightRequests.containsKey(path)) {
                // In a real system, this thread would wait on a future/promise
                // Here we just return a special coalesced marker or simulate the waiting
                // by fetching it after it's done. For our synchronous mock, we just
                // assume the first request populates it, and subsequent coalesced ones 
                // just use the result. We simulate this by checking if it's already in flight,
                // and if so, just returning the data if it gets populated by the "main" request.
                // Since this is a simple sequential simulator, we won't hit true concurrency issues,
                // but we can model coalescing logic explicitly for tests.
                
                // For a single threaded simulator, if we explicitly batch requests:
                return "COALESCED";
            }
            
            inFlightRequests.put(path, new ArrayList<>());
            String data = origin.fetch(path);
            if (data != null) {
                cache.put(path, data);
            }
            inFlightRequests.remove(path);
            return data;
        }
        
        public void simulateConcurrentFetches(String path, int numRequests, List<String> results) {
            fetchCount += numRequests;
            if (cache.containsKey(path)) {
                cacheHitCount += numRequests;
                for (int i = 0; i < numRequests; i++) {
                    results.add(cache.get(path));
                }
                return;
            }
            
            // Simulating coalescing: 1 request goes to origin, the rest wait
            String data = origin.fetch(path);
            if (data != null) {
                cache.put(path, data);
            }
            for (int i = 0; i < numRequests; i++) {
                results.add(data);
            }
        }
    }

    public static class EdgeNode {
        private OriginShield shield;
        private Map<String, String> cache = new HashMap<>();
        public int cacheHitCount = 0;

        public EdgeNode(OriginShield shield) {
            this.shield = shield;
        }

        public String fetch(String path) {
            if (cache.containsKey(path)) {
                cacheHitCount++;
                return cache.get(path);
            }

            String data = shield.fetch(path);
            if (data != null && !data.equals("COALESCED")) {
                cache.put(path, data);
            }
            return data;
        }
        
        public void fetchBatch(String path, int count, List<String> results) {
             if (cache.containsKey(path)) {
                cacheHitCount += count;
                for(int i=0; i<count; i++) {
                     results.add(cache.get(path));
                }
                return;
             }
             shield.simulateConcurrentFetches(path, count, results);
             if (results.size() > 0 && results.get(0) != null) {
                 cache.put(path, results.get(0));
             }
        }

        public void purge(String path) {
            cache.remove(path);
        }
    }
}
