import java.util.Arrays;
import java.util.Map;
import java.util.concurrent.TimeoutException;

class MockFailingBackend extends BackendService {
    private final int failCount;
    private int calls = 0;

    public MockFailingBackend(String name, int failCount) {
        super(name);
        this.failCount = failCount;
    }

    @Override
    public String call(long timeoutMs) throws TimeoutException {
        calls++;
        if (calls <= failCount) {
            throw new TimeoutException("Simulated timeout");
        }
        return name + " success";
    }
    
    public int getCalls() {
        return calls;
    }
}

class MockSuccessBackend extends BackendService {
    public MockSuccessBackend(String name) {
        super(name);
    }

    @Override
    public String call(long timeoutMs) {
        return name + " success";
    }
}

public class GatewayV3Test {
    public static void main(String[] args) {
        testSuccessfulRequest();
        testRetrySuccess();
        testRetryBudgetExhausted();
        testCircuitBreakerOpens();
        testAggregation();
        System.out.println("GatewayV3Test passed.");
    }

    private static void testSuccessfulRequest() {
        GatewayV3 gateway = new GatewayV3(0.1);
        MockSuccessBackend backend = new MockSuccessBackend("auth");
        String res = gateway.handle(backend, 1000);
        assert "auth success".equals(res) : "Expected auth success";
    }

    private static void testRetrySuccess() {
        GatewayV3 gateway = new GatewayV3(1.0); // 100% retries
        MockFailingBackend backend = new MockFailingBackend("payment", 1);
        String res = gateway.handle(backend, 1000);
        assert "payment success".equals(res) : "Expected payment success after retry";
        assert backend.getCalls() == 2 : "Expected 2 calls (1 fail, 1 retry)";
    }

    private static void testRetryBudgetExhausted() {
        GatewayV3 gateway = new GatewayV3(0.0); // No retries
        MockFailingBackend backend = new MockFailingBackend("payment", 1);
        String res = gateway.handle(backend, 1000);
        assert "504 Gateway Timeout".equals(res) : "Expected 504";
        assert backend.getCalls() == 1 : "Expected 1 call";
    }

    private static void testCircuitBreakerOpens() {
        GatewayV3 gateway = new GatewayV3(0.0);
        MockFailingBackend backend = new MockFailingBackend("inventory", 5);
        
        assert "504 Gateway Timeout".equals(gateway.handle(backend, 1000));
        assert "504 Gateway Timeout".equals(gateway.handle(backend, 1000));
        assert "504 Gateway Timeout".equals(gateway.handle(backend, 1000)); // 3rd failure opens breaker
        
        assert "503 Service Unavailable (Circuit Breaker OPEN)".equals(gateway.handle(backend, 1000)) : "Expected 503 from open breaker";
        assert backend.getCalls() == 3 : "Expected backend only called 3 times";
    }

    private static void testAggregation() {
        GatewayV3 gateway = new GatewayV3(0.1);
        MockSuccessBackend b1 = new MockSuccessBackend("user");
        MockFailingBackend b2 = new MockFailingBackend("cart", 10);
        
        Map<String, String> res = gateway.aggregate(Arrays.asList(b1, b2), 1000);
        
        assert "user success".equals(res.get("user"));
        assert "504 Gateway Timeout".equals(res.get("cart"));
    }
}
