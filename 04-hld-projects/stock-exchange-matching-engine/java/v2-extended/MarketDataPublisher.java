package v2_extended;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

/**
 * Bounded per-subscriber queues with drop-and-count protection for slow
 * consumers (FOLLOW-UPS.md #1): when a stuck consumer's queue is full the
 * trade is dropped for that consumer only and counted, so a slow consumer
 * can never block the matching engine.
 */
public class MarketDataPublisher {
    private static class Subscriber {
        final Deque<OrderBook.Trade> queue = new ArrayDeque<>();
        final int maxQueue;
        int dropped = 0;

        Subscriber(int maxQueue) {
            this.maxQueue = maxQueue;
        }
    }

    private final Map<String, Subscriber> subscribers = new HashMap<>();

    public synchronized void subscribe(String name, int maxQueue) {
        subscribers.put(name, new Subscriber(maxQueue));
    }

    public synchronized void publishTrade(OrderBook.Trade trade) {
        for (Subscriber subscriber : subscribers.values()) {
            if (subscriber.queue.size() >= subscriber.maxQueue) {
                // Non-blocking: drop for this consumer only, keep count.
                subscriber.dropped++;
            } else {
                subscriber.queue.addLast(trade);
            }
        }
    }

    public synchronized OrderBook.Trade poll(String name) {
        Subscriber subscriber = subscribers.get(name);
        if (subscriber == null) {
            return null;
        }
        return subscriber.queue.pollFirst();
    }

    public synchronized int dropped(String name) {
        Subscriber subscriber = subscribers.get(name);
        return subscriber != null ? subscriber.dropped : 0;
    }

    public synchronized int pending(String name) {
        Subscriber subscriber = subscribers.get(name);
        return subscriber != null ? subscriber.queue.size() : 0;
    }
}
