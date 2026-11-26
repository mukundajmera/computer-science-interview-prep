package v3_optimized.models;

public class Product {
    private final String id;
    private final String name;
    private double price;
    private final Category category;
    private final double weight;
    
    public Product(String id, String name, double price, Category category, double weight) {
        this.id = id; this.name = name; this.price = price; this.category = category; this.weight = weight;
    }
    public String getId() { return id; }
    public String getName() { return name; }
    public double getPrice() { return price; }
    public Category getCategory() { return category; }
    public double getWeight() { return weight; }
}