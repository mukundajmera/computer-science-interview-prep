package v1_basic;

import java.util.*;
import java.util.concurrent.*;
import v1_basic.models.*;
import v1_basic.enums.*;

public class ShoppingService {
    private final Map<String, Product> products;
    private final Map<String, Category> categories;
    private final Map<String, Cart> carts;
    private final Inventory inventory;
    private int cartCounter = 0;
    
    private static ShoppingService instance;
    
    private ShoppingService() {
        this.products = new HashMap<>();
        this.categories = new HashMap<>();
        this.carts = new HashMap<>();
        this.inventory = new Inventory();
    }
    
    public static synchronized ShoppingService getInstance() {
        if (instance == null) {
            instance = new ShoppingService();
        }
        return instance;
    }
    
    public static void resetInstance() {
        instance = null;
    }
    
    // Product management
    public void addCategory(Category category) {
        categories.put(category.getId(), category);
    }
    
    public void addProduct(Product product, int initialStock) {
        products.put(product.getId(), product);
        inventory.addStock(product.getId(), initialStock);
    }
    
    public Product getProduct(String productId) {
        return products.get(productId);
    }
    
    public List<Product> searchProducts(String query) {
        String lowerQuery = query.toLowerCase();
        return products.values().stream()
                .filter(p -> p.getName().toLowerCase().contains(lowerQuery) ||
                           p.getDescription().toLowerCase().contains(lowerQuery))
                .toList();
    }
    
    public List<Product> getProductsByCategory(String categoryId) {
        return products.values().stream()
                .filter(p -> p.getCategory() != null && 
                           p.getCategory().getId().equals(categoryId))
                .toList();
    }
    
    // Cart management
    public Cart createCart(String userId) {
        String cartId = "CART-" + (++cartCounter);
        Cart cart = new Cart(cartId, userId);
        carts.put(cartId, cart);
        return cart;
    }
    
    public Cart getCart(String cartId) {
        return carts.get(cartId);
    }
    
    public boolean addToCart(String cartId, String productId, int quantity) {
        Cart cart = carts.get(cartId);
        Product product = products.get(productId);
        
        if (cart == null || product == null) {
            return false;
        }
        
        // Check inventory
        CartItem existing = cart.getItem(productId);
        int totalRequired = quantity + (existing != null ? existing.getQuantity() : 0);
        
        if (!inventory.checkStock(productId, totalRequired)) {
            System.out.println("Insufficient stock for " + product.getName());
            return false;
        }
        
        cart.addItem(product, quantity);
        return true;
    }
    
    public boolean removeFromCart(String cartId, String productId) {
        Cart cart = carts.get(cartId);
        if (cart == null) return false;
        return cart.removeItem(productId);
    }
    
    public boolean updateCartQuantity(String cartId, String productId, int quantity) {
        Cart cart = carts.get(cartId);
        if (cart == null) return false;
        
        // Check inventory for new quantity
        if (quantity > 0 && !inventory.checkStock(productId, quantity)) {
            System.out.println("Insufficient stock");
            return false;
        }
        
        return cart.updateQuantity(productId, quantity);
    }
    
    // Checkout (simple version)
    public boolean checkout(String cartId) {
        Cart cart = carts.get(cartId);
        if (cart == null || cart.isEmpty()) {
            System.out.println("Cart is empty or not found");
            return false;
        }
        
        // Verify and deduct inventory
        for (CartItem item : cart.getItems()) {
            String productId = item.getProduct().getId();
            int quantity = item.getQuantity();
            
            if (!inventory.deductStock(productId, quantity)) {
                System.out.println("Checkout failed: insufficient stock for " + 
                                  item.getProduct().getName());
                return false;
            }
        }
        
        // Clear cart after successful checkout
        double total = cart.getSubtotal();
        cart.clear();
        
        System.out.printf("Checkout successful! Total: $%.2f%n", total);
        return true;
    }
    
    public Inventory getInventory() {
        return inventory;
    }
}