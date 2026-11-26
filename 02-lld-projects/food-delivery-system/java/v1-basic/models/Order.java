package v1_basic.models;

public class Order {
    private String id;
    private Customer customer;
    private Courier courier;
    private String state;
    private double restaurantLatitude;
    private double restaurantLongitude;

    public Order(String id, Customer customer, double restaurantLatitude, double restaurantLongitude) {
        this.id = id;
        this.customer = customer;
        this.state = "PLACED";
        this.restaurantLatitude = restaurantLatitude;
        this.restaurantLongitude = restaurantLongitude;
    }

    public String getId() {
        return id;
    }

    public Customer getCustomer() {
        return customer;
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

    public void setState(String state) {
        this.state = state;
    }

    public double getRestaurantLatitude() {
        return restaurantLatitude;
    }

    public double getRestaurantLongitude() {
        return restaurantLongitude;
    }
}
