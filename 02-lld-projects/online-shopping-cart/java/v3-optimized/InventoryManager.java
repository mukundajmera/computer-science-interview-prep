package v3_optimized;

import java.util.*;
import java.util.concurrent.*;
import v3_optimized.models.*;

public class InventoryManager {
    private final ConcurrentHashMap<String, Warehouse> warehouses = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, InventoryHold> activeHolds = new ConcurrentHashMap<>();
    
    private static final long HOLD_TTL_MS = 15 * 60 * 1000; // 15 minutes
    
    public void addWarehouse(Warehouse warehouse) {
        warehouses.put(warehouse.getId(), warehouse);
    }
    
    public void addStock(String warehouseId, String productId, int quantity) {
        Warehouse w = warehouses.get(warehouseId);
        if (w != null) {
            w.addStock(productId, quantity);
        }
    }
    
    public int getTotalAvailableStock(String productId) {
        cleanupExpiredHolds();
        int totalStock = warehouses.values().stream()
                .mapToInt(w -> w.getStock(productId))
                .sum();
                
        int heldStock = activeHolds.values().stream()
                .filter(h -> h.getProductId().equals(productId) && !h.isExpired())
                .mapToInt(InventoryHold::getQuantity)
                .sum();
                
        return totalStock - heldStock;
    }
    
    public boolean reserveStockAcrossWarehouses(String productId, int quantity, List<String> reservedHoldIds) {
        cleanupExpiredHolds();
        int remaining = quantity;
        
        for (Warehouse w : warehouses.values()) {
            if (remaining <= 0) break;
            
            int warehouseHeldStock = activeHolds.values().stream()
                    .filter(h -> h.getWarehouseId().equals(w.getId()) && h.getProductId().equals(productId) && !h.isExpired())
                    .mapToInt(InventoryHold::getQuantity)
                    .sum();
                    
            int availableInWarehouse = w.getStock(productId) - warehouseHeldStock;
            
            if (availableInWarehouse > 0) {
                int toReserve = Math.min(availableInWarehouse, remaining);
                String holdId = UUID.randomUUID().toString();
                InventoryHold hold = new InventoryHold(
                        holdId, productId, w.getId(), toReserve, System.currentTimeMillis() + HOLD_TTL_MS
                );
                activeHolds.put(holdId, hold);
                reservedHoldIds.add(holdId);
                remaining -= toReserve;
            }
        }
        
        if (remaining > 0) {
            for (String holdId : reservedHoldIds) {
                activeHolds.remove(holdId);
            }
            reservedHoldIds.clear();
            return false;
        }
        
        return true;
    }
    
    public boolean commitHold(String holdId) {
        InventoryHold hold = activeHolds.remove(holdId);
        if (hold != null && !hold.isExpired()) {
            Warehouse w = warehouses.get(hold.getWarehouseId());
            if (w != null) {
                return w.deductStock(hold.getProductId(), hold.getQuantity());
            }
        }
        return false;
    }
    
    private void cleanupExpiredHolds() {
        activeHolds.entrySet().removeIf(entry -> entry.getValue().isExpired());
    }
}
