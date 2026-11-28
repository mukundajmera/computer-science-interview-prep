package v2_extended;

import java.util.*;

/**
 * v2 order book. Matching logic is byte-for-byte v1 behavior (price-time
 * priority, fixed-point integer prices per PITFALLS.md #4); the only
 * change is that MatchResult carries a status and reject reason so the
 * engine can report validation failures without touching the book.
 */
public class OrderBook {
    private final TreeMap<Long, OrderQueue> bids = new TreeMap<>(Collections.reverseOrder());
    private final TreeMap<Long, OrderQueue> asks = new TreeMap<>();
    private final Map<String, Order> orderMap = new HashMap<>();

    public static class MatchResult {
        public final List<Trade> trades = new ArrayList<>();
        public Order residualOrder = null;
        // "filled" | "resting" | "rejected"; set by the engine/book.
        public String status = "resting";
        public String rejectReason = null;
    }

    public static class Trade {
        public final String makerOrderId;
        public final String takerOrderId;
        public final long price;
        public final long quantity;

        public Trade(String makerOrderId, String takerOrderId, long price, long quantity) {
            this.makerOrderId = makerOrderId;
            this.takerOrderId = takerOrderId;
            this.price = price;
            this.quantity = quantity;
        }
    }

    private static class OrderQueue {
        Order head = null;
        Order tail = null;
        long totalQuantity = 0;

        void add(Order order) {
            if (tail == null) {
                head = order;
                tail = order;
            } else {
                tail.next = order;
                order.prev = tail;
                tail = order;
            }
            totalQuantity += order.quantity;
        }

        void remove(Order order) {
            if (order.prev != null) {
                order.prev.next = order.next;
            } else {
                head = order.next;
            }
            if (order.next != null) {
                order.next.prev = order.prev;
            } else {
                tail = order.prev;
            }
            order.prev = null;
            order.next = null;
            totalQuantity -= order.quantity;
        }

        boolean isEmpty() {
            return head == null;
        }
    }

    public MatchResult processOrder(Order order) {
        MatchResult result = new MatchResult();
        long remainingQuantity = order.quantity;

        if (order.isBuy) {
            while (remainingQuantity > 0 && !asks.isEmpty()) {
                Map.Entry<Long, OrderQueue> bestAskEntry = asks.firstEntry();
                long bestAskPrice = bestAskEntry.getKey();
                if (order.price < bestAskPrice) {
                    break;
                }

                OrderQueue queue = bestAskEntry.getValue();
                while (remainingQuantity > 0 && !queue.isEmpty()) {
                    Order makerOrder = queue.head;
                    long tradeQuantity = Math.min(remainingQuantity, makerOrder.quantity);
                    result.trades.add(new Trade(makerOrder.orderId, order.orderId, makerOrder.price, tradeQuantity));

                    remainingQuantity -= tradeQuantity;
                    makerOrder.quantity -= tradeQuantity;
                    queue.totalQuantity -= tradeQuantity;

                    if (makerOrder.quantity == 0) {
                        queue.remove(makerOrder);
                        orderMap.remove(makerOrder.orderId);
                    }
                }

                if (queue.isEmpty()) {
                    asks.remove(bestAskPrice);
                }
            }
        } else {
            while (remainingQuantity > 0 && !bids.isEmpty()) {
                Map.Entry<Long, OrderQueue> bestBidEntry = bids.firstEntry();
                long bestBidPrice = bestBidEntry.getKey();
                if (order.price > bestBidPrice) {
                    break;
                }

                OrderQueue queue = bestBidEntry.getValue();
                while (remainingQuantity > 0 && !queue.isEmpty()) {
                    Order makerOrder = queue.head;
                    long tradeQuantity = Math.min(remainingQuantity, makerOrder.quantity);
                    result.trades.add(new Trade(makerOrder.orderId, order.orderId, makerOrder.price, tradeQuantity));

                    remainingQuantity -= tradeQuantity;
                    makerOrder.quantity -= tradeQuantity;
                    queue.totalQuantity -= tradeQuantity;

                    if (makerOrder.quantity == 0) {
                        queue.remove(makerOrder);
                        orderMap.remove(makerOrder.orderId);
                    }
                }

                if (queue.isEmpty()) {
                    bids.remove(bestBidPrice);
                }
            }
        }

        if (remainingQuantity > 0) {
            order.quantity = remainingQuantity;
            orderMap.put(order.orderId, order);
            if (order.isBuy) {
                bids.computeIfAbsent(order.price, k -> new OrderQueue()).add(order);
            } else {
                asks.computeIfAbsent(order.price, k -> new OrderQueue()).add(order);
            }
            result.residualOrder = order;
            result.status = "resting";
        } else {
            result.status = "filled";
        }

        return result;
    }

    public boolean cancelOrder(String orderId) {
        Order order = orderMap.remove(orderId);
        if (order == null) {
            return false;
        }

        if (order.isBuy) {
            OrderQueue queue = bids.get(order.price);
            if (queue != null) {
                queue.remove(order);
                if (queue.isEmpty()) {
                    bids.remove(order.price);
                }
            }
        } else {
            OrderQueue queue = asks.get(order.price);
            if (queue != null) {
                queue.remove(order);
                if (queue.isEmpty()) {
                    asks.remove(order.price);
                }
            }
        }
        return true;
    }

    public Map<Long, Long> getBidsDepth() {
        Map<Long, Long> depth = new LinkedHashMap<>();
        for (Map.Entry<Long, OrderQueue> entry : bids.entrySet()) {
            depth.put(entry.getKey(), entry.getValue().totalQuantity);
        }
        return depth;
    }

    public Map<Long, Long> getAsksDepth() {
        Map<Long, Long> depth = new LinkedHashMap<>();
        for (Map.Entry<Long, OrderQueue> entry : asks.entrySet()) {
            depth.put(entry.getKey(), entry.getValue().totalQuantity);
        }
        return depth;
    }
}
