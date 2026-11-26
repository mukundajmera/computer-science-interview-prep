package v1_basic;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class MatchingEngine {
    private final ConcurrentHashMap<String, OrderBook> orderBooks = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, ReentrantLock> symbolLocks = new ConcurrentHashMap<>();
    private final Sequencer sequencer = new Sequencer();

    private ReentrantLock getLock(String symbol) {
        return symbolLocks.computeIfAbsent(symbol, k -> new ReentrantLock());
    }

    private OrderBook getOrderBook(String symbol) {
        return orderBooks.computeIfAbsent(symbol, k -> new OrderBook());
    }

    public OrderBook.MatchResult placeOrder(String orderId, String symbol, boolean isBuy, long price, long quantity) {
        Order order = new Order(orderId, symbol, isBuy, price, quantity, sequencer.next());
        ReentrantLock lock = getLock(symbol);
        lock.lock();
        try {
            OrderBook book = getOrderBook(symbol);
            return book.processOrder(order);
        } finally {
            lock.unlock();
        }
    }

    public boolean cancelOrder(String symbol, String orderId) {
        ReentrantLock lock = getLock(symbol);
        lock.lock();
        try {
            OrderBook book = orderBooks.get(symbol);
            if (book != null) {
                return book.cancelOrder(orderId);
            }
            return false;
        } finally {
            lock.unlock();
        }
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
}
