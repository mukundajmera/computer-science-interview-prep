/**
 * Composite Pattern - V1 Basic: File System
 */

import java.util.*;

// Component
interface FileSystemItem {
    String getName();
    int getSize();
    void display(String indent);
}

// Leaf
class File implements FileSystemItem {
    private String name;
    private int size;
    
    public File(String name, int size) {
        this.name = name;
        this.size = size;
    }
    
    @Override public String getName() { return name; }
    @Override public int getSize() { return size; }
    
    @Override public void display(String indent) {
        System.out.println(indent + "" + name + " (" + size + " KB)");
    }
}

// Composite
class Directory implements FileSystemItem {
    private String name;
    private List<FileSystemItem> children = new ArrayList<>();
    
    public Directory(String name) {
        this.name = name;
    }
    
    public void add(FileSystemItem item) {
        children.add(item);
    }
    
    public void remove(FileSystemItem item) {
        children.remove(item);
    }
    
    @Override public String getName() { return name; }
    
    @Override public int getSize() {
        return children.stream()
            .mapToInt(FileSystemItem::getSize)
            .sum();
    }
    
    @Override public void display(String indent) {
        System.out.println(indent + "" + name + " (" + getSize() + " KB)");
        for (FileSystemItem item : children) {
            item.display(indent + "  ");
        }
    }
}

public class FileSystemDemo {
    public static void main(String[] args) {
        // Build file system
        Directory root = new Directory("root");
        
        Directory docs = new Directory("docs");
        docs.add(new File("readme.txt", 10));
        docs.add(new File("guide.pdf", 250));
        
        Directory src = new Directory("src");
        src.add(new File("main.java", 15));
        src.add(new File("utils.java", 8));
        
        Directory lib = new Directory("lib");
        lib.add(new File("spring.jar", 5000));
        src.add(lib);  // Nested composite
        
        root.add(docs);
        root.add(src);
        root.add(new File("config.xml", 5));
        
        // Display tree
        System.out.println("=== File System ===");
        root.display("");
        
        System.out.println("\n=== Total Size ===");
        System.out.println("Root: " + root.getSize() + " KB");
        System.out.println("Src: " + src.getSize() + " KB");
    }
}
