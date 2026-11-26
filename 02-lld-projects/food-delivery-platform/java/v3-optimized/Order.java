
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

public class Order {
    private String id;
    private AtomicReference<OrderState> state;
    private double baseTotal;
    private double finalTotal;

    public Order(String id, double baseTotal) {
        this.id = id;
        this.baseTotal = baseTotal;
        this.finalTotal = baseTotal;
        this.state = new AtomicReference<>(OrderState.CREATED);
    }
    
    public String getId() { return id; }
    public OrderState getState() { return state.get(); }
    public double getBaseTotal() { return baseTotal; }
    public double getFinalTotal() { return finalTotal; }
    public void setFinalTotal(double finalTotal) { this.finalTotal = finalTotal; }

    public void transitionState(OrderState expectedCurrent, OrderState nextState) {
        if (!isValidTransition(expectedCurrent, nextState)) {
            throw new IllegalStateException("Invalid state transition");
        }
        boolean success = state.compareAndSet(expectedCurrent, nextState);
        if (!success) {
            throw new IllegalStateException("Concurrent modification or invalid state");
        }
    }
    
    private boolean isValidTransition(OrderState current, OrderState next) {
        if (current == OrderState.CREATED && next == OrderState.ACCEPTED) return true;
        if (current == OrderState.ACCEPTED && next == OrderState.PREPARING) return true;
        if (current == OrderState.PREPARING && next == OrderState.OUT_FOR_DELIVERY) return true;
        if (current == OrderState.OUT_FOR_DELIVERY && next == OrderState.DELIVERED) return true;
        return false;
    }
}
