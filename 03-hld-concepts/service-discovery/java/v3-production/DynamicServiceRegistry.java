/**
 * V3: Dynamic Service Registry with TTL
 * 
 * Production-like registry with TTL-based deregistration.
 */

import java.util.*;
import java.util.concurrent.*;

public class DynamicServiceRegistry {
    
    private final ConcurrentMap<String, ConcurrentMap<String, ServiceInstance>> registry = 
        new ConcurrentHashMap<>();
    private final long defaultTtlMs;
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
    private final List<RegistryListener> listeners = new CopyOnWriteArrayList<>();
    
    public DynamicServiceRegistry(long defaultTtlMs) {
        this.defaultTtlMs = defaultTtlMs;
    }
    
    public void start() {
        scheduler.scheduleAtFixedRate(this::cleanup, 1000, 1000, TimeUnit.MILLISECONDS);
    }
    
    public void stop() {
        scheduler.shutdown();
    }
    
    public void addListener(RegistryListener listener) {
        listeners.add(listener);
    }
    
    public String register(String serviceName, String host, int port, Map<String, String> metadata) {
        String instanceId = UUID.randomUUID().toString().substring(0, 8);
        ServiceInstance instance = new ServiceInstance(
            instanceId, serviceName, host, port, metadata, defaultTtlMs);
        
        registry.computeIfAbsent(serviceName, k -> new ConcurrentHashMap<>())
                .put(instanceId, instance);
        
        notifyListeners(EventType.REGISTERED, instance);
        System.out.println("Registered: " + serviceName + "/" + instanceId + " at " + host + ":" + port);
        
        return instanceId;
    }
    
    public void renew(String serviceName, String instanceId) {
        ConcurrentMap<String, ServiceInstance> instances = registry.get(serviceName);
        if (instances != null) {
            ServiceInstance instance = instances.get(instanceId);
            if (instance != null) {
                instance.renew();
            }
        }
    }
    
    public void deregister(String serviceName, String instanceId) {
        ConcurrentMap<String, ServiceInstance> instances = registry.get(serviceName);
        if (instances != null) {
            ServiceInstance instance = instances.remove(instanceId);
            if (instance != null) {
                notifyListeners(EventType.DEREGISTERED, instance);
                System.out.println("Deregistered: " + serviceName + "/" + instanceId);
            }
        }
    }
    
    public List<ServiceInstance> discover(String serviceName) {
        ConcurrentMap<String, ServiceInstance> instances = registry.get(serviceName);
        if (instances == null) return Collections.emptyList();
        
        List<ServiceInstance> result = new ArrayList<>();
        for (ServiceInstance instance : instances.values()) {
            if (instance.isHealthy()) {
                result.add(instance);
            }
        }
        return result;
    }
    
    public ServiceInstance discoverOne(String serviceName, String sessionId) {
        List<ServiceInstance> instances = discover(serviceName);
        if (instances.isEmpty()) return null;
        
        // Consistent selection based on session ID (sticky sessions)
        int index = Math.abs(sessionId.hashCode()) % instances.size();
        return instances.get(index);
    }
    
    private void cleanup() {
        long now = System.currentTimeMillis();
        for (Map.Entry<String, ConcurrentMap<String, ServiceInstance>> serviceEntry : registry.entrySet()) {
            Iterator<Map.Entry<String, ServiceInstance>> iter = 
                serviceEntry.getValue().entrySet().iterator();
            
            while (iter.hasNext()) {
                ServiceInstance instance = iter.next().getValue();
                if (now > instance.expirationTime) {
                    iter.remove();
                    notifyListeners(EventType.EXPIRED, instance);
                    System.out.println("Expired: " + instance.serviceName + "/" + instance.id);
                }
            }
        }
    }
    
    private void notifyListeners(EventType type, ServiceInstance instance) {
        for (RegistryListener listener : listeners) {
            listener.onEvent(type, instance);
        }
    }
    
    public void printRegistry() {
        System.out.println("\n=== Dynamic Service Registry ===");
        for (Map.Entry<String, ConcurrentMap<String, ServiceInstance>> entry : registry.entrySet()) {
            System.out.println(entry.getKey() + ":");
            for (ServiceInstance instance : entry.getValue().values()) {
                long ttlRemaining = (instance.expirationTime - System.currentTimeMillis()) / 1000;
                System.out.printf("  %s (%s:%d) TTL: %ds %s%n",
                    instance.id, instance.host, instance.port, ttlRemaining,
                    instance.metadata.isEmpty() ? "" : instance.metadata);
            }
        }
    }
    
    public enum EventType { REGISTERED, DEREGISTERED, EXPIRED }
    
    public interface RegistryListener {
        void onEvent(EventType type, ServiceInstance instance);
    }
    
    public static class ServiceInstance {
        public final String id;
        public final String serviceName;
        public final String host;
        public final int port;
        public final Map<String, String> metadata;
        public final long ttlMs;
        public volatile long expirationTime;
        
        ServiceInstance(String id, String serviceName, String host, int port,
                       Map<String, String> metadata, long ttlMs) {
            this.id = id;
            this.serviceName = serviceName;
            this.host = host;
            this.port = port;
            this.metadata = new HashMap<>(metadata);
            this.ttlMs = ttlMs;
            this.expirationTime = System.currentTimeMillis() + ttlMs;
        }
        
        public void renew() {
            this.expirationTime = System.currentTimeMillis() + ttlMs;
        }
        
        public boolean isHealthy() {
            return System.currentTimeMillis() < expirationTime;
        }
        
        @Override
        public String toString() {
            return host + ":" + port;
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        DynamicServiceRegistry registry = new DynamicServiceRegistry(5000); // 5s TTL
        registry.addListener((type, instance) -> 
            System.out.println("[EVENT] " + type + ": " + instance.serviceName + "/" + instance.id));
        registry.start();
        
        // Register services
        String id1 = registry.register("api-service", "10.0.0.1", 8080, 
            Map.of("version", "1.0", "region", "us-east"));
        String id2 = registry.register("api-service", "10.0.0.2", 8080,
            Map.of("version", "1.0", "region", "us-west"));
        
        registry.printRegistry();
        
        // Simulate renewals for id1 only
        for (int i = 0; i < 3; i++) {
            Thread.sleep(2000);
            registry.renew("api-service", id1);
            System.out.println("\nRenewed " + id1);
            registry.printRegistry();
        }
        
        // Wait for id2 to expire
        Thread.sleep(3000);
        
        System.out.println("\nFinal state:");
        registry.printRegistry();
        
        registry.stop();
    }
}
