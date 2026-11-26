/**
 * V2: Service Registry with Health Checks
 * 
 * Registry with heartbeat-based health monitoring.
 */

import java.util.*;
import java.util.concurrent.*;

public class HealthCheckRegistry {
    
    private final Map<String, Map<String, ServiceInstance>> registry = new ConcurrentHashMap<>();
    private final long healthCheckIntervalMs;
    private final long instanceTimeoutMs;
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
    
    public HealthCheckRegistry(long healthCheckIntervalMs, long instanceTimeoutMs) {
        this.healthCheckIntervalMs = healthCheckIntervalMs;
        this.instanceTimeoutMs = instanceTimeoutMs;
    }
    
    public void start() {
        scheduler.scheduleAtFixedRate(
            this::checkHealth, 
            healthCheckIntervalMs, 
            healthCheckIntervalMs, 
            TimeUnit.MILLISECONDS
        );
    }
    
    public void stop() {
        scheduler.shutdown();
    }
    
    public void register(String serviceName, String instanceId, String host, int port) {
        ServiceInstance instance = new ServiceInstance(instanceId, host, port);
        registry.computeIfAbsent(serviceName, k -> new ConcurrentHashMap<>())
                .put(instanceId, instance);
        System.out.println("Registered: " + serviceName + "/" + instanceId);
    }
    
    public void heartbeat(String serviceName, String instanceId) {
        Map<String, ServiceInstance> instances = registry.get(serviceName);
        if (instances != null) {
            ServiceInstance instance = instances.get(instanceId);
            if (instance != null) {
                instance.lastHeartbeat = System.currentTimeMillis();
                instance.healthy = true;
            }
        }
    }
    
    public void deregister(String serviceName, String instanceId) {
        Map<String, ServiceInstance> instances = registry.get(serviceName);
        if (instances != null) {
            instances.remove(instanceId);
            System.out.println("Deregistered: " + serviceName + "/" + instanceId);
        }
    }
    
    public List<ServiceInstance> discoverHealthy(String serviceName) {
        Map<String, ServiceInstance> instances = registry.get(serviceName);
        if (instances == null) return Collections.emptyList();
        
        List<ServiceInstance> healthy = new ArrayList<>();
        for (ServiceInstance instance : instances.values()) {
            if (instance.healthy) {
                healthy.add(instance);
            }
        }
        return healthy;
    }
    
    private void checkHealth() {
        long now = System.currentTimeMillis();
        for (Map.Entry<String, Map<String, ServiceInstance>> serviceEntry : registry.entrySet()) {
            for (Map.Entry<String, ServiceInstance> instanceEntry : serviceEntry.getValue().entrySet()) {
                ServiceInstance instance = instanceEntry.getValue();
                if (now - instance.lastHeartbeat > instanceTimeoutMs) {
                    instance.healthy = false;
                    System.out.println("UNHEALTHY: " + serviceEntry.getKey() + "/" + instance.id);
                }
            }
        }
    }
    
    public void printRegistry() {
        System.out.println("\n=== Registry with Health ===");
        for (Map.Entry<String, Map<String, ServiceInstance>> entry : registry.entrySet()) {
            System.out.println(entry.getKey() + ":");
            for (ServiceInstance instance : entry.getValue().values()) {
                System.out.printf("  %s (%s:%d) - %s%n", 
                    instance.id, instance.host, instance.port,
                    instance.healthy ? "HEALTHY" : "UNHEALTHY");
            }
        }
    }
    
    public static class ServiceInstance {
        public final String id;
        public final String host;
        public final int port;
        public volatile boolean healthy = true;
        public volatile long lastHeartbeat = System.currentTimeMillis();
        
        ServiceInstance(String id, String host, int port) {
            this.id = id;
            this.host = host;
            this.port = port;
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        HealthCheckRegistry registry = new HealthCheckRegistry(1000, 3000);
        registry.start();
        
        registry.register("user-service", "user-1", "10.0.0.1", 8080);
        registry.register("user-service", "user-2", "10.0.0.2", 8080);
        
        // Simulate heartbeats
        for (int i = 0; i < 5; i++) {
            Thread.sleep(1000);
            registry.heartbeat("user-service", "user-1");
            // user-2 stops sending heartbeats
        }
        
        registry.printRegistry();
        
        System.out.println("\nHealthy instances:");
        System.out.println(registry.discoverHealthy("user-service"));
        
        registry.stop();
    }
}
