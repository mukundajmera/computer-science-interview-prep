package singleton.v1;
/**
 * Singleton Pattern - V1 Basic (Eager Initialization)
 * 
 * The instance is created at class loading time.
 * Thread-safe because JVM handles class loading synchronization.
 * 
 * Pros:
 * - Simple implementation
 * - Thread-safe without explicit synchronization
 * 
 * Cons:
 * - Instance created even if never used (not lazy)
 * - Cannot handle exceptions in construction gracefully
 */
public class Singleton {
    
    // Instance created at class loading
    private static final Singleton INSTANCE = new Singleton();
    
    // Private constructor prevents external instantiation
    private Singleton() {
        System.out.println("Singleton instance created");
    }
    
    // Global access point
    public static Singleton getInstance() {
        return INSTANCE;
    }
    
    // Example business method
    public void doSomething() {
        System.out.println("Singleton is doing something...");
    }
    
    // Prevent cloning
    @Override
    protected Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("Cannot clone a Singleton");
    }
}

/**
 * Demo class to test Singleton
 */
class SingletonDemo {
    public static void main(String[] args) {
        // Get the singleton instance
        Singleton s1 = Singleton.getInstance();
        Singleton s2 = Singleton.getInstance();
        
        // Verify both references point to same instance
        System.out.println("s1 hashCode: " + s1.hashCode());
        System.out.println("s2 hashCode: " + s2.hashCode());
        System.out.println("Same instance? " + (s1 == s2));
        
        // Use the singleton
        s1.doSomething();
    }
}
