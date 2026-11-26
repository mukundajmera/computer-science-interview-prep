import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class PriceTrackingService {
    // Structure: productId -> retailer -> list of PriceObservation
    private final Map<String, Map<String, List<PriceObservation>>> history = new ConcurrentHashMap<>();

    public void recordPrice(PriceObservation obs) {
        history.computeIfAbsent(obs.getProductId(), k -> new ConcurrentHashMap<>())
               .computeIfAbsent(obs.getRetailer(), k -> Collections.synchronizedList(new ArrayList<>()))
               .add(obs);
    }

    public Optional<ProductPriceSummary> getPriceSummary(String productId) {
        Map<String, List<PriceObservation>> productHistory = history.get(productId);
        if (productHistory == null || productHistory.isEmpty()) {
            return Optional.empty();
        }

        double minPrice = Double.MAX_VALUE;
        double maxPrice = Double.MIN_VALUE;
        double currentPrice = 0.0;
        Instant lastUpdated = Instant.MIN;

        boolean hasRecords = false;

        for (List<PriceObservation> retailerRecords : productHistory.values()) {
            synchronized (retailerRecords) {
                if (retailerRecords.isEmpty()) {
                    continue;
                }
                hasRecords = true;

                // Find min and max for this retailer
                for (PriceObservation obs : retailerRecords) {
                    double price = obs.getPrice();
                    if (price < minPrice) minPrice = price;
                    if (price > maxPrice) maxPrice = price;
                }

                // Find the latest observation for this retailer
                PriceObservation latestForRetailer = retailerRecords.get(0);
                for (PriceObservation obs : retailerRecords) {
                    if (obs.getTimestamp().isAfter(latestForRetailer.getTimestamp())) {
                        latestForRetailer = obs;
                    }
                }

                // Update the overall current price (from the retailer with the most recent update)
                if (latestForRetailer.getTimestamp().isAfter(lastUpdated)) {
                    lastUpdated = latestForRetailer.getTimestamp();
                    currentPrice = latestForRetailer.getPrice();
                }
            }
        }

        if (!hasRecords) {
            return Optional.empty();
        }

        return Optional.of(new ProductPriceSummary(productId, minPrice, maxPrice, currentPrice, lastUpdated));
    }

    public List<PriceObservation> getPriceHistory(String productId, Instant from, Instant to) {
        Map<String, List<PriceObservation>> productHistory = history.get(productId);
        if (productHistory == null) {
            return Collections.emptyList();
        }

        List<PriceObservation> result = new ArrayList<>();
        for (List<PriceObservation> retailerRecords : productHistory.values()) {
            synchronized (retailerRecords) {
                for (PriceObservation obs : retailerRecords) {
                    if (!obs.getTimestamp().isBefore(from) && !obs.getTimestamp().isAfter(to)) {
                        result.add(obs);
                    }
                }
            }
        }

        // Sort by timestamp for consistency
        result.sort((o1, o2) -> o1.getTimestamp().compareTo(o2.getTimestamp()));
        return result;
    }

    public Optional<String> getLowestPriceRetailer(String productId) {
        Map<String, List<PriceObservation>> productHistory = history.get(productId);
        if (productHistory == null || productHistory.isEmpty()) {
            return Optional.empty();
        }

        String lowestRetailer = null;
        double lowestCurrentPrice = Double.MAX_VALUE;

        for (Map.Entry<String, List<PriceObservation>> entry : productHistory.entrySet()) {
            String retailer = entry.getKey();
            List<PriceObservation> retailerRecords = entry.getValue();

            synchronized (retailerRecords) {
                if (retailerRecords.isEmpty()) {
                    continue;
                }

                // Get current price for this retailer (latest timestamp)
                PriceObservation latestForRetailer = retailerRecords.get(0);
                for (PriceObservation obs : retailerRecords) {
                    if (obs.getTimestamp().isAfter(latestForRetailer.getTimestamp())) {
                        latestForRetailer = obs;
                    }
                }

                if (latestForRetailer.getPrice() < lowestCurrentPrice) {
                    lowestCurrentPrice = latestForRetailer.getPrice();
                    lowestRetailer = retailer;
                }
            }
        }

        return Optional.ofNullable(lowestRetailer);
    }
}
