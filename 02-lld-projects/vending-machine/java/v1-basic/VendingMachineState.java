import java.util.List;

/**
 * Vending Machine System - V1 Basic
 * 
 * State pattern interfaces and implementations for vending machine states.
 */

/**
 * Interface for vending machine states.
 */
interface VendingMachineState {
    void insertMoney(VendingMachine machine, Coin coin);
    void selectProduct(VendingMachine machine, String slotCode);
    Product dispense(VendingMachine machine);
    List<Coin> cancel(VendingMachine machine);
    String getStateName();
}

/**
 * Idle state - machine is waiting for customer interaction.
 */
class IdleState implements VendingMachineState {
    
    @Override
    public void insertMoney(VendingMachine machine, Coin coin) {
        machine.addToBalance(coin);
        System.out.println("Inserted: " + coin + ". Balance: $" + 
                           String.format("%.2f", machine.getBalance()));
        machine.setState(new HasMoneyState());
    }
    
    @Override
    public void selectProduct(VendingMachine machine, String slotCode) {
        System.out.println("Please insert money first.");
    }
    
    @Override
    public Product dispense(VendingMachine machine) {
        System.out.println("Please insert money and select a product first.");
        return null;
    }
    
    @Override
    public List<Coin> cancel(VendingMachine machine) {
        System.out.println("No transaction to cancel.");
        return java.util.Collections.emptyList();
    }
    
    @Override
    public String getStateName() {
        return "IDLE";
    }
}

/**
 * Has money state - customer has inserted money but not selected product.
 */
class HasMoneyState implements VendingMachineState {
    
    @Override
    public void insertMoney(VendingMachine machine, Coin coin) {
        machine.addToBalance(coin);
        System.out.println("Inserted: " + coin + ". Balance: $" + 
                           String.format("%.2f", machine.getBalance()));
    }
    
    @Override
    public void selectProduct(VendingMachine machine, String slotCode) {
        Slot slot = machine.getInventory().getSlot(slotCode);
        
        if (slot == null) {
            System.out.println("Invalid slot code: " + slotCode);
            return;
        }
        
        if (slot.isEmpty()) {
            System.out.println("Sorry, " + slot.getProduct().getName() + " is out of stock.");
            return;
        }
        
        if (machine.getBalance() < slot.getProduct().getPrice()) {
            System.out.println("Insufficient balance. " + slot.getProduct().getName() + 
                               " costs $" + String.format("%.2f", slot.getProduct().getPrice()) +
                               ". Your balance: $" + String.format("%.2f", machine.getBalance()));
            return;
        }
        
        // Check if we can make change
        double changeNeeded = machine.getBalance() - slot.getProduct().getPrice();
        if (changeNeeded > 0 && !machine.getInventory().canMakeChange(changeNeeded)) {
            System.out.println("Sorry, cannot provide exact change. Please use exact amount or cancel.");
            return;
        }
        
        machine.setSelectedSlot(slot);
        System.out.println("Selected: " + slot.getProduct().getName() + 
                           ". Press dispense to complete purchase.");
        machine.setState(new ProductSelectedState());
    }
    
    @Override
    public Product dispense(VendingMachine machine) {
        System.out.println("Please select a product first.");
        return null;
    }
    
    @Override
    public List<Coin> cancel(VendingMachine machine) {
        List<Coin> refund = machine.getInsertedCoins();
        System.out.println("Transaction cancelled. Returning: " + refund.size() + " coin(s)");
        machine.resetTransaction();
        machine.setState(new IdleState());
        return refund;
    }
    
    @Override
    public String getStateName() {
        return "HAS_MONEY";
    }
}

/**
 * Product selected state - customer has selected a product.
 */
class ProductSelectedState implements VendingMachineState {
    
    @Override
    public void insertMoney(VendingMachine machine, Coin coin) {
        machine.addToBalance(coin);
        System.out.println("Inserted: " + coin + ". Balance: $" + 
                           String.format("%.2f", machine.getBalance()));
    }
    
    @Override
    public void selectProduct(VendingMachine machine, String slotCode) {
        // Allow changing selection
        Slot slot = machine.getInventory().getSlot(slotCode);
        
        if (slot == null) {
            System.out.println("Invalid slot code: " + slotCode);
            return;
        }
        
        if (slot.isEmpty()) {
            System.out.println("Sorry, " + slot.getProduct().getName() + " is out of stock.");
            return;
        }
        
        if (machine.getBalance() < slot.getProduct().getPrice()) {
            System.out.println("Insufficient balance for " + slot.getProduct().getName());
            return;
        }
        
        machine.setSelectedSlot(slot);
        System.out.println("Changed selection to: " + slot.getProduct().getName());
    }
    
    @Override
    public Product dispense(VendingMachine machine) {
        Slot slot = machine.getSelectedSlot();
        Product product = slot.getProduct();
        
        // Dispense product
        Product dispensed = slot.dispenseOne();
        if (dispensed == null) {
            System.out.println("Error: Product out of stock.");
            machine.setState(new HasMoneyState());
            return null;
        }
        
        // Add inserted coins to inventory
        machine.getInventory().addCoins(machine.getInsertedCoins());
        
        // Calculate and return change
        double changeAmount = machine.getBalance() - product.getPrice();
        if (changeAmount > 0) {
            List<Coin> change = machine.getInventory().getChange(changeAmount);
            System.out.println("Dispensing: " + product.getName());
            System.out.println("Returning change: $" + String.format("%.2f", changeAmount) + 
                               " (" + change.size() + " coin(s))");
        } else {
            System.out.println("Dispensing: " + product.getName());
            System.out.println("No change required.");
        }
        
        machine.resetTransaction();
        machine.setState(new IdleState());
        
        return dispensed;
    }
    
    @Override
    public List<Coin> cancel(VendingMachine machine) {
        List<Coin> refund = machine.getInsertedCoins();
        System.out.println("Transaction cancelled. Returning: " + refund.size() + " coin(s)");
        machine.resetTransaction();
        machine.setState(new IdleState());
        return refund;
    }
    
    @Override
    public String getStateName() {
        return "PRODUCT_SELECTED";
    }
}
