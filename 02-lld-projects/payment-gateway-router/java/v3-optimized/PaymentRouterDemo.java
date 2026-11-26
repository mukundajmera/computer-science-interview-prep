
import java.util.Arrays;
import java.util.UUID;

public class PaymentRouterDemo {
    public static void main(String[] args) {
        StripeGatewayAdapter stripe = new StripeGatewayAdapter();
        RazorpayGatewayAdapter razorpay = new RazorpayGatewayAdapter();
        
        RoutingStrategy strategy = new HealthBasedRoutingStrategy();
        IdempotencyStore store = new IdempotencyStore();
        
        GatewayRouter router = new GatewayRouter(Arrays.asList(stripe, razorpay), strategy, store);
        
        PaymentRequest req1 = new PaymentRequest("1", "key123", 100.0, "USD", "user1");
        System.out.println("Sending request 1...");
        PaymentResponse res1 = router.routePayment(req1);
        System.out.println("Result: " + res1.getStatus() + " via " + res1.getGatewayName());
        
        // Duplicate request
        PaymentRequest req2 = new PaymentRequest("2", "key123", 100.0, "USD", "user1");
        System.out.println("Sending duplicate request 2 with same idempotency key...");
        PaymentResponse res2 = router.routePayment(req2);
        System.out.println("Result: " + res2.getStatus() + " via " + res2.getGatewayName());
    }
}
