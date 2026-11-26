import java.util.*;

/**
 * Vending Machine System - V1 Basic
 * 
 * Main VendingMachine class implementing State pattern.
 */

/**
 * Main vending machine class that delegates to state objects.
 */
class VendingMachine {
    private VendingMachineState currentState;
    private final Inventory inventory;
    private double currentBalance;
    private Slot selectedSlot;
    private final List<Coin> insertedCoins;

    public VendingMachine() {
        this.currentState = new IdleState();
        this.inventory = new Inventory();
        this.currentBalance = 0;
        this.selectedSlot = null;
        this.insertedCoins = new ArrayList<>();
    }

    // ============ Public Operations (Delegated to State) ============

    public void insertMoney(Coin coin) {
        if (coin == null) {
            throw new IllegalArgumentException("Coin cannot be null");
        }
        currentState.insertMoney(this, coin);
    }

    public void selectProduct(String slotCode) {
        if (slotCode == null || slotCode.isEmpty()) {
            throw new IllegalArgumentException("Slot code cannot be null or empty");
        }
        currentState.selectProduct(this, slotCode);
    }

    public Product dispense() {
        return currentState.dispense(this);
    }

    public List<Coin> cancelTransaction() {
        return currentState.cancel(this);
    }

    // ============ State Management ============

    public void setState(VendingMachineState state) {
        this.currentState = state;
    }

    public String getCurrentStateName() {
        return currentState.getStateName();
    }

    // ============ Balance Management ============

    public void addToBalance(Coin coin) {
        currentBalance += coin.getValue();
        insertedCoins.add(coin);
    }

    public double getBalance() {
        return currentBalance;
    }

    public List<Coin> getInsertedCoins() {
        return new ArrayList<>(insertedCoins);
    }

    public void resetTransaction() {
        currentBalance = 0;
        selectedSlot = null;
        insertedCoins.clear();
    }

    // ============ Slot Management ============

    public void setSelectedSlot(Slot slot) {
        this.selectedSlot = slot;
    }

    public Slot getSelectedSlot() {
        return selectedSlot;
    }

    // ============ Inventory Access ============

    public Inventory getInventory() {
        return inventory;
    }

    public void addSlot(String code, String productName, double price, int quantity, int maxCapacity) {
        Product product = new Product(code, productName, price);
        Slot slot = new Slot(code, product, quantity, maxCapacity);
        inventory.addSlot(slot);
    }

    public List<Product> getAvailableProducts() {
        return inventory.getAvailableProducts();
    }

    // ============ Admin Operations ============

    public void restockSlot(String slotCode, int quantity) {
        Slot slot = inventory.getSlot(slotCode);
        if (slot == null) {
            System.out.println("Slot not found: " + slotCode);
            return;
        }
        int added = slot.restock(quantity);
        System.out.println("Added " + added + " items to slot " + slotCode);
    }

    public void addCoinsToInventory(Coin coin, int count) {
        inventory.addCoins(coin, count);
        System.out.println("Added " + count + " " + coin.name() + " coins to inventory");
    }

    // ============ Display ============

    public void displayProducts() {
        System.out.println("\n=== Available Products ===");
        for (Slot slot : inventory.getAllSlots()) {
            String status = slot.isEmpty() ? " [OUT OF STOCK]" : "";
            System.out.println(slot + status);
        }
        System.out.println();
    }

    public void displayStatus() {
        System.out.println("\n=== Vending Machine Status ===");
        System.out.println("State: " + getCurrentStateName());
        System.out.println("Current Balance: $" + String.format("%.2f", currentBalance));
        if (selectedSlot != null) {
            System.out.println("Selected: " + selectedSlot.getProduct().getName());
        }
        System.out.println();
        displayProducts();
        inventory.displayCoinStock();
    }
}
