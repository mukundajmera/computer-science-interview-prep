package v3_optimized.models;

import java.util.*;

public class CartItem {
    private final Product product;
    private int quantity;
    private final double priceAtAdd;
    
    public CartItem(Product product, int quantity) {
        this.product = product; this.quantity = quantity; this.priceAtAdd = product.getPrice();
    }
    public Product getProduct() { return product; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int q) { this.quantity = q; }
    public void addQuantity(int q) { this.quantity += q; }
    public double getSubtotal() { return priceAtAdd * quantity; }
}