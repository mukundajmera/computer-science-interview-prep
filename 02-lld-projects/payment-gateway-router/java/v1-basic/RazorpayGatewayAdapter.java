import java.util.UUID;

public class RazorpayGatewayAdapter extends AbstractPaymentGateway {
    public RazorpayGatewayAdapter() {
        super("Razorpay");
    }

    @Override
    public PaymentResponse processPayment(PaymentRequest request) {
        if (!circuitBreaker.allowRequest()) {
            return new PaymentResponse(null, PaymentResponse.Status.FAILED, "Circuit breaker open", getName());
        }

        boolean success = simulateNetworkCall();
        
        if (success) {
            recordMetrics(true);
            return new PaymentResponse(UUID.randomUUID().toString(), PaymentResponse.Status.SUCCESS, "Payment processed by Razorpay", getName());
        } else {
            recordMetrics(false);
            return new PaymentResponse(null, PaymentResponse.Status.TIMEOUT, "Razorpay timeout", getName());
        }
    }
    
    protected boolean simulateNetworkCall() {
        return true;
    }
}
