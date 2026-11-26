package v3_optimized;

import v3_optimized.models.*;
import v3_optimized.enums.*;
import java.util.*;

public class ShoppingCartDemo {
    
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Online Shopping Cart - V3 Optimized Demo");
        System.out.println("=".repeat(60));
        
        ShoppingService service = new ShoppingService();
        Warehouse w1 = new Warehouse("W1", "New York");
        Warehouse w2 = new Warehouse("W2", "Los Angeles");
        service.addWarehouse(w1);
        service.addWarehouse(w2);
        
        Category electronics = new Category("CAT1", "Electronics");
        Category clothing = new Category("CAT2", "Clothing");
        Product laptop = new Product("P1", "MacBook Pro", 1999.99, electronics, 2.0);
        Product phone = new Product("P2", "iPhone 15", 999.99, electronics, 0.2);
        Product shirt = new Product("P3", "Cotton Shirt", 29.99, clothing, 0.3);
        
        service.addProduct(laptop);
        service.addProduct(phone);
        service.addProduct(shirt);
        
        service.addStock("W1", "P1", 2); 
        service.addStock("W2", "P1", 3); 
        service.addStock("W1", "P3", 10);
        
        System.out.println("1. Multi-warehouse Inventory:");
        System.out.println("   MacBook Pro Total Stock: " + service.getInventoryManager().getTotalAvailableStock("P1"));
        
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_MONTH, 30);
        Coupon discount10 = new Coupon("SAVE10", DiscountType.PERCENTAGE, 10, 50, 100, cal.getTime(), 100);
        Coupon flat20 = new Coupon("FLAT20", DiscountType.FIXED_AMOUNT, 20, 100, 20, cal.getTime(), 50);
        service.addCoupon(discount10);
        service.addCoupon(flat20);
        
        Cart cart = service.createCart("user456");
        System.out.println("\n2. Adding items (splitting stock if necessary)...");
        service.addToCart(cart.getId(), "P1", 4);  
        service.addToCart(cart.getId(), "P3", 2);  
        cart.display();
        
        System.out.println("\n3. Coupon Stacking...");
        service.applyCoupon(cart.getId(), "SAVE10");
        service.applyCoupon(cart.getId(), "FLAT20");
        
        System.out.println("\n4. Checkout (Committing holds):");
        PriceSummary summary = service.checkout(cart.getId());
        if (summary != null) {
            System.out.println("\n=== Order Confirmed ===");
            summary.display();
        }
        
        System.out.println("\n5. Remaining Stock After Checkout:");
        System.out.println("   MacBook Pro Total Stock: " + service.getInventoryManager().getTotalAvailableStock("P1"));
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Demo completed!");
        System.out.println("=".repeat(60));
    }
}
