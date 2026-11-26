
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

public class StripeGatewayAdapter extends AbstractPaymentGateway {
    public StripeGatewayAdapter() {
        super("Stripe");
    }

    @Override
    public PaymentResponse processPayment(PaymentRequest request) {
        if (!circuitBreaker.allowRequest()) {
            return new PaymentResponse(null, PaymentResponse.Status.FAILED, "Circuit breaker open", getName());
        }

        long startTime = System.currentTimeMillis();
        boolean success = simulateNetworkCall();
        double latency = System.currentTimeMillis() - startTime;
        
        if (success) {
            recordMetrics(true, latency);
            return new PaymentResponse(UUID.randomUUID().toString(), PaymentResponse.Status.SUCCESS, "Payment processed by Stripe", getName());
        } else {
            recordMetrics(false, latency);
            return new PaymentResponse(null, PaymentResponse.Status.TIMEOUT, "Stripe timeout", getName());
        }
    }

    private boolean simulateNetworkCall() {
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true; // Simple simulation
    }
}
