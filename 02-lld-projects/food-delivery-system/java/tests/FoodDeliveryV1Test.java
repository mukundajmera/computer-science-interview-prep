package tests;

import v1_basic.models.Courier;
import v1_basic.models.Customer;
import v1_basic.models.Order;
import v1_basic.service.FoodDeliveryService;
import v1_basic.strategies.DeliveryFeeStrategy;
import v1_basic.strategies.NearestCourierStrategy;

import java.util.Arrays;
import java.util.List;

public class FoodDeliveryV1Test {
    public static void main(String[] args) {
        testNearestCourierStrategy();
        testDeliveryFeeStrategy();
        testFoodDeliveryServiceAssignment();
        System.out.println("All FoodDeliveryV1 tests passed!");
    }

    private static void testNearestCourierStrategy() {
        NearestCourierStrategy strategy = new NearestCourierStrategy();
        
        Customer customer = new Customer("U1", "Test", 0, 0);
        Order order = new Order("O1", customer, 0, 0);
        
        Courier courier1 = new Courier("C1", "Far", 10, 10);
        Courier courier2 = new Courier("C2", "Near", 1, 1);
        
        List<Courier> couriers = Arrays.asList(courier1, courier2);
        
        Courier nearest = strategy.findNearestCourier(order, couriers);
        assertCondition(nearest != null && nearest.getId().equals("C2"), "Nearest courier should be C2");
    }

    private static void testDeliveryFeeStrategy() {
        DeliveryFeeStrategy strategy = new DeliveryFeeStrategy();
        
        Customer customer = new Customer("U1", "Test", 0, 3);
        Order order = new Order("O1", customer, 4, 0);
        
        double fee = strategy.calculateFee(order);
        // distance is sqrt((4-0)^2 + (0-3)^2) = 5
        // fee = 5.0 + 5 * 2.0 = 15.0
        assertCondition(Math.abs(fee - 15.0) < 0.001, "Delivery fee should be 15.0");
    }

    private static void testFoodDeliveryServiceAssignment() {
        FoodDeliveryService service = new FoodDeliveryService();
        Courier courier1 = new Courier("C1", "Alice", 1, 1);
        service.addCourier(courier1);

        Customer customer = new Customer("U1", "Charlie", 0, 0);
        Order order = new Order("O1", customer, 0, 0);
        
        service.placeOrder(order);
        assertCondition("PLACED".equals(order.getState()), "Order state should be PLACED");
        
        boolean assigned = service.assignCourier(order);
        assertCondition(assigned, "Courier should be assigned");
        assertCondition("ASSIGNED".equals(order.getState()), "Order state should be ASSIGNED");
        assertCondition(!courier1.isAvailable(), "Assigned courier should be unavailable");
    }

    private static void assertCondition(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError("Test failed: " + message);
        }
    }
}
