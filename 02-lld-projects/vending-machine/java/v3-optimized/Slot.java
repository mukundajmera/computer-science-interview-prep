/**
 * Vending Machine System - V1 Basic
 * 
 * Slot class representing a product slot in the vending machine.
 */

/**
 * Represents a slot in the vending machine that holds products.
 */
class Slot {
    private final String code;
    private final Product product;
    private int quantity;
    private final int maxCapacity;

    public Slot(String code, Product product, int quantity, int maxCapacity) {
        if (code == null || code.isEmpty()) {
            throw new IllegalArgumentException("Slot code cannot be null or empty");
        }
        if (product == null) {
            throw new IllegalArgumentException("Product cannot be null");
        }
        if (quantity < 0) {
            throw new IllegalArgumentException("Quantity cannot be negative");
        }
        if (maxCapacity < 1) {
            throw new IllegalArgumentException("Max capacity must be at least 1");
        }
        if (quantity > maxCapacity) {
            throw new IllegalArgumentException("Quantity cannot exceed max capacity");
        }
        
        this.code = code;
        this.product = product;
        this.quantity = quantity;
        this.maxCapacity = maxCapacity;
    }

    public String getCode() {
        return code;
    }

    public Product getProduct() {
        return product;
    }

    public int getQuantity() {
        return quantity;
    }

    public int getMaxCapacity() {
        return maxCapacity;
    }

    public boolean isEmpty() {
        return quantity == 0;
    }

    public boolean isFull() {
        return quantity == maxCapacity;
    }

    /**
     * Dispense one product from this slot.
     * @return The dispensed product, or null if slot is empty
     */
    public Product dispenseOne() {
        if (isEmpty()) {
            return null;
        }
        quantity--;
        return product;
    }

    /**
     * Restock products to this slot.
     * @param count Number of products to add
     * @return Actual number added (may be less if capacity limit reached)
     */
    public int restock(int count) {
        if (count < 0) {
            throw new IllegalArgumentException("Restock count cannot be negative");
        }
        int spaceAvailable = maxCapacity - quantity;
        int added = Math.min(count, spaceAvailable);
        quantity += added;
        return added;
    }

    @Override
    public String toString() {
        return "[" + code + "] " + product.getName() + " ($" + 
               String.format("%.2f", product.getPrice()) + ") - " + 
               quantity + "/" + maxCapacity;
    }
}
