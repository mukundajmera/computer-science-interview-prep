/**
 * Strategy Pattern - V1 Basic: Payment Processing
 */

// Strategy Interface
interface PaymentStrategy {
    void pay(double amount);
    String getName();
}

// Concrete Strategies
class CreditCardPayment implements PaymentStrategy {
    private String cardNumber;
    private String name;
    
    public CreditCardPayment(String cardNumber, String name) {
        this.cardNumber = cardNumber;
        this.name = name;
    }
    
    @Override
    public void pay(double amount) {
        System.out.printf("Paid $%.2f with Credit Card ending in %s%n", 
            amount, cardNumber.substring(cardNumber.length() - 4));
    }
    
    @Override
    public String getName() { return "Credit Card"; }
}

class PayPalPayment implements PaymentStrategy {
    private String email;
    
    public PayPalPayment(String email) {
        this.email = email;
    }
    
    @Override
    public void pay(double amount) {
        System.out.printf("Paid $%.2f via PayPal account: %s%n", amount, email);
    }
    
    @Override
    public String getName() { return "PayPal"; }
}

class CryptoPayment implements PaymentStrategy {
    private String walletAddress;
    
    public CryptoPayment(String walletAddress) {
        this.walletAddress = walletAddress;
    }
    
    @Override
    public void pay(double amount) {
        System.out.printf("Paid $%.2f in cryptocurrency to wallet: %s%n", 
            amount, walletAddress.substring(0, 8) + "...");
    }
    
    @Override
    public String getName() { return "Cryptocurrency"; }
}

// Context
class ShoppingCart {
    private PaymentStrategy paymentStrategy;
    private double total = 0;
    
    public void addItem(String item, double price) {
        total += price;
        System.out.println("Added: " + item + " - $" + price);
    }
    
    public void setPaymentStrategy(PaymentStrategy strategy) {
        this.paymentStrategy = strategy;
        System.out.println("Payment method: " + strategy.getName());
    }
    
    public void checkout() {
        if (paymentStrategy == null) {
            throw new IllegalStateException("No payment method selected");
        }
        System.out.println("\n--- Checkout ---");
        System.out.println("Total: $" + total);
        paymentStrategy.pay(total);
        total = 0;
    }
}

public class StrategyDemo {
    public static void main(String[] args) {
        ShoppingCart cart = new ShoppingCart();
        
        // Add items
        cart.addItem("Laptop", 999.99);
        cart.addItem("Mouse", 29.99);
        
        // Pay with Credit Card
        cart.setPaymentStrategy(new CreditCardPayment("4111111111111111", "John Doe"));
        cart.checkout();
        
        // Different order with PayPal
        System.out.println("\n=== New Order ===");
        cart.addItem("Keyboard", 149.99);
        cart.setPaymentStrategy(new PayPalPayment("john@example.com"));
        cart.checkout();
        
        // Another order with Crypto
        System.out.println("\n=== New Order ===");
        cart.addItem("Monitor", 299.99);
        cart.setPaymentStrategy(new CryptoPayment("0x742d35Cc6634C0532925a3b844Bc454e4438f44e"));
        cart.checkout();
    }
}
