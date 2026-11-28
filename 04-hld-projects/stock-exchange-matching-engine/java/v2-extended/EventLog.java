package v2_extended;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Sequenced, append-only record of every inbound place/cancel with its
 * outcome: the reconciliation and hot-standby foundation from
 * FOLLOW-UPS.md #2. One flat Event shape covers both ops; place-specific
 * fields are zero/null on cancels.
 */
public class EventLog {
    public static class Event {
        public final long sequence;
        public final String op; // "place" | "cancel"
        public final String orderId;
        public final String symbol;
        public final boolean isBuy;
        public final long price;
        public final long quantity;
        // For "place": the order passed validation. For "cancel": the
        // cancel found a resting order. Either way, false means the book
        // was never touched and replay skips the event.
        public final boolean accepted;
        public final String reason;

        private Event(long sequence, String op, String orderId, String symbol,
                      boolean isBuy, long price, long quantity, boolean accepted, String reason) {
            this.sequence = sequence;
            this.op = op;
            this.orderId = orderId;
            this.symbol = symbol;
            this.isBuy = isBuy;
            this.price = price;
            this.quantity = quantity;
            this.accepted = accepted;
            this.reason = reason;
        }

        public static Event place(long sequence, String orderId, String symbol, boolean isBuy,
                                  long price, long quantity, boolean accepted, String reason) {
            return new Event(sequence, "place", orderId, symbol, isBuy, price, quantity, accepted, reason);
        }

        public static Event cancel(long sequence, String symbol, String orderId,
                                   boolean success, String reason) {
            return new Event(sequence, "cancel", orderId, symbol, false, 0, 0, success, reason);
        }
    }

    private final CopyOnWriteArrayList<Event> events = new CopyOnWriteArrayList<>();

    public void append(Event event) {
        events.add(event);
    }

    public List<Event> events() {
        return new ArrayList<>(events);
    }
}
