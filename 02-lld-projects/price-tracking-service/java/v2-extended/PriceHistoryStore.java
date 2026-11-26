package v2_extended;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public interface PriceHistoryStore {
    void addPriceTick(String productId, String merchantId, PriceRecord record);
    Integer getCurrentPrice(String productId, String merchantId);
    List<PriceRecord> getHistory(String productId, String merchantId);
}

class InMemoryPriceHistoryStore implements PriceHistoryStore {
    private final Map<String, Map<String, List<PriceRecord>>> history = new ConcurrentHashMap<>();
    private final long retentionSeconds;
    private final java.time.Clock clock;

    public InMemoryPriceHistoryStore(long retentionSeconds, java.time.Clock clock) {
        this.retentionSeconds = retentionSeconds;
        this.clock = clock;
    }

    @Override
    public void addPriceTick(String productId, String merchantId, PriceRecord record) {
        history.computeIfAbsent(productId, k -> new ConcurrentHashMap<>())
               .computeIfAbsent(merchantId, k -> new ArrayList<>())
               .add(record);
        cleanup(productId, merchantId);
    }

    @Override
    public Integer getCurrentPrice(String productId, String merchantId) {
        List<PriceRecord> records = getHistory(productId, merchantId);
        if (records.isEmpty()) {
            return null;
        }
        return records.get(records.size() - 1).priceCents;
    }

    @Override
    public List<PriceRecord> getHistory(String productId, String merchantId) {
        return history.getOrDefault(productId, new ConcurrentHashMap<>())
                      .getOrDefault(merchantId, new ArrayList<>());
    }

    private void cleanup(String productId, String merchantId) {
        long cutoffTime = clock.instant().getEpochSecond() - retentionSeconds;
        List<PriceRecord> records = history.getOrDefault(productId, new ConcurrentHashMap<>()).get(merchantId);
        if (records != null) {
            records.removeIf(record -> record.timestamp < cutoffTime);
        }
    }
}
