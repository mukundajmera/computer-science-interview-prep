package tests;

import v1_basic.ApiGatewaySimulator;
import v1_basic.Request;
import v1_basic.Response;

import java.util.HashMap;
import java.util.Map;

public class ApiGatewaySimulatorTest {

    public static void main(String[] args) {
        testNormalTrace();
        testFailureTrace();
        System.out.println("All Java API Gateway tests passed!");
    }

    private static void testNormalTrace() {
        ApiGatewaySimulator gateway = new ApiGatewaySimulator();
        
        Map<String, String> headers = new HashMap<>();
        headers.put("Authorization", "Bearer valid-token");
        
        Request req = new Request("/api/v1/data", headers);
        Response res = gateway.handleRequest(req);
        
        if (res.statusCode != 200) {
            throw new RuntimeException("Expected 200 OK, got " + res.statusCode);
        }
    }

    private static void testFailureTrace() {
        ApiGatewaySimulator gateway = new ApiGatewaySimulator();
        
        Map<String, String> headers = new HashMap<>();
        headers.put("Authorization", "Bearer valid-token");
        Request req = new Request("/api/v1/data", headers);
        
        // Simulate repeated timeouts by tripping the breaker
        gateway.getCircuitBreaker().tripOpen();
        
        // Next request should fail fast with 503
        Response res = gateway.handleRequest(req);
        
        if (res.statusCode != 503) {
            throw new RuntimeException("Expected 503 Service Unavailable, got " + res.statusCode);
        }
    }
}
