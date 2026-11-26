import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;

public class PaymentGatewayRouterTest {
    
    private IdempotencyStore idempotencyStore;
    private HealthBasedRoutingStrategy routingStrategy;
    
    @BeforeEach
    public void setup() {
        idempotencyStore = new IdempotencyStore();
        routingStrategy = new HealthBasedRoutingStrategy();
    }
    
    // Helper to create reliable test gateways
    static class TestGateway extends AbstractPaymentGateway {
        private boolean succeedNext = true;

        public TestGateway(String name) {
            super(name);
        }

        public void setSucceedNext(boolean succeedNext) {
            this.succeedNext = succeedNext;
        }

        @Override
        public PaymentResponse processPayment(PaymentRequest request) {
            if (!circuitBreaker.allowRequest()) {
                return new PaymentResponse(null, PaymentResponse.Status.FAILED, "Circuit breaker open", getName());
            }

            if (succeedNext) {
                recordMetrics(true);
                return new PaymentResponse("txn-" + getName(), PaymentResponse.Status.SUCCESS, "Success", getName());
            } else {
                recordMetrics(false);
                return new PaymentResponse(null, PaymentResponse.Status.TIMEOUT, "Timeout", getName());
            }
        }
    }
    
    @Test
    public void testIdempotencyDeduplication() {
        TestGateway g1 = new TestGateway("G1");
        GatewayRouter router = new GatewayRouter(Arrays.asList(g1), routingStrategy, idempotencyStore);
        
        PaymentRequest req1 = new PaymentRequest("req1", "idem-1", 10.0, "USD", "u1");
        PaymentResponse res1 = router.routePayment(req1);
        assertEquals(PaymentResponse.Status.SUCCESS, res1.getStatus());
        assertEquals("G1", res1.getGatewayName());
        
        // Second request with same idempotency key
        PaymentRequest req2 = new PaymentRequest("req2", "idem-1", 10.0, "USD", "u1");
        PaymentResponse res2 = router.routePayment(req2);
        
        // Should return exactly the same response object / transaction id
        assertEquals(PaymentResponse.Status.SUCCESS, res2.getStatus());
        assertEquals("G1", res2.getGatewayName());
        assertEquals(res1.getTransactionId(), res2.getTransactionId());
    }
    
    @Test
    public void testHealthBasedRouting() {
        TestGateway healthy = new TestGateway("Healthy");
        TestGateway unhealthy = new TestGateway("Unhealthy");
        
        // Unhealthy gateway fails a request, lowering its success rate
        unhealthy.setSucceedNext(false);
        unhealthy.processPayment(new PaymentRequest("dummy", null, 10, "USD", "u"));
        
        GatewayRouter router = new GatewayRouter(Arrays.asList(unhealthy, healthy), routingStrategy, idempotencyStore);
        PaymentRequest req = new PaymentRequest("req", "idem-2", 10.0, "USD", "u1");
        
        PaymentResponse res = router.routePayment(req);
        
        // Should route to Healthy because its success rate is 1.0 vs Unhealthy's 0.0
        assertEquals("Healthy", res.getGatewayName());
    }
    
    @Test
    public void testFallbackOnProviderTimeout() {
        TestGateway primary = new TestGateway("Primary");
        TestGateway secondary = new TestGateway("Secondary");
        
        // Make primary fail, but secondary succeed
        primary.setSucceedNext(false);
        
        GatewayRouter router = new GatewayRouter(Arrays.asList(primary, secondary), routingStrategy, idempotencyStore);
        PaymentRequest req = new PaymentRequest("req", "idem-3", 10.0, "USD", "u1");
        
        PaymentResponse res = router.routePayment(req);
        
        // Should fallback to secondary and succeed
        assertEquals(PaymentResponse.Status.SUCCESS, res.getStatus());
        assertEquals("Secondary", res.getGatewayName());
    }
    
    @Test
    public void testCircuitBreakerTripAndReset() throws InterruptedException {
        // Set up with 3 failure threshold and 100ms reset
        CircuitBreaker cb = new CircuitBreaker(3, 100);
        
        assertTrue(cb.allowRequest());
        
        cb.recordFailure();
        assertTrue(cb.allowRequest());
        
        cb.recordFailure();
        assertTrue(cb.allowRequest());
        
        cb.recordFailure();
        // Tripped!
        assertFalse(cb.allowRequest());
        
        // Wait for reset timeout
        Thread.sleep(150);
        
        // Should be HALF_OPEN and allow one request
        assertTrue(cb.allowRequest());
        
        // If it succeeds, it closes
        cb.recordSuccess();
        assertTrue(cb.allowRequest());
    }
}
