/**
 * Vending Machine System - V1 Basic Demo
 * 
 * Demonstrates the basic vending machine functionality.
 */
public class VendingMachineDemo {
    
    public static void main(String[] args) {
        System.out.println("===========================================");
        System.out.println("   Vending Machine System - V1 Basic Demo");
        System.out.println("===========================================\n");
        
        // Create vending machine
        VendingMachine machine = new VendingMachine();
        
        // Setup products
        setupProducts(machine);
        
        // Setup coin inventory for change
        setupCoinInventory(machine);
        
        // Display initial status
        machine.displayStatus();
        
        // Demo 1: Successful purchase with change
        System.out.println("\n--- Demo 1: Purchase Chips with Change ---");
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1");
        machine.dispense();
        
        // Demo 2: Multiple coins, exact change
        System.out.println("\n--- Demo 2: Purchase Soda with Exact Change ---");
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.QUARTER);
        machine.insertMoney(Coin.QUARTER);
        machine.selectProduct("B1");
        machine.dispense();
        
        // Demo 3: Cancelled transaction
        System.out.println("\n--- Demo 3: Cancelled Transaction ---");
        machine.insertMoney(Coin.QUARTER);
        machine.insertMoney(Coin.QUARTER);
        machine.cancelTransaction();
        
        // Demo 4: Insufficient funds
        System.out.println("\n--- Demo 4: Insufficient Funds ---");
        machine.insertMoney(Coin.QUARTER);
        machine.selectProduct("A1"); // Chips cost $1.50, only have $0.25
        
        // Add more money
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.QUARTER);
        machine.selectProduct("A1"); // Now have $1.50
        machine.dispense();
        
        // Demo 5: Out of stock
        System.out.println("\n--- Demo 5: Out of Stock ---");
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("C1"); // Candy only had 1 item
        machine.cancelTransaction();
        
        // Demo 6: Invalid slot
        System.out.println("\n--- Demo 6: Invalid Slot ---");
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("Z9"); // Doesn't exist
        machine.cancelTransaction();
        
        // Demo 7: Changing selection
        System.out.println("\n--- Demo 7: Changing Selection ---");
        machine.insertMoney(Coin.DOLLAR);
        machine.insertMoney(Coin.DOLLAR);
        machine.selectProduct("A1"); // Select chips
        machine.selectProduct("B1"); // Change to soda
        machine.dispense();
        
        // Final status
        System.out.println("\n--- Final Machine Status ---");
        machine.displayStatus();
    }
    
    private static void setupProducts(VendingMachine machine) {
        // Format: code, name, price, quantity, maxCapacity
        machine.addSlot("A1", "Chips", 1.50, 5, 10);
        machine.addSlot("A2", "Pretzels", 1.25, 5, 10);
        machine.addSlot("B1", "Soda", 1.50, 5, 10);
        machine.addSlot("B2", "Water", 1.00, 5, 10);
        machine.addSlot("C1", "Candy Bar", 1.75, 0, 10); // Out of stock
        machine.addSlot("C2", "Gum", 0.75, 5, 10);
    }
    
    private static void setupCoinInventory(VendingMachine machine) {
        // Add coins for making change
        machine.addCoinsToInventory(Coin.QUARTER, 20);
        machine.addCoinsToInventory(Coin.DIME, 20);
        machine.addCoinsToInventory(Coin.NICKEL, 20);
        machine.addCoinsToInventory(Coin.PENNY, 20);
    }
}
