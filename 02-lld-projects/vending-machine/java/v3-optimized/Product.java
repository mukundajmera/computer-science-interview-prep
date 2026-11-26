/**
 * Vending Machine System - V1 Basic
 * 
 * Product class representing items sold in the vending machine.
 */

/**
 * Represents a product in the vending machine.
 */
class Product {
    private final String code;
    private final String name;
    private final double price;

    public Product(String code, String name, double price) {
        if (code == null || code.isEmpty()) {
            throw new IllegalArgumentException("Product code cannot be null or empty");
        }
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("Product name cannot be null or empty");
        }
        if (price < 0) {
            throw new IllegalArgumentException("Product price cannot be negative");
        }
        this.code = code;
        this.name = name;
        this.price = price;
    }

    public String getCode() {
        return code;
    }

    public String getName() {
        return name;
    }

    public double getPrice() {
        return price;
    }

    @Override
    public String toString() {
        return code + ": " + name + " - $" + String.format("%.2f", price);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Product product = (Product) obj;
        return code.equals(product.code);
    }

    @Override
    public int hashCode() {
        return code.hashCode();
    }
}
