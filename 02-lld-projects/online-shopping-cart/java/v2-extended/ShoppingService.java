package v2_extended;

import java.util.*;
import java.util.concurrent.*;
import v2_extended.models.*;
import v2_extended.enums.*;

public class ShoppingService {
    private final Map<String, Product> products = new HashMap<>();
    private final Map<String, Cart> carts = new HashMap<>();
    private final Map<String, Coupon> coupons = new HashMap<>();
    private final PricingEngine pricingEngine = new PricingEngine();
    private int cartCounter = 0;
    
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
        cart.addItem(product, quantity);
        return true;
    }
    
    public boolean applyCoupon(String cartId, String couponCode) {
        Cart cart = carts.get(cartId);
        Coupon coupon = coupons.get(couponCode);
        if (cart == null || coupon == null || !coupon.isValid()) return false;
        cart.applyCoupon(coupon);
        return true;
    }
    
    public PriceSummary checkout(String cartId) {
        Cart cart = carts.get(cartId);
        if (cart == null || cart.isEmpty()) return null;
        
        PriceSummary summary = pricingEngine.calculate(cart, cart.getAppliedCoupon());
        if (cart.getAppliedCoupon() != null) cart.getAppliedCoupon().use();
        cart.clear();
        return summary;
    }
}