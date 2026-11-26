import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class SimpleGatewayTest {

    @Test
    void testUnauthenticatedRequestRejected() {
        SimpleGateway gateway = new SimpleGateway();
        gateway.addRoute("/users", "http://user-service:8080", true, 10);

        String response = gateway.handle("/users/1", false);

        assertEquals("401 Unauthorized", response);
    }

    @Test
    void testAuthenticatedRequestAllowedAndRateLimited() {
        SimpleGateway gateway = new SimpleGateway();
        gateway.addRoute("/users", "http://user-service:8080", true, 2);

        // First request
        String response1 = gateway.handle("/users/1", true);
        assertEquals("200 Forward -> http://user-service:8080", response1);

        // Second request
        String response2 = gateway.handle("/users/2", true);
        assertEquals("200 Forward -> http://user-service:8080", response2);

        // Third request - should be rate limited
        String response3 = gateway.handle("/users/3", true);
        assertEquals("429 Too Many Requests", response3);
    }

    @Test
    void testUnknownRouteReturnsNotFound() {
        SimpleGateway gateway = new SimpleGateway();
        gateway.addRoute("/users", "http://user-service:8080", false, 10);

        String response = gateway.handle("/products/1", false);

        assertEquals("404 Not Found", response);
    }
}
