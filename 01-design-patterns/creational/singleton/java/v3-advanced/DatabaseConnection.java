import java.io.*;

/**
 * Singleton Pattern - V3 Advanced (Enum Singleton - Recommended)
 * 
 * The most robust Singleton implementation in Java.
 * Recommended by Joshua Bloch in "Effective Java".
 * 
 * Pros:
 * - Thread-safe by JVM guarantee
 * - Serialization-safe by default
 * - Reflection-safe (cannot instantiate enum via reflection)
 * - Simple and concise
 * 
 * Cons:
 * - Cannot extend other classes (enum already extends Enum)
 * - Eager initialization (created when enum loaded)
 */
public enum DatabaseConnection {

    INSTANCE;

    // Configuration
    private String url;
    private String username;
    private boolean connected;

    // Constructor (called once when enum is loaded)
    DatabaseConnection() {
        this.url = "jdbc:mysql://localhost:3306/mydb";
        this.username = "admin";
        this.connected = false;
        System.out.println("DatabaseConnection enum instance created");
    }

    // Business methods
    public void connect() {
        if (!connected) {
            System.out.println("Connecting to: " + url);
            connected = true;
        } else {
            System.out.println("Already connected");
        }
    }

    public void disconnect() {
        if (connected) {
            System.out.println("Disconnecting from: " + url);
            connected = false;
        }
    }

    public void executeQuery(String query) {
        if (connected) {
            System.out.println("Executing: " + query);
        } else {
            throw new IllegalStateException("Not connected to database");
        }
    }

    public boolean isConnected() {
        return connected;
    }

    // Getters
    public String getUrl() {
        return url;
    }

    public String getUsername() {
        return username;
    }
}

/**
 * Alternative: Bill Pugh Singleton (Initialization-on-demand holder)
 * 
 * Uses static inner class for lazy + thread-safe initialization.
 * JVM guarantees thread-safety during class loading.
 */
class BillPughSingleton {

    private BillPughSingleton() {
        System.out.println("BillPughSingleton instance created");
    }

    // Static inner class - not loaded until getInstance() called
    private static class SingletonHolder {
        private static final BillPughSingleton INSTANCE = new BillPughSingleton();
    }

    public static BillPughSingleton getInstance() {
        return SingletonHolder.INSTANCE;
    }

    public void doSomething() {
        System.out.println("BillPughSingleton doing something...");
    }
}

/**
 * Demo class
 */
class SingletonDemo {
    public static void main(String[] args) {
        System.out.println("=== Enum Singleton Demo ===");

        // Get the singleton instance
        DatabaseConnection db1 = DatabaseConnection.INSTANCE;
        DatabaseConnection db2 = DatabaseConnection.INSTANCE;

        System.out.println("Same instance? " + (db1 == db2));

        // Use the connection
        db1.connect();
        db1.executeQuery("SELECT * FROM users");
        db2.disconnect(); // Same instance, so db1 is also disconnected

        System.out.println("\n=== Bill Pugh Singleton Demo ===");

        BillPughSingleton bp1 = BillPughSingleton.getInstance();
        BillPughSingleton bp2 = BillPughSingleton.getInstance();

        System.out.println("Same instance? " + (bp1 == bp2));
        bp1.doSomething();

        System.out.println("\n=== Serialization Test (Enum is safe) ===");
        try {
            // Serialize
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(DatabaseConnection.INSTANCE);

            // Deserialize
            ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bis);
            DatabaseConnection deserialized = (DatabaseConnection) ois.readObject();

            System.out.println("After serialization, same instance? " +
                    (DatabaseConnection.INSTANCE == deserialized));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
