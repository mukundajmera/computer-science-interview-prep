public class InventoryDemo {
    public static void main(String[] args) {
        InventoryManager manager = new InventoryManager();
        manager.addWarehouse("A");
        manager.addWarehouse("B");
        manager.addStock("A", "P", 9);

        System.out.println(manager.transferStock("A", "B", "P", 4));
        System.out.println(manager.checkAvailability("P", 4));
    }
}
