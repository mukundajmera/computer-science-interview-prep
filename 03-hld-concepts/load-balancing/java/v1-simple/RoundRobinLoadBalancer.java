package v1_simple;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * V1: Simple Round Robin Load Balancer
 * 
 * A basic load balancer that distributes requests evenly
 * across available servers in a circular order.
 * 
 * Features:
 * - Round robin algorithm
 * - Thread-safe counter
 * - Simple server pool management
 * 
 * Limitations:
 * - No health checks
 * - No server weights
 * - No consideration of server load
 */
public class RoundRobinLoadBalancer {
    
    private final List<String> servers;
    private final AtomicInteger currentIndex;
    
    /**
     * Creates a load balancer with the given servers.
     * 
     * @param servers List of server addresses (e.g., "192.168.1.1:8080")
     */
    public RoundRobinLoadBalancer(List<String> servers) {
        if (servers == null || servers.isEmpty()) {
            throw new IllegalArgumentException("Server list cannot be empty");
        }
        this.servers = new ArrayList<>(servers);
        this.currentIndex = new AtomicInteger(0);
    }
    
    /**
     * Gets the next server in round-robin order.
     * Thread-safe using atomic operations.
     * 
     * @return Server address
     */
    public String getNextServer() {
        int index = currentIndex.getAndUpdate(i -> (i + 1) % servers.size());
        return servers.get(index);
    }
    
    /**
     * Adds a new server to the pool.
     */
    public synchronized void addServer(String server) {
        if (!servers.contains(server)) {
            servers.add(server);
        }
    }
    
    /**
     * Removes a server from the pool.
     */
    public synchronized void removeServer(String server) {
        servers.remove(server);
    }
    
    /**
     * Returns current server count.
     */
    public int getServerCount() {
        return servers.size();
    }
    
    /**
     * Returns all servers.
     */
    public List<String> getServers() {
        return new ArrayList<>(servers);
    }
}
