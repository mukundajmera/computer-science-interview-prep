package v1_basic;

import java.util.Map;
import java.util.HashMap;

public class ApiGatewaySimulator {
    private CircuitBreaker circuitBreaker = new CircuitBreaker();
    
    public Response handleRequest(Request request) {
        // 1. Security/Auth Filter
        if (request.headers == null || !request.headers.containsKey("Authorization")) {
            return new Response(401, "Unauthorized");
        }
        
        // 2. Circuit Breaker Filter
        if (!circuitBreaker.allowRequest()) {
            return new Response(503, "Service Unavailable");
        }
        
        // 3. Routing/Proxy (Simulation)
        // If we made it here in normal trace, simulate success
        circuitBreaker.recordSuccess();
        return new Response(200, "OK from downstream");
    }
    
    public CircuitBreaker getCircuitBreaker() {
        return circuitBreaker;
    }
}
