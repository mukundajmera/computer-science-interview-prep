package v1_basic.models;

public class Product {
    private final String id;
    private final String name;
    private final String description;
    private double price;
    private final Category category;
    private final double weight;
    
    public Product(String id, String name, String description, double price, 
                   Category category, double weight) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.price = price;
        this.category = category;
        this.weight = weight;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public double getPrice() { return price; }
    public Category getCategory() { return category; }
    public double getWeight() { return weight; }
    
    public void setPrice(double price) {
        this.price = price;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Product product = (Product) obj;
        return id.equals(product.id);
    }
    
    @Override
    public int hashCode() {
        return id.hashCode();
    }
    
    @Override
    public String toString() {
        return String.format("%s - $%.2f", name, price);
    }
}