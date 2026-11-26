import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;



import java.util.Arrays;
import java.util.List;



public class PaymentGatewayRouterV2Test {
    
    private IdempotencyStore idempotencyStore;
    private DynamicMetricsRoutingStrategy routingStrategy;
    
    @BeforeEach
    public void setup() {
        idempotencyStore = new IdempotencyStore();
        routingStrategy = new DynamicMetricsRoutingStrategy();
    }
    
    static class MyTestGateway extends AbstractPaymentGateway {
        private boolean succeedNext = true;
        private double simulatedLatency;

        public MyTestGateway(String name, double latency) {
            super(name);
            this.simulatedLatency = latency;
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
                recordMetrics(true, simulatedLatency);
                return new PaymentResponse("txn-" + getName(), PaymentResponse.Status.SUCCESS, "Success", getName());
            } else {
                recordMetrics(false, simulatedLatency);
                return new PaymentResponse(null, PaymentResponse.Status.TIMEOUT, "Timeout", getName());
            }
        }
    }

    @Test
    public void testDynamicRoutingBySuccessRate() {
        MyTestGateway g1 = new MyTestGateway("G1", 0.0);
        MyTestGateway g2 = new MyTestGateway("G2", 0.0);
        
        g2.setSucceedNext(false);
        g2.processPayment(new PaymentRequest("dummy", null, 10, "USD", "u"));
        
        GatewayRouter router = new GatewayRouter(Arrays.asList(g1, g2), routingStrategy, idempotencyStore);
        PaymentRequest req = new PaymentRequest("req", "idem-v2-1", 10.0, "USD", "u1");
        
        PaymentResponse res = router.routePayment(req);
        assertEquals("G1", res.getGatewayName());
    }

    @Test
    public void testDynamicRoutingByLatency() {
        MyTestGateway g1 = new MyTestGateway("G1", 50.0);
        MyTestGateway g2 = new MyTestGateway("G2", 20.0);
        
        // Seed
        g1.processPayment(new PaymentRequest("dummy1", null, 10, "USD", "u"));
        g2.processPayment(new PaymentRequest("dummy2", null, 10, "USD", "u"));
        
        GatewayRouter router = new GatewayRouter(Arrays.asList(g1, g2), routingStrategy, idempotencyStore);
        PaymentRequest req = new PaymentRequest("req", "idem-v2-2", 10.0, "USD", "u1");
        
        PaymentResponse res = router.routePayment(req);
        assertEquals("G2", res.getGatewayName());
    }

    @Test
    public void testFallbackOnProviderTimeoutV2() {
        MyTestGateway primary = new MyTestGateway("Primary", 10.0);
        MyTestGateway secondary = new MyTestGateway("Secondary", 10.0);
        
        primary.setSucceedNext(false);
        
        GatewayRouter router = new GatewayRouter(Arrays.asList(primary, secondary), routingStrategy, idempotencyStore);
        PaymentRequest req = new PaymentRequest("req", "idem-v2-3", 10.0, "USD", "u1");
        
        PaymentResponse res = router.routePayment(req);
        assertEquals(PaymentResponse.Status.SUCCESS, res.getStatus());
        assertEquals("Secondary", res.getGatewayName());
    }
}
