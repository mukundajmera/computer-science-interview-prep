import java.util.UUID;

public class StripeGatewayAdapter extends AbstractPaymentGateway {
    public StripeGatewayAdapter() {
        super("Stripe");
    }

    @Override
    public PaymentResponse processPayment(PaymentRequest request) {
        if (!circuitBreaker.allowRequest()) {
            return new PaymentResponse(null, PaymentResponse.Status.FAILED, "Circuit breaker open", getName());
        }

        // Simulate processing (in a real system this would call Stripe SDK)
        boolean success = simulateNetworkCall();
        
        if (success) {
            recordMetrics(true);
            return new PaymentResponse(UUID.randomUUID().toString(), PaymentResponse.Status.SUCCESS, "Payment processed by Stripe", getName());
        } else {
            recordMetrics(false);
            return new PaymentResponse(null, PaymentResponse.Status.TIMEOUT, "Stripe timeout", getName());
        }
    }
    
    protected boolean simulateNetworkCall() {
        return true; // Overridden in tests for failure injection
    }
}
