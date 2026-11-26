import java.util.*;

interface AlertListener {
    void onLowStock(String warehouseId, String productId, int currentQty);
}

class AlertConfig {
    private final int threshold;
    private final AlertListener listener;

    public AlertConfig(int threshold, AlertListener listener) {
        if (threshold < 0) throw new IllegalArgumentException("Threshold cannot be negative");
        this.threshold = threshold;
        this.listener = listener;
    }

    public int getThreshold() { return threshold; }
    public AlertListener getListener() { return listener; }
}

class Warehouse {
    private final String id;
    private final Map<String, Integer> stock = new HashMap<>();
    private final Map<String, List<AlertConfig>> alerts = new HashMap<>();

    public Warehouse(String id) {
        this.id = id;
    }

    public String getId() { return id; }

    public int addStock(String productId, int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive");
        stock.put(productId, stock.getOrDefault(productId, 0) + quantity);
        notifyIfLow(productId);
        return stock.get(productId);
    }

    public boolean removeStock(String productId, int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive");
        int current = stock.getOrDefault(productId, 0);
        if (current < quantity) return false;
        stock.put(productId, current - quantity);
        notifyIfLow(productId);
        return true;
    }

    public int getStock(String productId) {
        return stock.getOrDefault(productId, 0);
    }

    public void registerAlert(String productId, AlertConfig config) {
        alerts.computeIfAbsent(productId, k -> new ArrayList<>()).add(config);
        notifyIfLow(productId);
    }

    private void notifyIfLow(String productId) {
        int qty = getStock(productId);
        List<AlertConfig> productAlerts = alerts.getOrDefault(productId, Collections.emptyList());
        for (AlertConfig config : productAlerts) {
            if (qty < config.getThreshold()) {
                config.getListener().onLowStock(id, productId, qty);
            }
        }
    }
}

class InventoryManager {
    private final Map<String, Warehouse> warehouses = new HashMap<>();

    public Warehouse addWarehouse(String warehouseId) {
        return warehouses.computeIfAbsent(warehouseId, Warehouse::new);
    }

    public int addStock(String warehouseId, String productId, int quantity) {
        return getWarehouse(warehouseId).addStock(productId, quantity);
    }

    public boolean removeStock(String warehouseId, String productId, int quantity) {
        return getWarehouse(warehouseId).removeStock(productId, quantity);
    }

    public boolean transferStock(String fromWarehouseId, String toWarehouseId, String productId, int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive");
        Warehouse source = getWarehouse(fromWarehouseId);
        Warehouse destination = getWarehouse(toWarehouseId);
        if (!source.removeStock(productId, quantity)) return false;
        destination.addStock(productId, quantity);
        return true;
    }

    public List<String> checkAvailability(String productId, int requiredQuantity) {
        if (requiredQuantity <= 0) throw new IllegalArgumentException("Required quantity must be positive");
        List<String> available = new ArrayList<>();
        for (Map.Entry<String, Warehouse> entry : warehouses.entrySet()) {
            if (entry.getValue().getStock(productId) >= requiredQuantity) {
                available.add(entry.getKey());
            }
        }
        Collections.sort(available);
        return available;
    }

    public void registerLowStockAlert(
        String warehouseId,
        String productId,
        int threshold,
        AlertListener listener
    ) {
        getWarehouse(warehouseId).registerAlert(productId, new AlertConfig(threshold, listener));
    }

    private Warehouse getWarehouse(String warehouseId) {
        Warehouse warehouse = warehouses.get(warehouseId);
        if (warehouse == null) throw new IllegalArgumentException("Unknown warehouse: " + warehouseId);
        return warehouse;
    }
}
