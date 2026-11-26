/**
 * Proxy Pattern - V2: Protection Proxy
 * 
 * Demonstrates access control based on user roles.
 */

import java.util.*;

// Subject Interface
interface Document {
    String read();
    void write(String content);
    void delete();
    String getName();
}

// Real Subject
class RealDocument implements Document {
    private String name;
    private String content;
    
    public RealDocument(String name) {
        this.name = name;
        this.content = "Document content for: " + name;
    }
    
    @Override public String read() { return content; }
    @Override public void write(String content) { this.content = content; }
    @Override public void delete() { System.out.println("Document deleted: " + name); }
    @Override public String getName() { return name; }
}

// User with roles
class User {
    private String username;
    private Set<String> roles;
    
    public User(String username, String... roles) {
        this.username = username;
        this.roles = new HashSet<>(Arrays.asList(roles));
    }
    
    public String getUsername() { return username; }
    public boolean hasRole(String role) { return roles.contains(role); }
}

// Protection Proxy
class ProtectedDocumentProxy implements Document {
    private RealDocument document;
    private User currentUser;
    
    public ProtectedDocumentProxy(RealDocument document, User user) {
        this.document = document;
        this.currentUser = user;
    }
    
    @Override
    public String read() {
        if (currentUser.hasRole("reader") || currentUser.hasRole("admin")) {
            System.out.println("[ACCESS] " + currentUser.getUsername() + " reading document");
            return document.read();
        }
        throw new SecurityException("Access denied: No read permission");
    }
    
    @Override
    public void write(String content) {
        if (currentUser.hasRole("writer") || currentUser.hasRole("admin")) {
            System.out.println("[ACCESS] " + currentUser.getUsername() + " writing to document");
            document.write(content);
            return;
        }
        throw new SecurityException("Access denied: No write permission");
    }
    
    @Override
    public void delete() {
        if (currentUser.hasRole("admin")) {
            System.out.println("[ACCESS] " + currentUser.getUsername() + " deleting document");
            document.delete();
            return;
        }
        throw new SecurityException("Access denied: Admin role required");
    }
    
    @Override
    public String getName() {
        return document.getName();
    }
}

// Demo
public class ProtectionProxyDemo {
    public static void main(String[] args) {
        RealDocument doc = new RealDocument("sensitive.txt");
        
        // Different users with different roles
        User admin = new User("alice", "admin");
        User writer = new User("bob", "reader", "writer");
        User reader = new User("charlie", "reader");
        User guest = new User("guest");
        
        System.out.println("=== Admin Access ===");
        Document adminProxy = new ProtectedDocumentProxy(doc, admin);
        System.out.println("Read: " + adminProxy.read());
        adminProxy.write("New content");
        
        System.out.println("\n=== Writer Access ===");
        Document writerProxy = new ProtectedDocumentProxy(doc, writer);
        System.out.println("Read: " + writerProxy.read());
        writerProxy.write("Writer's content");
        try {
            writerProxy.delete();  // Should fail
        } catch (SecurityException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        System.out.println("\n=== Reader Access ===");
        Document readerProxy = new ProtectedDocumentProxy(doc, reader);
        System.out.println("Read: " + readerProxy.read());
        try {
            readerProxy.write("Hacked!");  // Should fail
        } catch (SecurityException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        System.out.println("\n=== Guest Access ===");
        Document guestProxy = new ProtectedDocumentProxy(doc, guest);
        try {
            guestProxy.read();  // Should fail
        } catch (SecurityException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
