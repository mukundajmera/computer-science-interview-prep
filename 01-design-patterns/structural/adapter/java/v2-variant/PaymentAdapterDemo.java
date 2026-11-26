/**
 * Adapter Pattern - V2: Payment Gateway Adapter
 * 
 * Real-world scenario: E-commerce system needs to support multiple
 * payment gateways (Stripe, PayPal, Square) with different APIs.
 */

import java.util.Map;

// Target Interface - Our unified payment interface
interface PaymentProcessor {
    boolean processPayment(double amount, String currency, Map<String, String> cardDetails);
    boolean refund(String transactionId, double amount);
    String getProviderName();
}

// Adaptee 1 - Stripe-like API
class StripeAPI {
    public String createCharge(int amountInCents, String currency, String cardToken) {
        System.out.println("Stripe: Charging " + amountInCents + " cents in " + currency);
        return "stripe_txn_" + System.currentTimeMillis();
    }
    
    public boolean createRefund(String chargeId, int amountInCents) {
        System.out.println("Stripe: Refunding " + amountInCents + " cents for " + chargeId);
        return true;
    }
    
    public String createCardToken(String cardNumber, String expiry, String cvv) {
        return "tok_" + cardNumber.substring(cardNumber.length() - 4);
    }
}

// Adaptee 2 - PayPal-like API
class PayPalSDK {
    public PayPalPayment createPayment(double amount, String currencyCode) {
        return new PayPalPayment(amount, currencyCode);
    }
    
    public PayPalPayment executePayment(PayPalPayment payment, String payerId) {
        System.out.println("PayPal: Executing payment of " + payment.amount + " " + payment.currency);
        payment.transactionId = "pp_" + System.currentTimeMillis();
        payment.status = "COMPLETED";
        return payment;
    }
    
    public boolean refundPayment(String transactionId, double amount) {
        System.out.println("PayPal: Refunding " + amount + " for " + transactionId);
        return true;
    }
    
    static class PayPalPayment {
        double amount;
        String currency;
        String transactionId;
        String status;
        
        PayPalPayment(double amount, String currency) {
            this.amount = amount;
            this.currency = currency;
        }
    }
}

// Adaptee 3 - Square-like API
class SquareClient {
    public SquarePaymentResult charge(SquarePaymentRequest request) {
        System.out.println("Square: Processing " + request.amountMoney.amount + " " + request.amountMoney.currency);
        SquarePaymentResult result = new SquarePaymentResult();
        result.paymentId = "sq_" + System.currentTimeMillis();
        result.success = true;
        return result;
    }
    
    public boolean refundPayment(String paymentId, long amount) {
        System.out.println("Square: Refunding " + amount + " for " + paymentId);
        return true;
    }
    
    static class SquarePaymentRequest {
        SquareMoney amountMoney;
        String sourceId;
    }
    
    static class SquareMoney {
        long amount;
        String currency;
    }
    
    static class SquarePaymentResult {
        String paymentId;
        boolean success;
    }
}

// Adapter for Stripe
class StripeAdapter implements PaymentProcessor {
    private final StripeAPI stripe;
    private String lastTransactionId;
    
    public StripeAdapter(StripeAPI stripe) {
        this.stripe = stripe;
    }
    
    @Override
    public boolean processPayment(double amount, String currency, Map<String, String> cardDetails) {
        // Convert dollars to cents
        int amountInCents = (int) (amount * 100);
        
        // Create token from card details
        String token = stripe.createCardToken(
            cardDetails.get("number"),
            cardDetails.get("expiry"),
            cardDetails.get("cvv")
        );
        
        // Process payment
        lastTransactionId = stripe.createCharge(amountInCents, currency, token);
        return lastTransactionId != null;
    }
    
    @Override
    public boolean refund(String transactionId, double amount) {
        int amountInCents = (int) (amount * 100);
        return stripe.createRefund(transactionId, amountInCents);
    }
    
    @Override
    public String getProviderName() {
        return "Stripe";
    }
}

// Adapter for PayPal
class PayPalAdapter implements PaymentProcessor {
    private final PayPalSDK paypal;
    
    public PayPalAdapter(PayPalSDK paypal) {
        this.paypal = paypal;
    }
    
    @Override
    public boolean processPayment(double amount, String currency, Map<String, String> cardDetails) {
        PayPalSDK.PayPalPayment payment = paypal.createPayment(amount, currency);
        PayPalSDK.PayPalPayment result = paypal.executePayment(payment, "PAYER_ID");
        return "COMPLETED".equals(result.status);
    }
    
    @Override
    public boolean refund(String transactionId, double amount) {
        return paypal.refundPayment(transactionId, amount);
    }
    
    @Override
    public String getProviderName() {
        return "PayPal";
    }
}

// Adapter for Square
class SquareAdapter implements PaymentProcessor {
    private final SquareClient square;
    
    public SquareAdapter(SquareClient square) {
        this.square = square;
    }
    
    @Override
    public boolean processPayment(double amount, String currency, Map<String, String> cardDetails) {
        SquareClient.SquarePaymentRequest request = new SquareClient.SquarePaymentRequest();
        request.amountMoney = new SquareClient.SquareMoney();
        request.amountMoney.amount = (long) (amount * 100);
        request.amountMoney.currency = currency;
        request.sourceId = cardDetails.get("number");
        
        SquareClient.SquarePaymentResult result = square.charge(request);
        return result.success;
    }
    
    @Override
    public boolean refund(String transactionId, double amount) {
        return square.refundPayment(transactionId, (long) (amount * 100));
    }
    
    @Override
    public String getProviderName() {
        return "Square";
    }
}

// Client code - Payment service using any processor
class PaymentService {
    private PaymentProcessor processor;
    
    public void setProcessor(PaymentProcessor processor) {
        this.processor = processor;
        System.out.println("Using payment provider: " + processor.getProviderName());
    }
    
    public boolean checkout(double amount, Map<String, String> card) {
        return processor.processPayment(amount, "USD", card);
    }
}

// Demo
public class PaymentAdapterDemo {
    public static void main(String[] args) {
        PaymentService service = new PaymentService();
        Map<String, String> card = Map.of(
            "number", "4111111111111111",
            "expiry", "12/25",
            "cvv", "123"
        );
        
        // Use Stripe
        service.setProcessor(new StripeAdapter(new StripeAPI()));
        service.checkout(99.99, card);
        
        System.out.println();
        
        // Switch to PayPal
        service.setProcessor(new PayPalAdapter(new PayPalSDK()));
        service.checkout(49.99, card);
        
        System.out.println();
        
        // Switch to Square
        service.setProcessor(new SquareAdapter(new SquareClient()));
        service.checkout(29.99, card);
    }
}
