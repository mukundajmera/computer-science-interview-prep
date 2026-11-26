/**
 * Flyweight Pattern - V1 Basic: Tree Forest
 */

import java.util.*;

// Flyweight - Shared intrinsic state
class TreeType {
    private String name;
    private String color;
    private String texture;  // Expensive data
    
    public TreeType(String name, String color, String texture) {
        this.name = name;
        this.color = color;
        this.texture = texture;
        System.out.println("Creating TreeType: " + name);
    }
    
    public void draw(int x, int y) {
        System.out.printf("Drawing %s tree at (%d, %d)%n", name, x, y);
    }
}

// Flyweight Factory
class TreeTypeFactory {
    private static Map<String, TreeType> treeTypes = new HashMap<>();
    
    public static TreeType getTreeType(String name, String color, String texture) {
        String key = name + "_" + color + "_" + texture;
        
        if (!treeTypes.containsKey(key)) {
            treeTypes.put(key, new TreeType(name, color, texture));
        }
        return treeTypes.get(key);
    }
    
    public static int getTreeTypeCount() {
        return treeTypes.size();
    }

    public static void reset() {
        treeTypes.clear();
    }
}

// Context - Contains extrinsic state
class Tree {
    private int x, y;  // Extrinsic state
    private TreeType type;  // Reference to flyweight
    
    public Tree(int x, int y, TreeType type) {
        this.x = x;
        this.y = y;
        this.type = type;
    }
    
    public void draw() {
        type.draw(x, y);
    }
}

// Forest with many trees
class Forest {
    private List<Tree> trees = new ArrayList<>();
    
    public void plantTree(int x, int y, String name, String color, String texture) {
        TreeType type = TreeTypeFactory.getTreeType(name, color, texture);
        trees.add(new Tree(x, y, type));
    }
    
    public void draw() {
        for (Tree tree : trees) {
            tree.draw();
        }
    }
    
    public int getTreeCount() {
        return trees.size();
    }
}

public class FlyweightDemo {
    public static void main(String[] args) {
        Forest forest = new Forest();
        
        // Plant many trees, but only a few types
        Random rand = new Random();
        String[] types = {"Oak", "Pine", "Birch"};
        String[] colors = {"Green", "DarkGreen"};
        
        System.out.println("=== Creating Forest ===");
        for (int i = 0; i < 100; i++) {
            forest.plantTree(
                rand.nextInt(1000),
                rand.nextInt(1000),
                types[rand.nextInt(types.length)],
                colors[rand.nextInt(colors.length)],
                "standard_texture"
            );
        }
        
        System.out.println("\n=== Statistics ===");
        System.out.println("Total trees: " + forest.getTreeCount());
        System.out.println("Tree types created: " + TreeTypeFactory.getTreeTypeCount());
        System.out.println("Memory saved: ~" + 
            (forest.getTreeCount() - TreeTypeFactory.getTreeTypeCount()) * 100 + " bytes");
        
        System.out.println("\n=== Drawing first 5 trees ===");
        // Draw just first few for demo
    }
}
