package prototype.v1;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

/**
 * Prototype Pattern - V1 Basic
 * 
 * Creates new objects by cloning existing prototypes.
 * Useful when object creation is expensive or complex.
 */

// Prototype interface
public interface Prototype<T> {
    T clone();
}

// Concrete Prototype - Shape hierarchy
abstract class Shape implements Prototype<Shape> {
    protected String color;
    protected int x;
    protected int y;

    // Default constructor
    public Shape() {
        this.color = "black";
        this.x = 0;
        this.y = 0;
    }

    // Copy constructor (for cloning)
    public Shape(Shape source) {
        this.color = source.color;
        this.x = source.x;
        this.y = source.y;
    }

    // Setters for configuration
    public Shape setColor(String color) {
        this.color = color;
        return this;
    }

    public Shape setPosition(int x, int y) {
        this.x = x;
        this.y = y;
        return this;
    }

    @Override
    public abstract Shape clone();

    public abstract void draw();

    @Override
    public String toString() {
        return String.format("%s at (%d, %d) [%s]",
                getClass().getSimpleName(), x, y, color);
    }
}

// Concrete Prototypes
class Circle extends Shape {
    private int radius;

    public Circle() {
        super();
        this.radius = 10;
    }

    public Circle(Circle source) {
        super(source);
        this.radius = source.radius;
    }

    public Circle setRadius(int radius) {
        this.radius = radius;
        return this;
    }

    @Override
    public Circle clone() {
        return new Circle(this);
    }

    @Override
    public void draw() {
        System.out.println("Drawing " + this);
    }

    @Override
    public String toString() {
        return String.format("Circle(r=%d) at (%d, %d) [%s]",
                radius, x, y, color);
    }
}

class Rectangle extends Shape {
    private int width;
    private int height;

    public Rectangle() {
        super();
        this.width = 20;
        this.height = 10;
    }

    public Rectangle(Rectangle source) {
        super(source);
        this.width = source.width;
        this.height = source.height;
    }

    public Rectangle setDimensions(int width, int height) {
        this.width = width;
        this.height = height;
        return this;
    }

    @Override
    public Rectangle clone() {
        return new Rectangle(this);
    }

    @Override
    public void draw() {
        System.out.println("Drawing " + this);
    }

    @Override
    public String toString() {
        return String.format("Rectangle(%dx%d) at (%d, %d) [%s]",
                width, height, x, y, color);
    }
}

// Complex object with nested objects (demonstrating deep copy)
class Document implements Prototype<Document> {
    private String title;
    private String content;
    private List<String> tags;
    private Map<String, String> metadata;

    public Document() {
        this.title = "Untitled";
        this.content = "";
        this.tags = new ArrayList<>();
        this.metadata = new HashMap<>();
    }

    // Copy constructor - performs deep copy
    public Document(Document source) {
        this.title = source.title;
        this.content = source.content;
        // Deep copy collections
        this.tags = new ArrayList<>(source.tags);
        this.metadata = new HashMap<>(source.metadata);
    }

    public Document setTitle(String title) {
        this.title = title;
        return this;
    }

    public Document setContent(String content) {
        this.content = content;
        return this;
    }

    public Document addTag(String tag) {
        this.tags.add(tag);
        return this;
    }

    public Document addMetadata(String key, String value) {
        this.metadata.put(key, value);
        return this;
    }

    @Override
    public Document clone() {
        return new Document(this);
    }

    @Override
    public String toString() {
        return String.format("Document{title='%s', tags=%s, metadata=%s}",
                title, tags, metadata);
    }
}

// Prototype Registry - stores and provides prototypes
class PrototypeRegistry {
    private static final Map<String, Prototype<?>> prototypes = new HashMap<>();

    public static void register(String key, Prototype<?> prototype) {
        prototypes.put(key, prototype);
        System.out.println("Registered prototype: " + key);
    }

    @SuppressWarnings("unchecked")
    public static <T extends Prototype<T>> T getClone(String key) {
        Prototype<?> prototype = prototypes.get(key);
        if (prototype == null) {
            throw new IllegalArgumentException("Prototype not found: " + key);
        }
        return (T) prototype.clone();
    }

    public static boolean contains(String key) {
        return prototypes.containsKey(key);
    }

    public static void listPrototypes() {
        System.out.println("Available prototypes: " + prototypes.keySet());
    }
}

// Demo
class PrototypeDemo {
    public static void main(String[] args) {
        System.out.println("=== Prototype Pattern Demo ===\n");

        // Register prototype shapes
        System.out.println("--- Registering Prototypes ---");
        PrototypeRegistry.register("red-circle",
                new Circle().setRadius(50).setColor("red"));
        PrototypeRegistry.register("blue-rectangle",
                new Rectangle().setDimensions(100, 50).setColor("blue"));
        PrototypeRegistry.register("document-template",
                new Document()
                        .setTitle("Template")
                        .setContent("This is a template document.")
                        .addTag("template")
                        .addMetadata("version", "1.0"));

        PrototypeRegistry.listPrototypes();

        // Clone shapes
        System.out.println("\n--- Cloning Shapes ---\n");

        Shape shape1 = (Shape) PrototypeRegistry.getClone("red-circle");
        Circle circle1 = (Circle) shape1;
        circle1.draw();

        Shape shape2 = (Shape) PrototypeRegistry.getClone("red-circle");
        Circle circle2 = (Circle) shape2;
        circle2.setPosition(100, 100);
        circle2.draw();

        // Verify independence
        System.out.println("Same instance? " + (circle1 == circle2)); // false

        Shape shape3 = (Shape) PrototypeRegistry.getClone("blue-rectangle");
        Rectangle rect1 = (Rectangle) shape3;
        rect1.setPosition(50, 50);
        rect1.draw();

        // Clone and modify document
        System.out.println("\n--- Cloning Documents ---\n");

        Document doc1 = PrototypeRegistry.getClone("document-template");
        doc1.setTitle("Report Q1 2024")
                .addTag("report")
                .addMetadata("author", "Alice");

        Document doc2 = PrototypeRegistry.getClone("document-template");
        doc2.setTitle("Report Q2 2024")
                .addTag("report")
                .addMetadata("author", "Bob");

        System.out.println("Doc1: " + doc1);
        System.out.println("Doc2: " + doc2);

        // Verify deep copy
        System.out.println("\n--- Verify Deep Copy ---");
        Document original = new Document()
                .setTitle("Original")
                .addTag("original-tag");

        Document cloned = original.clone();
        cloned.setTitle("Cloned")
                .addTag("cloned-tag");

        System.out.println("Original: " + original);
        System.out.println("Cloned: " + cloned);
        System.out.println("Tags are independent: " +
                !original.toString().contains("cloned-tag"));
    }
}
