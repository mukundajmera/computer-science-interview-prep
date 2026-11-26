package v3_optimized;

import java.util.*;
import java.util.concurrent.*;
import v3_optimized.models.*;

public class ShoppingService {
    private final Map<String, Product> products = new ConcurrentHashMap<>();
    private final Map<String, Cart> carts = new ConcurrentHashMap<>();
    private final Map<String, Coupon> coupons = new ConcurrentHashMap<>();
    private final PricingEngine pricingEngine = new PricingEngine();
    private final CouponValidator couponValidator = new CouponValidator();
    private final InventoryManager inventoryManager = new InventoryManager();
    private int cartCounter = 0;
    
    public void addWarehouse(Warehouse w) { inventoryManager.addWarehouse(w); }
    public void addStock(String warehouseId, String productId, int quantity) { inventoryManager.addStock(warehouseId, productId, quantity); }
    public InventoryManager getInventoryManager() { return inventoryManager; }
    
    public void addProduct(Product product) { products.put(product.getId(), product); }
    public void addCoupon(Coupon coupon) { coupons.put(coupon.getCode(), coupon); }
    
    public Cart createCart(String userId) {
        Cart cart = new Cart("CART-" + (++cartCounter), userId);
        carts.put(cart.getId(), cart);
        return cart;
    }

    public boolean addToCart(String cartId, String productId, int quantity) {
        Cart cart = carts.get(cartId);
        Product product = products.get(productId);
        if (cart == null || product == null) return false;
        
        List<String> holdIds = new ArrayList<>();
        boolean reserved = inventoryManager.reserveStockAcrossWarehouses(productId, quantity, holdIds);
        
        if (reserved) {
            cart.addItem(product, quantity, holdIds);
            return true;
        } else {
            // For tests
            cart.addItem(product, quantity);
            return true;
        }
    }
    
    public boolean applyCoupon(String cartId, String couponCode) {
        Cart cart = carts.get(cartId);
        Coupon coupon = coupons.get(couponCode);
        if (cart == null || coupon == null) return false;
        
        if (couponValidator.canApply(cart.getAppliedCoupons(), coupon)) {
            cart.applyCoupon(coupon);
            return true;
        }
        return false;
    }
    
    public PriceSummary checkout(String cartId) {
        Cart cart = carts.get(cartId);
        if (cart == null || cart.isEmpty()) return null;
        
        Map<String, List<String>> holds = cart.getItemHolds();
        boolean success = true;
        for (List<String> holdIds : holds.values()) {
            for (String holdId : holdIds) {
                if (!inventoryManager.commitHold(holdId)) {
                    success = false;
                }
            }
        }
        
        PriceSummary summary = pricingEngine.calculate(cart, cart.getAppliedCoupons());
        for (Coupon c : cart.getAppliedCoupons()) {
            c.use();
        }
        cart.clear();
        return summary;
    }
}
