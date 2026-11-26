package v3_optimized.models;

import java.util.*;
import java.util.concurrent.*;

public class Cart {
    private final String id;
    private final String userId;
    private final Map<String, CartItem> items = new ConcurrentHashMap<>();
    private final List<Coupon> appliedCoupons = new CopyOnWriteArrayList<>();
    private final Map<String, List<String>> itemHolds = new ConcurrentHashMap<>(); 
    
    public Cart(String id, String userId) { this.id = id; this.userId = userId; }
    public String getId() { return id; }
    
    public void addItem(Product product, int quantity) {
        items.compute(product.getId(), (k, v) -> {
            if (v == null) return new CartItem(product, quantity);
            v.addQuantity(quantity);
            return v;
        });
    }

    public void addItem(Product product, int quantity, List<String> holdIds) {
        addItem(product, quantity);
        itemHolds.computeIfAbsent(product.getId(), k -> new CopyOnWriteArrayList<>()).addAll(holdIds);
    }
    
    public boolean removeItem(String productId) { 
        CartItem removed = items.remove(productId); 
        return removed != null;
    }
    
    public void clear() { 
        items.clear(); 
        appliedCoupons.clear(); 
        itemHolds.clear();
    }
    
    public List<CartItem> getItems() { return new ArrayList<>(items.values()); }
    public boolean isEmpty() { return items.isEmpty(); }
    
    public double getSubtotal() {
        return items.values().stream().mapToDouble(CartItem::getSubtotal).sum();
    }
    
    public double getTotalWeight() {
        return items.values().stream()
            .mapToDouble(i -> i.getProduct().getWeight() * i.getQuantity()).sum();
    }
    
    public void applyCoupon(Coupon coupon) { this.appliedCoupons.add(coupon); }
    public List<Coupon> getAppliedCoupons() { return new ArrayList<>(appliedCoupons); }
    public Coupon getAppliedCoupon() { return appliedCoupons.isEmpty() ? null : appliedCoupons.get(0); }
    
    public Map<String, List<String>> getItemHolds() { return itemHolds; }
    
    public void display() {
        System.out.println("\n=== Cart: " + id + " ===");
        for (CartItem item : items.values()) {
            System.out.printf("%s x%d = $%.2f%n", item.getProduct().getName(), 
                            item.getQuantity(), item.getSubtotal());
        }
    }
}
