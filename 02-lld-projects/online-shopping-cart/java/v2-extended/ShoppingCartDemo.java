package v2_extended;

import v2_extended.models.*;
import v2_extended.enums.*;
/**
 * Online Shopping Cart - V2 Extended Demo
 */
import java.util.*;

public class ShoppingCartDemo {
    
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Online Shopping Cart - V2 Extended Demo");
        System.out.println("=".repeat(60));
        
        ShoppingService service = new ShoppingService();
        
        // Create categories
        Category electronics = new Category("CAT1", "Electronics");
        Category clothing = new Category("CAT2", "Clothing");
        
        // Create products
        Product laptop = new Product("P1", "MacBook Pro", 1999.99, electronics, 2.0);
        Product phone = new Product("P2", "iPhone 15", 999.99, electronics, 0.2);
        Product shirt = new Product("P3", "Cotton Shirt", 29.99, clothing, 0.3);
        Product jeans = new Product("P4", "Denim Jeans", 59.99, clothing, 0.5);
        
        service.addProduct(laptop);
        service.addProduct(phone);
        service.addProduct(shirt);
        service.addProduct(jeans);
        
        // Create coupons
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_MONTH, 30);
        
        Coupon discount10 = new Coupon("SAVE10", DiscountType.PERCENTAGE, 10, 
                                       50, 100, cal.getTime(), 100);
        
        cal.add(Calendar.DAY_OF_MONTH, -23);
        Coupon discount20 = new Coupon("FLAT20", DiscountType.FIXED_AMOUNT, 20,
                                       100, 20, cal.getTime(), 50);
        
        service.addCoupon(discount10);
        service.addCoupon(discount20);
        
        System.out.println("\n1. Available coupons:");
        System.out.println("   - SAVE10: 10% off (min $50, max $100 discount)");
        System.out.println("   - FLAT20: $20 off (min $100 order)");
        
        // Create cart and add items
        Cart cart = service.createCart("user456");
        System.out.println("\n2. Created cart: " + cart.getId());
        
        service.addToCart(cart.getId(), "P1", 1);  // MacBook
        service.addToCart(cart.getId(), "P3", 2);  // 2 shirts
        
        cart.display();
        
        // Apply coupon
        System.out.println("\n3. Applying SAVE10 coupon...");
        service.applyCoupon(cart.getId(), "SAVE10");
        
        // Checkout
        System.out.println("\n4. Checkout:");
        PriceSummary summary = service.checkout(cart.getId());
        if (summary != null) {
            System.out.println("\n=== Order Confirmed ===");
            summary.display();
        }
        
        // New cart with different coupon
        System.out.println("\n5. New cart with FLAT20 coupon...");
        Cart cart2 = service.createCart("user789");
        service.addToCart(cart2.getId(), "P2", 1);
        service.addToCart(cart2.getId(), "P4", 1);
        
        cart2.display();
        
        service.applyCoupon(cart2.getId(), "FLAT20");
        
        PriceSummary summary2 = service.checkout(cart2.getId());
        if (summary2 != null) {
            summary2.display();
        }
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Demo completed!");
        System.out.println("=".repeat(60));
    }
}
