package v2_extended;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

/**
 * v2-extended matching engine. Matching behavior is identical to v1; the
 * step-ups are the ones the project's own docs call for:
 *
 * 1. Sequenced event log + deterministic replay (FOLLOW-UPS.md #2 and the
 *    standby interviewer probe): every inbound place/cancel is stamped by
 *    the sequencer and appended to an event log with its outcome.
 *    replay() applies the accepted events to a fresh engine in sequence
 *    order, reproducing the exact book state.
 * 2. Order validation (input-validation weakness; PITFALLS.md #3's O(1)
 *    cancel map only works when ids are unique): non-positive
 *    price/quantity, missing order ids and duplicate order ids are
 *    rejected before they reach the book, with the reason on the result
 *    and in the log. Rejected orders never mutate book state.
 * 3. Market-data publisher with slow-consumer protection
 *    (FOLLOW-UPS.md #1): see MarketDataPublisher.
 */
public class MatchingEngine {
    private final ConcurrentHashMap<String, OrderBook> orderBooks = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, ReentrantLock> symbolLocks = new ConcurrentHashMap<>();
    private final Sequencer sequencer;
    private final EventLog eventLog = new EventLog();
    private final Set<String> seenOrderIds = ConcurrentHashMap.newKeySet();
    private MarketDataPublisher publisher;

    public MatchingEngine() {
        this(0);
    }

    private MatchingEngine(long sequencerSeed) {
        this.sequencer = new Sequencer(sequencerSeed);
    }

    public void setMarketDataPublisher(MarketDataPublisher publisher) {
        this.publisher = publisher;
    }

    public EventLog getEventLog() {
        return eventLog;
    }

    private ReentrantLock getLock(String symbol) {
        return symbolLocks.computeIfAbsent(symbol, k -> new ReentrantLock());
    }

    private OrderBook getOrderBook(String symbol) {
        return orderBooks.computeIfAbsent(symbol, k -> new OrderBook());
    }

    private String validate(String orderId, long price, long quantity) {
        if (orderId == null || orderId.trim().isEmpty()) {
            return "missing order id";
        }
        if (price <= 0) {
            return "non-positive price";
        }
        if (quantity <= 0) {
            return "non-positive quantity";
        }
        if (seenOrderIds.contains(orderId)) {
            return "duplicate order id";
        }
        return null;
    }

    public OrderBook.MatchResult placeOrder(String orderId, String symbol, boolean isBuy, long price, long quantity) {
        // The sequencer stamps every inbound message, accepted or not, so
        // the log and any standby see one gapless stream.
        long sequence = sequencer.next();

        String reason = validate(orderId, price, quantity);
        if (reason != null) {
            OrderBook.MatchResult rejected = new OrderBook.MatchResult();
            rejected.status = "rejected";
            rejected.rejectReason = reason;
            eventLog.append(EventLog.Event.place(sequence, orderId, symbol, isBuy, price, quantity, false, reason));
            return rejected;
        }

        Order order = new Order(orderId, symbol, isBuy, price, quantity, sequence);
        OrderBook.MatchResult result;
        ReentrantLock lock = getLock(symbol);
        lock.lock();
        try {
            OrderBook book = getOrderBook(symbol);
            result = book.processOrder(order);
            seenOrderIds.add(orderId);
            eventLog.append(EventLog.Event.place(sequence, orderId, symbol, isBuy, price, quantity, true, null));
        } finally {
            lock.unlock();
        }

        if (publisher != null) {
            for (OrderBook.Trade trade : result.trades) {
                publisher.publishTrade(trade);
            }
        }
        return result;
    }

    public boolean cancelOrder(String symbol, String orderId) {
        long sequence = sequencer.next();
        boolean success;
        ReentrantLock lock = getLock(symbol);
        lock.lock();
        try {
            OrderBook book = orderBooks.get(symbol);
            success = book != null && book.cancelOrder(orderId);
        } finally {
            lock.unlock();
        }
        eventLog.append(EventLog.Event.cancel(sequence, symbol, orderId, success,
                success ? null : "unknown order"));
        return success;
    }

    public Map<Long, Long> getBidsDepth(String symbol) {
        ReentrantLock lock = getLock(symbol);
        lock.lock();
        try {
            OrderBook book = orderBooks.get(symbol);
            if (book != null) {
                return book.getBidsDepth();
            }
            return Collections.emptyMap();
        } finally {
            lock.unlock();
        }
    }

    public Map<Long, Long> getAsksDepth(String symbol) {
        ReentrantLock lock = getLock(symbol);
        lock.lock();
        try {
            OrderBook book = orderBooks.get(symbol);
            if (book != null) {
                return book.getAsksDepth();
            }
            return Collections.emptyMap();
        } finally {
            lock.unlock();
        }
    }

    /**
     * Rebuild an engine from a sequenced log (FOLLOW-UPS.md #2). Accepted
     * places and successful cancels are applied in sequence order;
     * rejected places and failed cancels never touched the book, so they
     * are skipped. The new engine's sequencer continues past the log's
     * maximum so fresh orders never reuse a sequence number.
     */
    public static MatchingEngine replay(List<EventLog.Event> events) {
        List<EventLog.Event> ordered = new ArrayList<>(events);
        ordered.sort(Comparator.comparingLong(e -> e.sequence));
        long seed = 0;
        for (EventLog.Event event : ordered) {
            seed = Math.max(seed, event.sequence);
        }
        MatchingEngine engine = new MatchingEngine(seed);
        for (EventLog.Event event : ordered) {
            if ("place".equals(event.op) && event.accepted) {
                engine.placeOrder(event.orderId, event.symbol, event.isBuy, event.price, event.quantity);
            } else if ("cancel".equals(event.op) && event.accepted) {
                engine.cancelOrder(event.symbol, event.orderId);
            }
        }
        return engine;
    }
}
