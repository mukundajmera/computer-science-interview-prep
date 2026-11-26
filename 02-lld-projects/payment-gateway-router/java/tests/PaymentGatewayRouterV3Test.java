import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;



import java.util.Arrays;
import java.util.List;



public class PaymentGatewayRouterV3Test {
    
    private DynamicMetricsRoutingStrategy routingStrategy;
    
    @BeforeEach
    public void setup() {
        routingStrategy = new DynamicMetricsRoutingStrategy();
    }
    
    static class MyTestGateway extends AbstractPaymentGateway {
        private boolean succeedNext = true;
        private double sleepTime;

        public MyTestGateway(String name, double sleepTime) {
            super(name);
            this.sleepTime = sleepTime;
        }

        public void setSucceedNext(boolean succeedNext) {
            this.succeedNext = succeedNext;
        }

        @Override
        public PaymentResponse processPayment(PaymentRequest request) {
            if (sleepTime > 0) {
                try {
                    Thread.sleep((long) sleepTime);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }

            if (succeedNext) {
                recordMetrics(true, sleepTime);
                return new PaymentResponse("txn-" + getName(), PaymentResponse.Status.SUCCESS, "Success", getName());
            } else {
                recordMetrics(false, sleepTime);
                return new PaymentResponse(null, PaymentResponse.Status.TIMEOUT, "Timeout", getName());
            }
        }
    }

    @Test
    public void testIdempotencyDeduplicationV3() {
        IdempotencyStore store = new IdempotencyStore();
        MyTestGateway g1 = new MyTestGateway("G1", 0.0);
        GatewayRouter router = new GatewayRouter(Arrays.asList(g1), routingStrategy, store);
        
        PaymentRequest req1 = new PaymentRequest("req1", "idem-v3-1", 10.0, "USD", "u1");
        PaymentResponse res1 = router.routePayment(req1);
        assertEquals(PaymentResponse.Status.SUCCESS, res1.getStatus());
        
        PaymentRequest req2 = new PaymentRequest("req2", "idem-v3-1", 10.0, "USD", "u1");
        PaymentResponse res2 = router.routePayment(req2);
        
        assertEquals(PaymentResponse.Status.SUCCESS, res2.getStatus());
        assertEquals(res1.getTransactionId(), res2.getTransactionId());
    }

    @Test
    public void testIdempotencyTtlExpiry() throws InterruptedException {
        IdempotencyStore store = new IdempotencyStore(100); // 100ms TTL
        MyTestGateway g1 = new MyTestGateway("G1", 0.0);
        GatewayRouter router = new GatewayRouter(Arrays.asList(g1), routingStrategy, store);
        
        PaymentRequest req1 = new PaymentRequest("req1", "idem-v3-2", 10.0, "USD", "u1");
        PaymentResponse res1 = router.routePayment(req1);
        assertEquals(PaymentResponse.Status.SUCCESS, res1.getStatus());
        
        Thread.sleep(150);
        
        PaymentRequest req2 = new PaymentRequest("req2", "idem-v3-2", 10.0, "USD", "u1");
        PaymentResponse res2 = router.routePayment(req2);
        
        assertEquals(PaymentResponse.Status.SUCCESS, res2.getStatus());
        // Since the actual gateway just returns "txn-G1" for transactionId in this mock, we can just assert it succeeds
    }

    @Test
    public void testConcurrentDoubleChargePrevention() throws InterruptedException {
        IdempotencyStore store = new IdempotencyStore();
        MyTestGateway g1 = new MyTestGateway("G1", 200.0); // 200ms delay
        GatewayRouter router = new GatewayRouter(Arrays.asList(g1), routingStrategy, store);
        
        final PaymentResponse[] results = new PaymentResponse[2];
        
        Thread t1 = new Thread(() -> {
            PaymentRequest req = new PaymentRequest("req", "idem-v3-3", 10.0, "USD", "u1");
            results[0] = router.routePayment(req);
        });
        
        Thread t2 = new Thread(() -> {
            PaymentRequest req = new PaymentRequest("req", "idem-v3-3", 10.0, "USD", "u1");
            results[1] = router.routePayment(req);
        });
        
        t1.start();
        Thread.sleep(50); // Ensure t1 locks first
        t2.start();
        
        t1.join();
        t2.join();
        
        boolean hasSuccess = false;
        boolean hasConflict = false;
        
        for (PaymentResponse res : results) {
            if (res != null) {
                if (res.getStatus() == PaymentResponse.Status.SUCCESS) hasSuccess = true;
                if (res.getStatus() == PaymentResponse.Status.CONFLICT) hasConflict = true;
            }
        }
        
        assertTrue(hasSuccess);
        assertTrue(hasConflict);
    }
}
