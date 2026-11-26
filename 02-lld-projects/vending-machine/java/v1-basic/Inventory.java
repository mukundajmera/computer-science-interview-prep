import java.util.*;

/**
 * Vending Machine System - V1 Basic
 * 
 * Inventory class managing product slots and coin stock.
 */

/**
 * Manages the inventory of products and coins in the vending machine.
 */
class Inventory {
    private final Map<String, Slot> slots;
    private final Map<Coin, Integer> coinStock;

    public Inventory() {
        this.slots = new HashMap<>();
        this.coinStock = new EnumMap<>(Coin.class);
        
        // Initialize coin stock with zeros
        for (Coin coin : Coin.values()) {
            coinStock.put(coin, 0);
        }
    }

    // ============ Slot Operations ============

    public void addSlot(Slot slot) {
        if (slot == null) {
            throw new IllegalArgumentException("Slot cannot be null");
        }
        slots.put(slot.getCode(), slot);
    }

    public Slot getSlot(String code) {
        return slots.get(code);
    }

    public boolean hasSlot(String code) {
        return slots.containsKey(code);
    }

    public List<Slot> getAllSlots() {
        return new ArrayList<>(slots.values());
    }

    public List<Product> getAvailableProducts() {
        List<Product> available = new ArrayList<>();
        for (Slot slot : slots.values()) {
            if (!slot.isEmpty()) {
                available.add(slot.getProduct());
            }
        }
        return available;
    }

    // ============ Coin Operations ============

    public void addCoins(Coin coin, int count) {
        if (coin == null) {
            throw new IllegalArgumentException("Coin cannot be null");
        }
        if (count < 0) {
            throw new IllegalArgumentException("Count cannot be negative");
        }
        coinStock.merge(coin, count, Integer::sum);
    }

    public void addCoins(List<Coin> coins) {
        for (Coin coin : coins) {
            addCoins(coin, 1);
        }
    }

    public int getCoinCount(Coin coin) {
        return coinStock.getOrDefault(coin, 0);
    }

    /**
     * Calculate and return change using greedy algorithm.
     * Returns empty list if exact change cannot be made.
     * 
     * @param amount The amount of change needed
     * @return List of coins for change, or empty list if not possible
     */
    public List<Coin> getChange(double amount) {
        List<Coin> change = new ArrayList<>();
        
        // Round to avoid floating point issues
        int amountInCents = (int) Math.round(amount * 100);
        
        // Create a copy of coin stock for this calculation
        Map<Coin, Integer> availableCoins = new EnumMap<>(coinStock);
        
        // Get coins sorted by value (highest first)
        List<Coin> coinsByValue = new ArrayList<>(Arrays.asList(Coin.values()));
        coinsByValue.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));
        
        for (Coin coin : coinsByValue) {
            int coinValueInCents = (int) Math.round(coin.getValue() * 100);
            int available = availableCoins.get(coin);
            
            while (amountInCents >= coinValueInCents && available > 0) {
                change.add(coin);
                amountInCents -= coinValueInCents;
                available--;
                availableCoins.put(coin, available);
            }
        }
        
        // If we couldn't make exact change, return empty and don't modify stock
        if (amountInCents > 0) {
            return Collections.emptyList();
        }
        
        // Deduct coins from actual stock
        for (Coin coin : change) {
            coinStock.merge(coin, -1, Integer::sum);
        }
        
        return change;
    }

    /**
     * Check if exact change can be made for the given amount.
     */
    public boolean canMakeChange(double amount) {
        int amountInCents = (int) Math.round(amount * 100);
        
        Map<Coin, Integer> availableCoins = new EnumMap<>(coinStock);
        
        List<Coin> coinsByValue = new ArrayList<>(Arrays.asList(Coin.values()));
        coinsByValue.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));
        
        for (Coin coin : coinsByValue) {
            int coinValueInCents = (int) Math.round(coin.getValue() * 100);
            int available = availableCoins.get(coin);
            
            while (amountInCents >= coinValueInCents && available > 0) {
                amountInCents -= coinValueInCents;
                available--;
            }
        }
        
        return amountInCents == 0;
    }

    public double getTotalCoinValue() {
        double total = 0;
        for (Map.Entry<Coin, Integer> entry : coinStock.entrySet()) {
            total += entry.getKey().getValue() * entry.getValue();
        }
        return total;
    }

    public void displayCoinStock() {
        System.out.println("Coin Stock:");
        for (Coin coin : Coin.values()) {
            System.out.println("  " + coin.name() + ": " + coinStock.get(coin));
        }
        System.out.println("  Total Value: $" + String.format("%.2f", getTotalCoinValue()));
    }
}
