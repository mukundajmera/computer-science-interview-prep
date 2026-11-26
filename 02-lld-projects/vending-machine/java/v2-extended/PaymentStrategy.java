/**
 * Vending Machine System - V2 Extended
 * 
 * Payment strategy pattern for different payment methods.
 */

/**
 * Interface for payment strategies.
 */
interface PaymentStrategy {
    boolean pay(double amount);
    double getPaymentAmount();
    String getPaymentMethod();
    boolean canRefund();
    boolean refund(double amount);
}

/**
 * Cash payment using coins and notes.
 */
class CashPayment implements PaymentStrategy {
    private double totalInserted;
    
    public CashPayment() {
        this.totalInserted = 0;
    }
    
    public void insertCoin(Coin coin) {
        totalInserted += coin.getValue();
    }
    
    public void insertNote(Note note) {
        totalInserted += note.getValue();
    }
    
    @Override
    public boolean pay(double amount) {
        if (totalInserted >= amount) {
            totalInserted -= amount;
            return true;
        }
        return false;
    }
    
    @Override
    public double getPaymentAmount() {
        return totalInserted;
    }
    
    @Override
    public String getPaymentMethod() {
        return "CASH";
    }
    
    @Override
    public boolean canRefund() {
        return true;
    }
    
    @Override
    public boolean refund(double amount) {
        totalInserted += amount;
        return true;
    }
    
    public double getChange() {
        return totalInserted;
    }
    
    public void clearBalance() {
        totalInserted = 0;
    }
}

/**
 * Card payment (credit/debit).
 */
class CardPayment implements PaymentStrategy {
    private final String cardNumber;
    private double chargedAmount;
    
    public CardPayment(String cardNumber) {
        this.cardNumber = cardNumber;
        this.chargedAmount = 0;
    }
    
    @Override
    public boolean pay(double amount) {
        // Simulate card processing
        if (validateCard() && processPayment(amount)) {
            chargedAmount = amount;
            return true;
        }
        return false;
    }
    
    private boolean validateCard() {
        // In real implementation, would validate card
        return cardNumber != null && cardNumber.length() >= 13;
    }
    
    private boolean processPayment(double amount) {
        // In real implementation, would process payment
        System.out.println("Processing card payment of $" + String.format("%.2f", amount));
        return true;
    }
    
    @Override
    public double getPaymentAmount() {
        return chargedAmount;
    }
    
    @Override
    public String getPaymentMethod() {
        return "CARD";
    }
    
    @Override
    public boolean canRefund() {
        return true;
    }
    
    @Override
    public boolean refund(double amount) {
        System.out.println("Refunding $" + String.format("%.2f", amount) + " to card");
        chargedAmount = 0;
        return true;
    }
    
    public String getMaskedCardNumber() {
        if (cardNumber.length() >= 4) {
            return "****" + cardNumber.substring(cardNumber.length() - 4);
        }
        return "****";
    }
}

/**
 * Mobile payment (digital wallet).
 */
class MobilePayment implements PaymentStrategy {
    private final String phoneNumber;
    private double chargedAmount;
    
    public MobilePayment(String phoneNumber) {
        this.phoneNumber = phoneNumber;
        this.chargedAmount = 0;
    }
    
    @Override
    public boolean pay(double amount) {
        // Simulate mobile payment processing
        if (validatePhone() && processPayment(amount)) {
            chargedAmount = amount;
            return true;
        }
        return false;
    }
    
    private boolean validatePhone() {
        return phoneNumber != null && phoneNumber.length() >= 10;
    }
    
    private boolean processPayment(double amount) {
        System.out.println("Processing mobile payment of $" + String.format("%.2f", amount));
        return true;
    }
    
    @Override
    public double getPaymentAmount() {
        return chargedAmount;
    }
    
    @Override
    public String getPaymentMethod() {
        return "MOBILE";
    }
    
    @Override
    public boolean canRefund() {
        return true;
    }
    
    @Override
    public boolean refund(double amount) {
        System.out.println("Refunding $" + String.format("%.2f", amount) + " to mobile wallet");
        chargedAmount = 0;
        return true;
    }
}
