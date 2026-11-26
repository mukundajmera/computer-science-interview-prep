package v3_optimized.models;

import java.util.*;
import java.util.concurrent.*;

public class Warehouse {
    private final String id;
    private final String location;
    private final ConcurrentHashMap<String, Integer> inventory;

    public Warehouse(String id, String location) {
        this.id = id;
        this.location = location;
        this.inventory = new ConcurrentHashMap<>();
    }

    public String getId() { return id; }
    public String getLocation() { return location; }
    
    public void addStock(String productId, int quantity) {
        inventory.merge(productId, quantity, Integer::sum);
    }
    
    public int getStock(String productId) {
        return inventory.getOrDefault(productId, 0);
    }
    
    public boolean deductStock(String productId, int quantity) {
        while (true) {
            int current = getStock(productId);
            if (current < quantity) return false;
            if (inventory.replace(productId, current, current - quantity)) {
                return true;
            }
        }
    }
    
    public void restoreStock(String productId, int quantity) {
        addStock(productId, quantity);
    }
}
