package v1_basic;

import v1_basic.models.*;
import v1_basic.enums.*;
/**
 * Online Shopping Cart - V1 Basic Demo
 */
public class ShoppingCartDemo {
    public static void main(String[] args) {
        System.out.println("=== Online Shopping Cart V1 - Basic Demo ===\n");
        
        ShoppingService.resetInstance();
        ShoppingService service = ShoppingService.getInstance();
        
        // Setup categories
        Category electronics = new Category("CAT1", "Electronics");
        Category accessories = new Category("CAT2", "Accessories");
        service.addCategory(electronics);
        service.addCategory(accessories);
        
        // Setup products
        Product laptop = new Product("P1", "Laptop", "High-performance laptop", 999.99, electronics, 2.5);
        Product mouse = new Product("P2", "Wireless Mouse", "Ergonomic mouse", 29.99, accessories, 0.1);
        Product keyboard = new Product("P3", "Mechanical Keyboard", "RGB keyboard", 79.99, accessories, 0.5);
        
        service.addProduct(laptop, 10);
        service.addProduct(mouse, 50);
        service.addProduct(keyboard, 30);
        
        System.out.println("Products added to catalog");
        
        // Create cart
        Cart cart = service.createCart("user1");
        System.out.println("Created cart: " + cart.getId());
        
        // Add items
        service.addToCart(cart.getId(), "P1", 1);
        service.addToCart(cart.getId(), "P2", 2);
        service.addToCart(cart.getId(), "P3", 1);
        
        cart.display();
        
        // Update quantity
        service.updateCartQuantity(cart.getId(), "P2", 3);
        System.out.println("\nUpdated mouse quantity to 3");
        cart.display();
        
        // Remove item
        service.removeFromCart(cart.getId(), "P3");
        System.out.println("\nRemoved keyboard");
        cart.display();
        
        // Checkout
        System.out.println("\n--- Checkout ---");
        service.checkout(cart.getId());
        
        cart.display();
        System.out.println("\n=== Demo Complete ===");
    }
}
