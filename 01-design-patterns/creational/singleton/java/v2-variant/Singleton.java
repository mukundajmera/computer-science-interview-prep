/**
 * Singleton Pattern - V2 Variant (Double-Checked Locking)
 * 
 * Lazy initialization with thread-safety.
 * Uses volatile + double-checked locking for efficiency.
 * 
 * Pros:
 * - Lazy initialization (created only when needed)
 * - Thread-safe
 * - Efficient (synchronization only on first call)
 * 
 * Cons:
 * - More complex implementation
 * - volatile keyword required (Java 5+)
 */
public class Singleton {

    // volatile ensures visibility across threads and prevents reordering
    private static volatile Singleton instance;

    // Private constructor
    private Singleton() {
        // Prevent reflection attack
        if (instance != null) {
            throw new RuntimeException("Use getInstance() to get the single instance");
        }
        System.out.println("Singleton instance created");
    }

    // Double-checked locking for thread-safe lazy initialization
    public static Singleton getInstance() {
        // First check (no locking)
        if (instance == null) {
            synchronized (Singleton.class) {
                // Second check (with locking)
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }

    public void doSomething() {
        System.out.println("Singleton is doing something...");
    }

    // Prevent cloning
    @Override
    protected Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("Cannot clone a Singleton");
    }

    // Handle serialization - return same instance
    protected Object readResolve() {
        return getInstance();
    }
}

/**
 * Thread-safe demo
 */
class SingletonDemo {
    public static void main(String[] args) throws InterruptedException {
        // Create multiple threads trying to get instance
        Runnable task = () -> {
            Singleton instance = Singleton.getInstance();
            System.out.println(Thread.currentThread().getName() +
                    " got instance: " + instance.hashCode());
        };

        Thread t1 = new Thread(task, "Thread-1");
        Thread t2 = new Thread(task, "Thread-2");
        Thread t3 = new Thread(task, "Thread-3");

        t1.start();
        t2.start();
        t3.start();

        t1.join();
        t2.join();
        t3.join();

        System.out.println("All threads got the same instance!");
    }
}
