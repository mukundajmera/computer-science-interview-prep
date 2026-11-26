package v1_basic.models;

import java.util.*;
import java.util.concurrent.*;
public class Cart {
    private final String id;
    private final String userId;
    private final Map<String, CartItem> items;
    private final Date createdAt;
    private Date updatedAt;
    
    public Cart(String id, String userId) {
        this.id = id;
        this.userId = userId;
        this.items = new HashMap<>();
        this.createdAt = new Date();
        this.updatedAt = new Date();
    }
    
    public String getId() { return id; }
    public String getUserId() { return userId; }
    public Date getCreatedAt() { return createdAt; }
    public Date getUpdatedAt() { return updatedAt; }
    
    /**
     * Add a product to the cart.
     */
    public void addItem(Product product, int quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        
        String productId = product.getId();
        if (items.containsKey(productId)) {
            items.get(productId).addQuantity(quantity);
        } else {
            items.put(productId, new CartItem(product, quantity));
        }
        
        updateTimestamp();
    }
    
    /**
     * Remove a product from the cart.
     */
    public boolean removeItem(String productId) {
        CartItem removed = items.remove(productId);
        if (removed != null) {
            updateTimestamp();
            return true;
        }
        return false;
    }
    
    /**
     * Update quantity of a product.
     */
    public boolean updateQuantity(String productId, int quantity) {
        CartItem item = items.get(productId);
        if (item == null) {
            return false;
        }
        
        if (quantity <= 0) {
            return removeItem(productId);
        }
        
        item.setQuantity(quantity);
        updateTimestamp();
        return true;
    }
    
    /**
     * Clear all items from the cart.
     */
    public void clear() {
        items.clear();
        updateTimestamp();
    }
    
    /**
     * Get all cart items.
     */
    public List<CartItem> getItems() {
        return new ArrayList<>(items.values());
    }
    
    /**
     * Get a specific cart item.
     */
    public CartItem getItem(String productId) {
        return items.get(productId);
    }
    
    /**
     * Get total number of items (sum of quantities).
     */
    public int getTotalItems() {
        return items.values().stream()
                .mapToInt(CartItem::getQuantity)
                .sum();
    }
    
    /**
     * Get number of unique products.
     */
    public int getUniqueProducts() {
        return items.size();
    }
    
    /**
     * Check if cart is empty.
     */
    public boolean isEmpty() {
        return items.isEmpty();
    }
    
    /**
     * Calculate subtotal (before discounts, tax, shipping).
     */
    public double getSubtotal() {
        return items.values().stream()
                .mapToDouble(CartItem::getSubtotal)
                .sum();
    }
    
    /**
     * Calculate total weight.
     */
    public double getTotalWeight() {
        return items.values().stream()
                .mapToDouble(item -> item.getProduct().getWeight() * item.getQuantity())
                .sum();
    }
    
    private void updateTimestamp() {
        this.updatedAt = new Date();
    }
    
    /**
     * Display cart contents.
     */
    public void display() {
        System.out.println("\n=== Shopping Cart ===");
        System.out.println("Cart ID: " + id);
        System.out.println("User: " + userId);
        System.out.println("---");
        
        if (isEmpty()) {
            System.out.println("Cart is empty");
        } else {
            for (CartItem item : items.values()) {
                System.out.println(item);
            }
            System.out.println("---");
            System.out.printf("Subtotal: $%.2f%n", getSubtotal());
            System.out.printf("Total Items: %d%n", getTotalItems());
        }
    }
    
    @Override
    public String toString() {
        return String.format("Cart[%s] - %d items, $%.2f", id, getTotalItems(), getSubtotal());
    }
}

