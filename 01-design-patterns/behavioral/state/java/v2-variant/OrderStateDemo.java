/**
 * State Pattern - V2: Order Lifecycle
 *
 * Real-world scenario: each order status owns the transitions that are legal
 * from that point in the lifecycle.
 */

import java.util.ArrayList;
import java.util.List;

interface OrderState {
    String getStatus();
    default void pay(Order order, String method) {
        throw new IllegalStateException("Cannot pay while order is " + order.getStatus());
    }
    default void ship(Order order, String trackingNumber) {
        throw new IllegalStateException("Cannot ship while order is " + order.getStatus());
    }
    default void deliver(Order order) {
        throw new IllegalStateException("Cannot deliver while order is " + order.getStatus());
    }
    default void cancel(Order order, String reason) {
        throw new IllegalStateException("Cannot cancel while order is " + order.getStatus());
    }
}

class PendingOrderState implements OrderState {
    @Override public String getStatus() { return "PENDING"; }
    @Override public void pay(Order order, String method) {
        order.setPaymentMethod(method);
        order.setState(new PaidOrderState());
    }
    @Override public void cancel(Order order, String reason) {
        order.setCancelReason(reason);
        order.setState(new CancelledOrderState());
    }
}

class PaidOrderState implements OrderState {
    @Override public String getStatus() { return "PAID"; }
    @Override public void ship(Order order, String trackingNumber) {
        order.setTrackingNumber(trackingNumber);
        order.setState(new ShippedOrderState());
    }
    @Override public void cancel(Order order, String reason) {
        order.setCancelReason(reason);
        order.setState(new CancelledOrderState());
    }
}

class ShippedOrderState implements OrderState {
    @Override public String getStatus() { return "SHIPPED"; }
    @Override public void deliver(Order order) {
        order.setState(new DeliveredOrderState());
    }
    @Override public void cancel(Order order, String reason) {
        throw new IllegalStateException("Cannot cancel after shipment has started");
    }
}

class DeliveredOrderState implements OrderState {
    @Override public String getStatus() { return "DELIVERED"; }
}

class CancelledOrderState implements OrderState {
    @Override public String getStatus() { return "CANCELLED"; }
}

class Order {
    private final String orderId;
    private final List<String> history = new ArrayList<>();
    private OrderState state = new PendingOrderState();
    private String paymentMethod;
    private String trackingNumber;
    private String cancelReason;

    public Order(String orderId) {
        this.orderId = orderId;
        history.add("CREATED");
    }

    public String getOrderId() { return orderId; }
    public String getStatus() { return state.getStatus(); }
    public OrderState getState() { return state; }
    public String getPaymentMethod() { return paymentMethod; }
    public String getTrackingNumber() { return trackingNumber; }
    public String getCancelReason() { return cancelReason; }
    public List<String> getHistory() { return new ArrayList<>(history); }

    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }
    public void setTrackingNumber(String trackingNumber) { this.trackingNumber = trackingNumber; }
    public void setCancelReason(String cancelReason) { this.cancelReason = cancelReason; }

    public void setState(OrderState state) {
        this.state = state;
        history.add(state.getStatus());
    }

    public void pay(String method) { state.pay(this, method); }
    public void ship(String trackingNumber) { state.ship(this, trackingNumber); }
    public void deliver() { state.deliver(this); }
    public void cancel(String reason) { state.cancel(this, reason); }
}

public class OrderStateDemo {
    public static void main(String[] args) {
        Order order = new Order("order-1001");
        order.pay("card");
        order.ship("TRK-1");
        order.deliver();

        System.out.println(order.getOrderId() + ": " + order.getStatus());
        System.out.println(order.getHistory());
    }
}
