import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.function.Consumer;

public class PubSubBus {
    private final ConcurrentHashMap<String, Set<Consumer<LocationUpdate>>> channelSubscribers;

    public PubSubBus() {
        this.channelSubscribers = new ConcurrentHashMap<>();
    }

    /**
     * Subscribe a callback to a specific channel.
     * @param channel The channel to subscribe to (e.g., user ID).
     * @param subscriber Callback to invoke when a message is published.
     */
    public void subscribe(String channel, Consumer<LocationUpdate> subscriber) {
        channelSubscribers.computeIfAbsent(channel, k -> new CopyOnWriteArraySet<>()).add(subscriber);
    }

    /**
     * Unsubscribe a callback from a specific channel.
     * @param channel The channel to unsubscribe from.
     * @param subscriber Callback to remove.
     */
    public void unsubscribe(String channel, Consumer<LocationUpdate> subscriber) {
        Set<Consumer<LocationUpdate>> subscribers = channelSubscribers.get(channel);
        if (subscribers != null) {
            subscribers.remove(subscriber);
            if (subscribers.isEmpty()) {
                channelSubscribers.remove(channel, subscribers);
            }
        }
    }

    /**
     * Publish a message to a specific channel.
     * @param channel The channel to publish to.
     * @param message The message to publish.
     */
    public void publish(String channel, LocationUpdate message) {
        Set<Consumer<LocationUpdate>> subscribers = channelSubscribers.get(channel);
        if (subscribers != null) {
            for (Consumer<LocationUpdate> subscriber : subscribers) {
                subscriber.accept(message);
            }
        }
    }
}
