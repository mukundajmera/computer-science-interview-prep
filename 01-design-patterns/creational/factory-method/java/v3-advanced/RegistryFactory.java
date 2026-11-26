import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Factory Method Pattern - V3 Advanced (Registry-based Factory)
 * 
 * Uses registration to dynamically add new product types
 * without modifying the factory class.
 * 
 * Benefits:
 * - Open/Closed Principle fully satisfied
 * - New types can be added at runtime
 * - No switch statements
 */

// Product interface
interface PaymentProcessor {
    void processPayment(double amount);

    boolean refund(String transactionId, double amount);

    String getProviderName();
}

// Concrete Products
class CreditCardProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.printf("Processing $%.2f via Credit Card%n", amount);
        System.out.println("  → Validating card...");
        System.out.println("  → Charging card...");
        System.out.println("  → Payment successful!");
    }

    @Override
    public boolean refund(String transactionId, double amount) {
        System.out.printf("Refunding $%.2f to Credit Card (TX: %s)%n", amount, transactionId);
        return true;
    }

    @Override
    public String getProviderName() {
        return "Credit Card";
    }
}

class PayPalProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.printf("Processing $%.2f via PayPal%n", amount);
        System.out.println("  → Redirecting to PayPal...");
        System.out.println("  → User authenticated...");
        System.out.println("  → Payment confirmed!");
    }

    @Override
    public boolean refund(String transactionId, double amount) {
        System.out.printf("Refunding $%.2f via PayPal (TX: %s)%n", amount, transactionId);
        return true;
    }

    @Override
    public String getProviderName() {
        return "PayPal";
    }
}

class CryptoProcessor implements PaymentProcessor {
    private String currency;

    public CryptoProcessor() {
        this.currency = "BTC";
    }

    public CryptoProcessor(String currency) {
        this.currency = currency;
    }

    @Override
    public void processPayment(double amount) {
        System.out.printf("Processing $%.2f equivalent in %s%n", amount, currency);
        System.out.println("  → Generating wallet address...");
        System.out.println("  → Waiting for blockchain confirmation...");
        System.out.println("  → Payment verified on chain!");
    }

    @Override
    public boolean refund(String transactionId, double amount) {
        System.out.printf("Refunding $%.2f in %s (TX: %s)%n", amount, currency, transactionId);
        return true;
    }

    @Override
    public String getProviderName() {
        return "Crypto (" + currency + ")";
    }
}

// Registry-based Factory
class PaymentProcessorFactory {

    // Registry of product creators
    private static final Map<String, Supplier<PaymentProcessor>> registry = new HashMap<>();

    // Static initializer for built-in types
    static {
        register("credit_card", CreditCardProcessor::new);
        register("paypal", PayPalProcessor::new);
        register("crypto", CryptoProcessor::new);
        register("bitcoin", () -> new CryptoProcessor("BTC"));
        register("ethereum", () -> new CryptoProcessor("ETH"));
    }

    // Register new payment processor type
    public static void register(String type, Supplier<PaymentProcessor> creator) {
        registry.put(type.toLowerCase(), creator);
        System.out.println("Registered payment processor: " + type);
    }

    // Check if type is registered
    public static boolean supports(String type) {
        return registry.containsKey(type.toLowerCase());
    }

    // Factory method
    public static PaymentProcessor create(String type) {
        Supplier<PaymentProcessor> creator = registry.get(type.toLowerCase());

        if (creator == null) {
            throw new IllegalArgumentException(
                    "Unknown payment type: " + type +
                            ". Supported types: " + registry.keySet());
        }

        return creator.get();
    }

    // List all registered types
    public static void listSupportedTypes() {
        System.out.println("Supported payment types: " + registry.keySet());
    }
}

// Custom processor that can be registered at runtime
class ApplePayProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        System.out.printf("Processing $%.2f via Apple Pay%n", amount);
        System.out.println("  → Authenticating with Face ID...");
        System.out.println("  → Payment complete!");
    }

    @Override
    public boolean refund(String transactionId, double amount) {
        System.out.printf("Refunding $%.2f via Apple Pay (TX: %s)%n", amount, transactionId);
        return true;
    }

    @Override
    public String getProviderName() {
        return "Apple Pay";
    }
}

// Demo
class RegistryFactoryDemo {
    public static void main(String[] args) {
        System.out.println("=== Registry-based Factory Demo ===\n");

        // List initial registered types
        PaymentProcessorFactory.listSupportedTypes();

        System.out.println("\n--- Processing payments with registered types ---\n");

        // Use factory to create processors
        PaymentProcessor card = PaymentProcessorFactory.create("credit_card");
        card.processPayment(99.99);

        System.out.println();

        PaymentProcessor paypal = PaymentProcessorFactory.create("PayPal");
        paypal.processPayment(49.99);

        System.out.println();

        PaymentProcessor btc = PaymentProcessorFactory.create("bitcoin");
        btc.processPayment(1000.00);

        System.out.println("\n--- Registering new payment type at runtime ---\n");

        // Register new type at runtime
        PaymentProcessorFactory.register("apple_pay", ApplePayProcessor::new);
        PaymentProcessorFactory.listSupportedTypes();

        System.out.println();

        PaymentProcessor apple = PaymentProcessorFactory.create("apple_pay");
        apple.processPayment(25.00);

        System.out.println("\n--- Testing error handling ---\n");

        try {
            PaymentProcessorFactory.create("google_pay"); // Not registered
        } catch (IllegalArgumentException e) {
            System.out.println("Expected error: " + e.getMessage());
        }
    }
}
