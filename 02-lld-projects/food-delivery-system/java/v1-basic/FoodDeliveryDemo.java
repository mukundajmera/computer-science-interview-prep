import v1_basic.models.Courier;
import v1_basic.models.Customer;
import v1_basic.models.Order;
import v1_basic.service.FoodDeliveryService;

public class FoodDeliveryDemo {
    public static void main(String[] args) {
        System.out.println("Starting Food Delivery Demo...");

        FoodDeliveryService service = new FoodDeliveryService();

        // Initialize Couriers
        Courier courier1 = new Courier("C1", "Alice", 40.7128, -74.0060);
        Courier courier2 = new Courier("C2", "Bob", 40.7306, -73.9352);
        service.addCourier(courier1);
        service.addCourier(courier2);

        // Initialize Customer and Order
        Customer customer = new Customer("U1", "Charlie", 40.7120, -74.0050);
        Order order = new Order("O1", customer, 40.7130, -74.0070);

        // Place Order
        service.placeOrder(order);
        System.out.println("Order " + order.getId() + " placed. State: " + order.getState());

        // Assign Courier
        boolean assigned = service.assignCourier(order);
        if (assigned) {
            System.out.println("Courier " + order.getCourier().getName() + " assigned to order " + order.getId() + ".");
            System.out.println("Order State: " + order.getState());
        } else {
            System.out.println("No couriers available.");
        }

        // Calculate Fee
        double fee = service.calculateOrderFee(order);
        System.out.println("Delivery Fee: $" + String.format("%.2f", fee));
        
        System.out.println("Demo completed.");
    }
}
