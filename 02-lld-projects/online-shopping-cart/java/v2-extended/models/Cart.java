package v2_extended.models;

import java.util.*;
import java.util.concurrent.*;
import v2_extended.*;
public class Cart {
    private final String id;
    private final String userId;
    private final Map<String, CartItem> items = new HashMap<>();
    private Coupon appliedCoupon;
    
    public Cart(String id, String userId) { this.id = id; this.userId = userId; }
    public String getId() { return id; }
    
    public void addItem(Product product, int quantity) {
        if (items.containsKey(product.getId())) items.get(product.getId()).addQuantity(quantity);
        else items.put(product.getId(), new CartItem(product, quantity));
    }
    
    public boolean removeItem(String productId) { return items.remove(productId) != null; }
    public void clear() { items.clear(); appliedCoupon = null; }
    public List<CartItem> getItems() { return new ArrayList<>(items.values()); }
    public boolean isEmpty() { return items.isEmpty(); }
    
    public double getSubtotal() {
        return items.values().stream().mapToDouble(CartItem::getSubtotal).sum();
    }
    
    public double getTotalWeight() {
        return items.values().stream()
            .mapToDouble(i -> i.getProduct().getWeight() * i.getQuantity()).sum();
    }
    
    public void applyCoupon(Coupon coupon) { this.appliedCoupon = coupon; }
    public Coupon getAppliedCoupon() { return appliedCoupon; }
    
    public void display() {
        System.out.println("\n=== Cart: " + id + " ===");
        for (CartItem item : items.values()) {
            System.out.printf("%s x%d = $%.2f%n", item.getProduct().getName(), 
                            item.getQuantity(), item.getSubtotal());
        }
    }
}

