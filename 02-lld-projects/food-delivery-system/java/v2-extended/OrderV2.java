package v2_extended;

import v1_basic.models.Customer;
import v1_basic.models.Courier;

/**
 * v2 order: replaces v1's free-form String state with a guarded state
 * machine and state-dependent cancellation (FOLLOW-UPS).
 *
 * PLACED            -> cancel: full refund
 * ASSIGNED          -> cancel: refund minus a 20% preparation penalty,
 *                       the courier is freed
 * OUT_FOR_DELIVERY  -> cancel: rejected, route the customer to support
 * DELIVERED/CANCELLED -> cancel: rejected
 */
public class OrderV2 {
    public static final double PREPARATION_PENALTY = 0.2;

    private final String id;
    private final Customer customer;
    private final double restaurantLatitude;
    private final double restaurantLongitude;
    private final double total;
    private Courier courier;
    private String state;

    public OrderV2(String id, Customer customer, double restaurantLatitude,
                   double restaurantLongitude, double total) {
        this.id = id;
        this.customer = customer;
        this.restaurantLatitude = restaurantLatitude;
        this.restaurantLongitude = restaurantLongitude;
        this.total = total;
        this.state = "PLACED";
    }

    public String getId() {
        return id;
    }

    public Customer getCustomer() {
        return customer;
    }

    public double getRestaurantLatitude() {
        return restaurantLatitude;
    }

    public double getRestaurantLongitude() {
        return restaurantLongitude;
    }

    public double getTotal() {
        return total;
    }

    public Courier getCourier() {
        return courier;
    }

    public void setCourier(Courier courier) {
        this.courier = courier;
    }

    public String getState() {
        return state;
    }

    /** Advances through the happy-path lifecycle; terminal states throw. */
    public void advance() {
        switch (state) {
            case "PLACED":
                state = "ASSIGNED";
                break;
            case "ASSIGNED":
                state = "OUT_FOR_DELIVERY";
                break;
            case "OUT_FOR_DELIVERY":
                state = "DELIVERED";
                break;
            default:
                throw new IllegalStateException("Cannot advance from state " + state);
        }
    }

    public CancelResult cancel() {
        switch (state) {
            case "PLACED":
                state = "CANCELLED";
                return new CancelResult(true, total, "Cancelled before preparation; full refund.");
            case "ASSIGNED":
                state = "CANCELLED";
                if (courier != null) {
                    courier.setAvailable(true);
                }
                return new CancelResult(true, total * (1.0 - PREPARATION_PENALTY),
                        "Cancelled during preparation; refund less 20% penalty.");
            case "OUT_FOR_DELIVERY":
                return new CancelResult(false, 0.0, "Order is out for delivery; contact support.");
            case "DELIVERED":
                return new CancelResult(false, 0.0, "Already delivered; use the returns flow.");
            default:
                return new CancelResult(false, 0.0, "Already cancelled.");
        }
    }
}
