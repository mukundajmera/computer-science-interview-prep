package v1_basic.models;

import java.util.*;

public class CartItem {
    private final Product product;
    private int quantity;
    private final double priceAtAdd;
    private final Date addedAt;
    
    public CartItem(Product product, int quantity) {
        this.product = product;
        this.quantity = quantity;
        this.priceAtAdd = product.getPrice();
        this.addedAt = new Date();
    }
    
    public Product getProduct() { return product; }
    public int getQuantity() { return quantity; }
    public double getPriceAtAdd() { return priceAtAdd; }
    public Date getAddedAt() { return addedAt; }
    
    public void setQuantity(int quantity) {
        if (quantity < 0) {
            throw new IllegalArgumentException("Quantity cannot be negative");
        }
        this.quantity = quantity;
    }
    
    public void addQuantity(int amount) {
        this.quantity += amount;
    }
    
    public double getSubtotal() {
        return priceAtAdd * quantity;
    }
    
    @Override
    public String toString() {
        return String.format("%s x%d = $%.2f", product.getName(), quantity, getSubtotal());
    }
}