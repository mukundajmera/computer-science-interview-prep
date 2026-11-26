import java.util.*;

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

class StockReservation {
    private final String reservationId;
    private final String warehouseId;
    private final String productId;
    private final int quantity;
    private boolean active;

    public StockReservation(String reservationId, String warehouseId, String productId, int quantity) {
        this.reservationId = reservationId;
        this.warehouseId = warehouseId;
        this.productId = productId;
        this.quantity = quantity;
        this.active = true;
    }

    public String getReservationId() { return reservationId; }
    public String getWarehouseId() { return warehouseId; }
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public boolean isActive() { return active; }
    public void deactivate() { this.active = false; }
}

class Warehouse {
    private final String id;
    private final Map<String, Integer> stock = new HashMap<>();
    private final Map<String, List<AlertConfig>> alerts = new HashMap<>();

    public Warehouse(String id) { this.id = id; }

    public int addStock(String productId, int quantity) {
        stock.put(productId, stock.getOrDefault(productId, 0) + quantity);
        notifyIfLow(productId);
        return stock.get(productId);
    }

    public boolean removeStock(String productId, int quantity) {
        int current = stock.getOrDefault(productId, 0);
        if (current < quantity) return false;
        stock.put(productId, current - quantity);
        notifyIfLow(productId);
        return true;
    }

    public int getStock(String productId) { return stock.getOrDefault(productId, 0); }

    public void registerAlert(String productId, AlertConfig config) {
        alerts.computeIfAbsent(productId, k -> new ArrayList<>()).add(config);
        notifyIfLow(productId);
    }

    private void notifyIfLow(String productId) {
        int qty = getStock(productId);
        for (AlertConfig config : alerts.getOrDefault(productId, Collections.emptyList())) {
            if (qty < config.getThreshold()) {
                config.getListener().onLowStock(id, productId, qty);
            }
        }
    }
}

class InventoryManager {
    private final Map<String, Warehouse> warehouses = new HashMap<>();
    private final Map<String, StockReservation> reservations = new HashMap<>();
    private int reservationCounter = 0;

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
        Warehouse source = getWarehouse(fromWarehouseId);
        Warehouse destination = getWarehouse(toWarehouseId);
        if (!source.removeStock(productId, quantity)) return false;
        destination.addStock(productId, quantity);
        return true;
    }

    public StockReservation reserveStock(String warehouseId, String productId, int quantity) {
        Warehouse warehouse = getWarehouse(warehouseId);
        if (!warehouse.removeStock(productId, quantity)) return null;
        reservationCounter += 1;
        StockReservation reservation = new StockReservation(
            "R-" + reservationCounter,
            warehouseId,
            productId,
            quantity
        );
        reservations.put(reservation.getReservationId(), reservation);
        return reservation;
    }

    public boolean releaseReservation(String reservationId) {
        StockReservation reservation = reservations.get(reservationId);
        if (reservation == null || !reservation.isActive()) return false;
        getWarehouse(reservation.getWarehouseId()).addStock(reservation.getProductId(), reservation.getQuantity());
        reservation.deactivate();
        return true;
    }

    public boolean commitReservation(String reservationId) {
        StockReservation reservation = reservations.get(reservationId);
        if (reservation == null || !reservation.isActive()) return false;
        reservation.deactivate();
        return true;
    }

    public Map<String, Integer> availabilitySnapshot(String productId) {
        Map<String, Integer> snapshot = new HashMap<>();
        for (Map.Entry<String, Warehouse> entry : warehouses.entrySet()) {
            snapshot.put(entry.getKey(), entry.getValue().getStock(productId));
        }
        return snapshot;
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
