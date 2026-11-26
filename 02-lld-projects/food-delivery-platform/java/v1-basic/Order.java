import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

public class Order {
    private String id;
    private AtomicReference<OrderState> state;
    private List<MenuItem> items;
    private double total;
    private double finalTotal;

    public Order(String id, List<MenuItem> items, double total) {
        this.id = id;
        this.items = items;
        this.total = total;
        this.state = new AtomicReference<>(OrderState.CREATED);
        this.finalTotal = total;
    }

    public Order(String id, double total) {
        this.id = id;
        this.items = null;
        this.total = total;
        this.state = new AtomicReference<>(OrderState.CREATED);
        this.finalTotal = total;
    }

    public String getId() { return id; }
    public OrderState getState() { return state.get(); }
    public List<MenuItem> getItems() { return items; }
    public double getTotal() { return total; }
    public double getFinalTotal() { return finalTotal; }

    public void setState(OrderState newState) {
        this.state.set(newState);
    }
    
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
