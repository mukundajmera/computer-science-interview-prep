import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class SimpleServiceCallTest {

    private SimpleServiceCall client;

    @BeforeEach
    public void setUp() {
        client = new SimpleServiceCall();
    }

    @Test
    public void testSuccessfulServiceCall() {
        client.registerService("auth", req -> "Token for " + req);
        
        String response = client.call("auth", "user123");
        assertEquals("Token for user123", response);
    }

    @Test
    public void testServiceNotFoundThrowsException() {
        RuntimeException thrown = assertThrows(
            RuntimeException.class,
            () -> client.call("unknown-service", "request data")
        );
        assertEquals("Service not found: unknown-service", thrown.getMessage());
    }

    @Test
    public void testMultipleServices() {
        client.registerService("users", req -> "Alice");
        client.registerService("orders", req -> "Order456");
        
        String userResp = client.call("users", "id=1");
        String orderResp = client.call("orders", "id=456");
        
        assertEquals("Alice", userResp);
        assertEquals("Order456", orderResp);
    }
}
