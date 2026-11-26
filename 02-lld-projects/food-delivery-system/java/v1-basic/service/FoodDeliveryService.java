package v1_basic.service;

import v1_basic.models.Courier;
import v1_basic.models.Order;
import v1_basic.strategies.DeliveryFeeStrategy;
import v1_basic.strategies.NearestCourierStrategy;

import java.util.ArrayList;
import java.util.List;

public class FoodDeliveryService {
    private List<Courier> couriers;
    private List<Order> orders;
    private DeliveryFeeStrategy feeStrategy;
    private NearestCourierStrategy nearestCourierStrategy;

    public FoodDeliveryService() {
        this.couriers = new ArrayList<>();
        this.orders = new ArrayList<>();
        this.feeStrategy = new DeliveryFeeStrategy();
        this.nearestCourierStrategy = new NearestCourierStrategy();
    }

    public void addCourier(Courier courier) {
        couriers.add(courier);
    }

    public void placeOrder(Order order) {
        orders.add(order);
        order.setState("PLACED");
    }

    public boolean assignCourier(Order order) {
        Courier nearest = nearestCourierStrategy.findNearestCourier(order, couriers);
        if (nearest != null) {
            order.setCourier(nearest);
            nearest.setAvailable(false);
            order.setState("ASSIGNED");
            return true;
        }
        return false;
    }

    public double calculateOrderFee(Order order) {
        return feeStrategy.calculateFee(order);
    }
}
