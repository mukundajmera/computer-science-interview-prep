package v1_basic.models;

public class Category {
    private final String id;
    private final String name;
    private Category parent;
    
    public Category(String id, String name) {
        this(id, name, null);
    }
    
    public Category(String id, String name, Category parent) {
        this.id = id;
        this.name = name;
        this.parent = parent;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public Category getParent() { return parent; }
    
    @Override
    public String toString() {
        return name;
    }
}