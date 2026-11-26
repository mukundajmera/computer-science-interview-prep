/**
 * V1: Simple Service Call
 * 
 * Basic HTTP-like service-to-service call simulation.
 */

import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

public class SimpleServiceCall {
    
    private final Map<String, Service> services = new HashMap<>();
    
    public void registerService(String name, Service service) {
        services.put(name, service);
    }
    
    public String call(String serviceName, String request) {
        Service service = services.get(serviceName);
        if (service == null) {
            throw new RuntimeException("Service not found: " + serviceName);
        }
        
        System.out.println("Calling " + serviceName + " with: " + request);
        String response = service.handle(request);
        System.out.println("Response from " + serviceName + ": " + response);
        return response;
    }
    
    public interface Service {
        String handle(String request);
    }
    
    public static void main(String[] args) {
        SimpleServiceCall client = new SimpleServiceCall();
        
        client.registerService("user-service", req -> "User: Alice");
        client.registerService("order-service", req -> "Order: #123");
        
        client.call("user-service", "getUser?id=1");
        client.call("order-service", "getOrder?id=123");
    }
}
