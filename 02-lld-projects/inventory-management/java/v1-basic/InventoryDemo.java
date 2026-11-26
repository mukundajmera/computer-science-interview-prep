public class InventoryDemo {
    public static void main(String[] args) {
        InventoryManager manager = new InventoryManager();
        manager.addWarehouse("W1");
        manager.addWarehouse("W2");

        manager.registerLowStockAlert("W1", "SKU-1", 3,
            (warehouseId, productId, currentQty) ->
                System.out.println("LOW STOCK: " + warehouseId + " " + productId + "=" + currentQty));

        manager.addStock("W1", "SKU-1", 5);
        manager.removeStock("W1", "SKU-1", 2);
        manager.transferStock("W1", "W2", "SKU-1", 1);
        System.out.println(manager.checkAvailability("SKU-1", 1));
    }
}
