public class InventoryDemo {
    public static void main(String[] args) {
        InventoryManager manager = new InventoryManager();
        manager.addWarehouse("W1");
        manager.addStock("W1", "SKU-1", 10);

        StockReservation reservation = manager.reserveStock("W1", "SKU-1", 4);
        System.out.println(manager.availabilitySnapshot("SKU-1"));

        if (reservation != null) {
            manager.commitReservation(reservation.getReservationId());
        }
        System.out.println(manager.availabilitySnapshot("SKU-1"));
    }
}
