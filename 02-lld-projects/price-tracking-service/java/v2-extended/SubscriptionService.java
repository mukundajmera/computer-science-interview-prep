package v2_extended;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class SubscriptionService {
    private final PriceHistoryStore historyStore;
    private final RateLimitedDispatcher dispatcher;
    private final Map<String, List<PriceAlertSubscription>> subscriptions = new ConcurrentHashMap<>();
    private final Map<String, Boolean> alertState = new ConcurrentHashMap<>();

    public SubscriptionService(PriceHistoryStore historyStore, RateLimitedDispatcher dispatcher) {
        this.historyStore = historyStore;
        this.dispatcher = dispatcher;
    }

    public void subscribe(PriceAlertSubscription subscription) {
        subscriptions.computeIfAbsent(subscription.productId, k -> new ArrayList<>()).add(subscription);
    }

    public void unsubscribe(String subscriptionId) {
        for (List<PriceAlertSubscription> subs : subscriptions.values()) {
            subs.removeIf(sub -> sub.id.equals(subscriptionId));
        }
    }

    public void onPriceUpdate(String productId, String merchantId, PriceRecord record) {
        List<PriceRecord> history = historyStore.getHistory(productId, merchantId);
        
        // Out of order timestamps: Ignore older events
        if (!history.isEmpty()) {
            long maxTimestamp = history.stream().mapToLong(r -> r.timestamp).max().orElse(0);
            if (record.timestamp < maxTimestamp) {
                return;
            }
        }
        
        historyStore.addPriceTick(productId, merchantId, record);
        checkAlerts(productId, merchantId, record);
    }

    private void checkAlerts(String productId, String merchantId, PriceRecord currentRecord) {
        List<PriceAlertSubscription> subs = subscriptions.getOrDefault(productId, new ArrayList<>());
        for (PriceAlertSubscription sub : subs) {
            boolean conditionMet = false;
            
            if (sub.thresholdPrice.isPresent() && currentRecord.priceCents < sub.thresholdPrice.get()) {
                conditionMet = true;
            }
            
            if (!conditionMet && sub.percentageDrop.isPresent()) {
                long now = currentRecord.timestamp;
                List<PriceRecord> history = historyStore.getHistory(productId, merchantId);
                long twentyFourHoursAgo = now - (24 * 60 * 60);
                
                List<PriceRecord> oldRecords = history.stream()
                    .filter(r -> r.timestamp <= twentyFourHoursAgo)
                    .collect(Collectors.toList());
                
                if (!oldRecords.isEmpty()) {
                    PriceRecord oldPriceRecord = oldRecords.stream().max((r1, r2) -> Long.compare(r1.timestamp, r2.timestamp)).get();
                    int oldPrice = oldPriceRecord.priceCents;
                    if (oldPrice > 0) {
                        double drop = ((double)(oldPrice - currentRecord.priceCents) / oldPrice) * 100.0;
                        if (drop >= sub.percentageDrop.get()) {
                            conditionMet = true;
                        }
                    }
                }
            }
            
            String alertKey = sub.id + ":" + merchantId;
            boolean previouslyAlerted = alertState.getOrDefault(alertKey, false);

            if (conditionMet) {
                if (!previouslyAlerted) {
                    String msg = String.format("Price alert for %s: %d cents", productId, currentRecord.priceCents);
                    dispatcher.dispatch(sub.id, sub.userId, sub.channel, msg);
                    alertState.put(alertKey, true);
                }
            } else {
                alertState.put(alertKey, false);
            }
        }
    }
}

// substantive change
