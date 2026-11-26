package v3_optimized.models;

import java.util.Date;

public class InventoryHold {
    private final String holdId;
    private final String productId;
    private final String warehouseId;
    private final int quantity;
    private final long expiresAt;

    public InventoryHold(String holdId, String productId, String warehouseId, int quantity, long expiresAt) {
        this.holdId = holdId;
        this.productId = productId;
        this.warehouseId = warehouseId;
        this.quantity = quantity;
        this.expiresAt = expiresAt;
    }

    public String getHoldId() { return holdId; }
    public String getProductId() { return productId; }
    public String getWarehouseId() { return warehouseId; }
    public int getQuantity() { return quantity; }
    public boolean isExpired() { return System.currentTimeMillis() > expiresAt; }
}
