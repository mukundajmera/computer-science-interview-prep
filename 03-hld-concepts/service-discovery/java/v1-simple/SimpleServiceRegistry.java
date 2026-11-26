/**
 * V1: Simple Service Registry
 * 
 * Basic in-memory service registry.
 */

import java.util.*;

public class SimpleServiceRegistry {
    
    private final Map<String, List<ServiceInstance>> registry = new HashMap<>();
    
    public void register(String serviceName, String host, int port) {
        registry.computeIfAbsent(serviceName, k -> new ArrayList<>())
                .add(new ServiceInstance(host, port));
        System.out.println("Registered: " + serviceName + " at " + host + ":" + port);
    }
    
    public void deregister(String serviceName, String host, int port) {
        List<ServiceInstance> instances = registry.get(serviceName);
        if (instances != null) {
            instances.removeIf(i -> i.host.equals(host) && i.port == port);
            System.out.println("Deregistered: " + serviceName + " at " + host + ":" + port);
        }
    }
    
    public List<ServiceInstance> discover(String serviceName) {
        return new ArrayList<>(registry.getOrDefault(serviceName, Collections.emptyList()));
    }
    
    public ServiceInstance discoverOne(String serviceName) {
        List<ServiceInstance> instances = discover(serviceName);
        if (instances.isEmpty()) {
            throw new RuntimeException("No instances found for: " + serviceName);
        }
        // Simple round-robin
        return instances.get(Math.abs(serviceName.hashCode()) % instances.size());
    }
    
    public void printRegistry() {
        System.out.println("\n=== Service Registry ===");
        for (Map.Entry<String, List<ServiceInstance>> entry : registry.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }
    }
    
    public static class ServiceInstance {
        public final String host;
        public final int port;
        
        ServiceInstance(String host, int port) {
            this.host = host;
            this.port = port;
        }
        
        @Override
        public String toString() {
            return host + ":" + port;
        }
    }
    
    public static void main(String[] args) {
        SimpleServiceRegistry registry = new SimpleServiceRegistry();
        
        registry.register("user-service", "10.0.0.1", 8080);
        registry.register("user-service", "10.0.0.2", 8080);
        registry.register("order-service", "10.0.0.3", 8081);
        
        registry.printRegistry();
        
        System.out.println("\nDiscovering user-service:");
        System.out.println(registry.discover("user-service"));
        
        System.out.println("\nDiscovering one instance:");
        System.out.println(registry.discoverOne("user-service"));
    }
}
