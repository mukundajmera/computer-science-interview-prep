import java.util.concurrent.atomic.AtomicReference;

public class Order {
    private String id;
    private AtomicReference<OrderState> state;
    private double finalTotal;

    public Order(String id, double finalTotal) {
        this.id = id;
        this.finalTotal = finalTotal;
        this.state = new AtomicReference<>(OrderState.CREATED);
    }
    
    public String getId() { return id; }
    public OrderState getState() { return state.get(); }
    public double getFinalTotal() { return finalTotal; }
    
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
        if (current == OrderState.CREATED && next == OrderState.RESERVATION) return true;
        if (current == OrderState.RESERVATION && next == OrderState.ACCEPTED) return true;
        if (current == OrderState.ACCEPTED && next == OrderState.COURIER_DISPATCH) return true;
        if (current == OrderState.COURIER_DISPATCH && next == OrderState.PAYMENT) return true;
        return false;
    }
}
