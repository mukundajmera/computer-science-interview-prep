import java.util.*;
import java.util.concurrent.locks.ReentrantLock;

interface AlertListener {
    void onLowStock(String warehouseId, String productId, int currentQty);
}

class AlertConfig {
    private final int threshold;
    private final AlertListener listener;

    public AlertConfig(int threshold, AlertListener listener) {
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
    private final ReentrantLock lock = new ReentrantLock();

    public Warehouse(String id) { this.id = id; }

    public String getId() { return id; }
    public ReentrantLock getLock() { return lock; }

    public int addStock(String productId, int quantity) {
        lock.lock();
        try {
            stock.put(productId, stock.getOrDefault(productId, 0) + quantity);
            notifyIfLow(productId);
            return stock.get(productId);
        } finally {
            lock.unlock();
        }
    }

    public boolean removeStock(String productId, int quantity) {
        lock.lock();
        try {
            return removeStockNoLock(productId, quantity);
        } finally {
            lock.unlock();
        }
    }

    public int getStock(String productId) {
        lock.lock();
        try {
            return stock.getOrDefault(productId, 0);
        } finally {
            lock.unlock();
        }
    }

    public boolean removeStockNoLock(String productId, int quantity) {
        int current = stock.getOrDefault(productId, 0);
        if (current < quantity) return false;
        stock.put(productId, current - quantity);
        notifyIfLow(productId);
        return true;
    }

    public void addStockNoLock(String productId, int quantity) {
        stock.put(productId, stock.getOrDefault(productId, 0) + quantity);
        notifyIfLow(productId);
    }

    public void registerAlert(String productId, AlertConfig config) {
        lock.lock();
        try {
            alerts.computeIfAbsent(productId, k -> new ArrayList<>()).add(config);
            notifyIfLow(productId);
        } finally {
            lock.unlock();
        }
    }

    private void notifyIfLow(String productId) {
        int qty = stock.getOrDefault(productId, 0);
        for (AlertConfig config : alerts.getOrDefault(productId, Collections.emptyList())) {
            if (qty < config.getThreshold()) {
                config.getListener().onLowStock(id, productId, qty);
            }
        }
    }
}

class InventoryManager {
    private final Map<String, Warehouse> warehouses = new HashMap<>();

    public synchronized Warehouse addWarehouse(String warehouseId) {
        return warehouses.computeIfAbsent(warehouseId, Warehouse::new);
    }

    public int addStock(String warehouseId, String productId, int quantity) {
        return getWarehouse(warehouseId).addStock(productId, quantity);
    }

    public boolean removeStock(String warehouseId, String productId, int quantity) {
        return getWarehouse(warehouseId).removeStock(productId, quantity);
    }

    public boolean transferStock(String fromWarehouseId, String toWarehouseId, String productId, int quantity) {
        Warehouse source = getWarehouse(fromWarehouseId);
        Warehouse destination = getWarehouse(toWarehouseId);

        Warehouse first = source.getId().compareTo(destination.getId()) <= 0 ? source : destination;
        Warehouse second = first == source ? destination : source;

        first.getLock().lock();
        second.getLock().lock();
        try {
            if (!source.removeStockNoLock(productId, quantity)) return false;
            destination.addStockNoLock(productId, quantity);
            return true;
        } finally {
            second.getLock().unlock();
            first.getLock().unlock();
        }
    }

    public List<String> checkAvailability(String productId, int requiredQuantity) {
        List<String> available = new ArrayList<>();
        for (Map.Entry<String, Warehouse> entry : warehouses.entrySet()) {
            if (entry.getValue().getStock(productId) >= requiredQuantity) {
                available.add(entry.getKey());
            }
        }
        Collections.sort(available);
        return available;
    }

    public void registerLowStockAlert(String warehouseId, String productId, int threshold, AlertListener listener) {
        getWarehouse(warehouseId).registerAlert(productId, new AlertConfig(threshold, listener));
    }

    private Warehouse getWarehouse(String warehouseId) {
        Warehouse warehouse = warehouses.get(warehouseId);
        if (warehouse == null) throw new IllegalArgumentException("Unknown warehouse: " + warehouseId);
        return warehouse;
    }
}
