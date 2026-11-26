package v1_basic.models;

import java.util.*;

public class Inventory {
    private final Map<String, Integer> stock;
    
    public Inventory() {
        this.stock = new HashMap<>();
    }
    
    public void addStock(String productId, int quantity) {
        stock.merge(productId, quantity, Integer::sum);
    }
    
    public int getStock(String productId) {
        return stock.getOrDefault(productId, 0);
    }
    
    public boolean checkStock(String productId, int quantity) {
        return getStock(productId) >= quantity;
    }
    
    public boolean deductStock(String productId, int quantity) {
        int current = getStock(productId);
        if (current >= quantity) {
            stock.put(productId, current - quantity);
            return true;
        }
        return false;
    }
}