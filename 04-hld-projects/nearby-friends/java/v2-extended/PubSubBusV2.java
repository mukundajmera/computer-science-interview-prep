import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

/**
 * v2 PubSubBus: v1 parity plus per-channel publish metrics
 * (improvement #2: fan-out multiplier, PITFALLS.md #3).
 * See NearbyFriendsServiceV2 for the full v2 list.
 */
public class PubSubBusV2 {
    private final ConcurrentHashMap<String, Set<Consumer<LocationUpdateV2>>> channelSubscribers;
    private final ConcurrentHashMap<String, AtomicInteger> publishCounts;

    public PubSubBusV2() {
        this.channelSubscribers = new ConcurrentHashMap<>();
        this.publishCounts = new ConcurrentHashMap<>();
    }

    public void subscribe(String channel, Consumer<LocationUpdateV2> subscriber) {
        channelSubscribers.computeIfAbsent(channel, k -> new CopyOnWriteArraySet<>()).add(subscriber);
    }

    public void unsubscribe(String channel, Consumer<LocationUpdateV2> subscriber) {
        Set<Consumer<LocationUpdateV2>> subscribers = channelSubscribers.get(channel);
        if (subscribers != null) {
            subscribers.remove(subscriber);
            if (subscribers.isEmpty()) {
                channelSubscribers.remove(channel, subscribers);
            }
        }
    }

    public void publish(String channel, LocationUpdateV2 message) {
        publishCounts.computeIfAbsent(channel, k -> new AtomicInteger(0)).incrementAndGet();
        Set<Consumer<LocationUpdateV2>> subscribers = channelSubscribers.get(channel);
        if (subscribers != null) {
            for (Consumer<LocationUpdateV2> subscriber : subscribers) {
                subscriber.accept(message);
            }
        }
    }

    /** Fan-out metric: total publishes on a channel (PITFALLS.md #3). */
    public int getPublishCount(String channel) {
        AtomicInteger count = publishCounts.get(channel);
        return count == null ? 0 : count.get();
    }
}
