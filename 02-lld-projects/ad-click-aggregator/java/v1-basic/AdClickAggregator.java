package v1_basic;

import java.util.HashSet;
import java.util.Set;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

class SimpleBloomFilter {
    private final int size;
    private final boolean[] bitArray;

    public SimpleBloomFilter(int size) {
        this.size = size;
        this.bitArray = new boolean[size];
    }

    private int hash(String item, int seed) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            String data = item + seed;
            byte[] hash = digest.digest(data.getBytes());
            int hashInt = ((hash[0] & 0xFF) << 24) |
                          ((hash[1] & 0xFF) << 16) |
                          ((hash[2] & 0xFF) << 8) |
                          (hash[3] & 0xFF);
            return (hashInt & 0x7FFFFFFF) % size;
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    public void add(String item) {
        bitArray[hash(item, 1)] = true;
        bitArray[hash(item, 2)] = true;
        bitArray[hash(item, 3)] = true;
    }

    public boolean mightContain(String item) {
        return bitArray[hash(item, 1)] &&
               bitArray[hash(item, 2)] &&
               bitArray[hash(item, 3)];
    }
}

public class AdClickAggregator {
    private final AggregationStore store;
    private final long windowSizeMs;
    private final SimpleBloomFilter bloomFilter;
    private final Set<String> exactSeenEvents;
    
    public AdClickAggregator(AggregationStore store, long windowSizeMs) {
        this.store = store;
        this.windowSizeMs = windowSizeMs;
        this.bloomFilter = new SimpleBloomFilter(10000);
        this.exactSeenEvents = new HashSet<>();
    }

    public AdClickAggregator() {
        this.store = new InMemoryAggregationStore();
        this.windowSizeMs = 60000;
        this.bloomFilter = new SimpleBloomFilter(10000);
        this.exactSeenEvents = new HashSet<>();
    }

    public void ingest(ClickEvent event) {
        // empty input and invalid event payloads fail predictably
        if (event == null || event.getEventId() == null || event.getEventId().isEmpty() || event.getAdId() == null || event.getAdId().isEmpty()) {
            throw new IllegalArgumentException("Invalid event payload");
        }

        String eventId = event.getEventId();
        // Duplicate event IDs affect billing aggregates exactly once; probabilistic filters only accelerate an exact deduplication check.
        if (bloomFilter.mightContain(eventId) && exactSeenEvents.contains(eventId)) {
            return;
        }
        
        // Window-boundary, late-event and out-of-order timestamp examples state processing-time/event-time policy
        long windowStartMs = (event.getTimestamp() / windowSizeMs) * windowSizeMs;
        AggregationKey key = new AggregationKey(event.getAdId(), windowStartMs);
        store.increment(key, 1);
        
        bloomFilter.add(eventId);
        exactSeenEvents.add(eventId);
    }

    public String getId() {
        return "AdClickAggregator";
    }
}
