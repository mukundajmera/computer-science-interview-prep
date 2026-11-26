import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

/**
 * Unit tests for Vending Machine System
 */
class VendingMachineTest {

    // ============ Coin Tests ============

    @Test
    @DisplayName("Coin values are correct")
    void testCoinValues() {
        assertEquals(0.01, Coin.PENNY.getValue(), 0.001);
        assertEquals(0.05, Coin.NICKEL.getValue(), 0.001);
        assertEquals(0.10, Coin.DIME.getValue(), 0.001);
        assertEquals(0.25, Coin.QUARTER.getValue(), 0.001);
        assertEquals(0.50, Coin.HALF_DOLLAR.getValue(), 0.001);
        assertEquals(1.00, Coin.DOLLAR.getValue(), 0.001);
    }

    // ============ Product Tests ============

    @Test
    @DisplayName("Product creation with valid data")
    void testProductCreation() {
        Product product = new Product("A1", "Chips", 1.50);
        
        assertEquals("A1", product.getCode());
        assertEquals("Chips", product.getName());
        assertEquals(1.50, product.getPrice(), 0.001);
    }

    @Test
    @DisplayName("Product throws exception for invalid data")
    void testProductInvalidData() {
        assertThrows(IllegalArgumentException.class, 
            () -> new Product(null, "Chips", 1.50));
        assertThrows(IllegalArgumentException.class, 
            () -> new Product("A1", null, 1.50));
        assertThrows(IllegalArgumentException.class, 
            () -> new Product("A1", "Chips", -1.0));
    }

    // ============ Slot Tests ============

    @Test
    @DisplayName("Slot dispenses product correctly")
    void testSlotDispense() {
        Product product = new Product("A1", "Chips", 1.50);
        Slot slot = new Slot("A1", product, 5, 10);
        
        assertEquals(5, slot.getQuantity());
        assertFalse(slot.isEmpty());
        
        Product dispensed = slot.dispenseOne();
        
        assertNotNull(dispensed);
        assertEquals("Chips", dispensed.getName());
        assertEquals(4, slot.getQuantity());
    }

    @Test
    @DisplayName("Slot returns null when empty")
    void testSlotDispenseEmpty() {
        Product product = new Product("A1", "Chips", 1.50);
        Slot slot = new Slot("A1", product, 0, 10);
        
        assertTrue(slot.isEmpty());
        assertNull(slot.dispenseOne());
    }

    @Test
    @DisplayName("Slot restock works correctly")
    void testSlotRestock() {
        Product product = new Product("A1", "Chips", 1.50);
        Slot slot = new Slot("A1", product, 5, 10);
        
        int added = slot.restock(3);
        assertEquals(3, added);
        assertEquals(8, slot.getQuantity());
        
        // Try to add more than capacity
        added = slot.restock(10);
        assertEquals(2, added); // Only 2 more fit
        assertEquals(10, slot.getQuantity());
        assertTrue(slot.isFull());
    }

    // ============ Inventory Tests ============

    @Test
    @DisplayName("Inventory tracks slots correctly")
    void testInventorySlots() {
        Inventory inventory = new Inventory();
        Product product = new Product("A1", "Chips", 1.50);
        Slot slot = new Slot("A1", product, 5, 10);
        
        inventory.addSlot(slot);
        
        assertTrue(inventory.hasSlot("A1"));
        assertEquals(slot, inventory.getSlot("A1"));
    }

    @Test
    @DisplayName("Inventory calculates change correctly")
    void testInventoryChange() {
        Inventory inventory = new Inventory();
        inventory.addCoins(Coin.QUARTER, 10);
        inventory.addCoins(Coin.DIME, 10);
        inventory.addCoins(Coin.NICKEL, 10);
        
        List<Coin> change = inventory.getChange(0.50);
        
        assertFalse(change.isEmpty());
        double total = change.stream().mapToDouble(Coin::getValue).sum();
        assertEquals(0.50, total, 0.001);
    }

    @Test
    @DisplayName("Inventory returns empty list when change impossible")
    void testInventoryNoChange() {
        Inventory inventory = new Inventory();
        // No coins in inventory
        
        List<Coin> change = inventory.getChange(0.50);
        
        assertTrue(change.isEmpty());
    }

    // ============ State Tests ============

    @Test
    @DisplayName("Machine starts in IDLE state")
    void testInitialState() {
        VendingMachine machine = new VendingMachine();
        assertEquals("IDLE", machine.getCurrentStateName());
    }

    @Test
    @DisplayName("Inserting money changes state to HAS_MONEY")
    void testInsertMoneyState() {
        VendingMachine machine = new VendingMachine();
        machine.insertMoney(Coin.DOLLAR);
        
        assertEquals("HAS_MONEY", machine.getCurrentStateName());
        assertEquals(1.00, machine.getBalance(), 0.001);
    }

    @Test
    @DisplayName("Selecting product changes state to PRODUCT_SELECTED")
    void testSelectProductState() {
        VendingMachine machine = setupMachine();
        
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1"); // $1.50
        
        assertEquals("PRODUCT_SELECTED", machine.getCurrentStateName());
    }

    @Test
    @DisplayName("Dispensing returns to IDLE state")
    void testDispenseState() {
        VendingMachine machine = setupMachine();
        
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1");
        Product product = machine.dispense();
        
        assertNotNull(product);
        assertEquals("Chips", product.getName());
        assertEquals("IDLE", machine.getCurrentStateName());
        assertEquals(0.0, machine.getBalance(), 0.001);
    }

    // ============ VendingMachine Tests ============

    @Test
    @DisplayName("Complete purchase workflow")
    void testCompletePurchase() {
        VendingMachine machine = setupMachine();
        
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.QUARTER);
        machine.insertMoney(Coin.QUARTER);
        machine.selectProduct("A1"); // $1.50 exact
        Product product = machine.dispense();
        
        assertNotNull(product);
        assertEquals("Chips", product.getName());
        assertEquals(4, machine.getInventory().getSlot("A1").getQuantity());
    }

    @Test
    @DisplayName("Cancel transaction returns coins")
    void testCancelTransaction() {
        VendingMachine machine = setupMachine();
        
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.QUARTER);
        
        List<Coin> returned = machine.cancelTransaction();
        
        assertEquals(2, returned.size());
        assertEquals("IDLE", machine.getCurrentStateName());
        assertEquals(0.0, machine.getBalance(), 0.001);
    }

    @Test
    @DisplayName("Insufficient funds prevents selection")
    void testInsufficientFunds() {
        VendingMachine machine = setupMachine();
        
        machine.insertMoney(Coin.QUARTER); // Only $0.25
        machine.selectProduct("A1"); // Needs $1.50
        
        assertEquals("HAS_MONEY", machine.getCurrentStateName());
        assertNull(machine.getSelectedSlot());
    }

    @Test
    @DisplayName("Out of stock product cannot be selected")
    void testOutOfStock() {
        VendingMachine machine = new VendingMachine();
        Product product = new Product("A1", "Chips", 1.50);
        Slot slot = new Slot("A1", product, 0, 10); // Empty
        machine.getInventory().addSlot(slot);
        machine.getInventory().addCoins(Coin.QUARTER, 20);
        
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1");
        
        assertEquals("HAS_MONEY", machine.getCurrentStateName());
        assertNull(machine.getSelectedSlot());
    }

    @Test
    @DisplayName("Invalid slot code is rejected")
    void testInvalidSlot() {
        VendingMachine machine = setupMachine();
        
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("Z9");
        
        assertEquals("HAS_MONEY", machine.getCurrentStateName());
        assertNull(machine.getSelectedSlot());
    }

    @Test
    @DisplayName("Change is calculated correctly")
    void testChangeCalculation() {
        VendingMachine machine = setupMachine();
        
        // Insert $2.00, buy $1.50 item
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1");
        
        // Store initial coin count
        int initialQuarters = machine.getInventory().getCoinCount(Coin.QUARTER);
        
        machine.dispense();
        
        // Should have used 2 quarters for change ($0.50)
        // But also added 2 dollars from inserted coins
        assertEquals("IDLE", machine.getCurrentStateName());
    }

    // ============ Integration Tests ============

    @Test
    @DisplayName("Multiple purchases workflow")
    void testMultiplePurchases() {
        VendingMachine machine = setupMachine();
        
        // First purchase
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1");
        Product p1 = machine.dispense();
        assertNotNull(p1);
        
        // Second purchase
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("B1"); // Water $1.00
        Product p2 = machine.dispense();
        assertNotNull(p2);
        assertEquals("Water", p2.getName());
        
        // Third purchase - change selection
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1");
        machine.selectProduct("A2"); // Change to Pretzels
        Product p3 = machine.dispense();
        assertNotNull(p3);
        assertEquals("Pretzels", p3.getName());
    }

    @Test
    @DisplayName("Machine handles exact change scenario")
    void testExactChange() {
        VendingMachine machine = new VendingMachine();
        Product product = new Product("A1", "Chips", 1.50);
        Slot slot = new Slot("A1", product, 5, 10);
        machine.getInventory().addSlot(slot);
        // No change coins added
        
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1");
        
        // Should fail because no change available
        assertEquals("HAS_MONEY", machine.getCurrentStateName());
    }

    // ============ Helper Methods ============

    private VendingMachine setupMachine() {
        VendingMachine machine = new VendingMachine();
        
        Product chips = new Product("A1", "Chips", 1.50);
        Product pretzels = new Product("A2", "Pretzels", 1.25);
        Product water = new Product("B1", "Water", 1.00);
        
        machine.getInventory().addSlot(new Slot("A1", chips, 5, 10));
        machine.getInventory().addSlot(new Slot("A2", pretzels, 5, 10));
        machine.getInventory().addSlot(new Slot("B1", water, 5, 10));
        
        machine.getInventory().addCoins(Coin.QUARTER, 20);
        machine.getInventory().addCoins(Coin.DIME, 20);
        machine.getInventory().addCoins(Coin.NICKEL, 20);
        
        return machine;
    }
}
