package v2_extended;

import java.time.LocalDateTime;

/**
 * Parking Lot System - V2 Extended
 * 
 * Payment processing with multiple payment methods using Strategy pattern.
 */

/**
 * Enumeration of payment methods.
 */
enum PaymentMethod {
    CASH,
    CREDIT_CARD,
    DEBIT_CARD,
    MOBILE_PAYMENT
}

/**
 * Enumeration of payment status.
 */
enum PaymentStatus {
    PENDING,
    COMPLETED,
    FAILED,
    REFUNDED
}

/**
 * Represents a payment transaction.
 */
class Payment {
    private final String paymentId;
    private final Ticket ticket;
    private final double amount;
    private final PaymentMethod method;
    private final LocalDateTime timestamp;
    private PaymentStatus status;

    public Payment(Ticket ticket, double amount, PaymentMethod method) {
        this.paymentId = generatePaymentId();
        this.ticket = ticket;
        this.amount = amount;
        this.method = method;
        this.timestamp = LocalDateTime.now();
        this.status = PaymentStatus.PENDING;
    }

    private String generatePaymentId() {
        return "PAY-" + System.currentTimeMillis();
    }

    /**
     * Process the payment.
     */
    public boolean process() {
        // Simulate payment processing
        // In real implementation, this would call payment gateway
        try {
            Thread.sleep(100); // Simulate processing time
            this.status = PaymentStatus.COMPLETED;
            return true;
        } catch (InterruptedException e) {
            this.status = PaymentStatus.FAILED;
            return false;
        }
    }

    /**
     * Refund the payment.
     */
    public boolean refund() {
        if (status != PaymentStatus.COMPLETED) {
            return false;
        }
        this.status = PaymentStatus.REFUNDED;
        return true;
    }

    // Getters
    public String getPaymentId() {
        return paymentId;
    }

    public Ticket getTicket() {
        return ticket;
    }

    public double getAmount() {
        return amount;
    }

    public PaymentMethod getMethod() {
        return method;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public PaymentStatus getStatus() {
        return status;
    }

    @Override
    public String toString() {
        return "Payment[" + paymentId + ", $" + String.format("%.2f", amount) + 
               ", " + method + ", " + status + "]";
    }
}

/**
 * Interface for payment processing strategies.
 */
interface PaymentProcessor {
    boolean processPayment(Payment payment);
    String getProcessorName();
}

/**
 * Cash payment processor.
 */
class CashPaymentProcessor implements PaymentProcessor {
    @Override
    public boolean processPayment(Payment payment) {
        System.out.println("Processing cash payment of $" + 
                          String.format("%.2f", payment.getAmount()));
        return payment.process();
    }

    @Override
    public String getProcessorName() {
        return "Cash";
    }
}

/**
 * Card payment processor.
 */
class CardPaymentProcessor implements PaymentProcessor {
    @Override
    public boolean processPayment(Payment payment) {
        System.out.println("Processing card payment of $" + 
                          String.format("%.2f", payment.getAmount()) + 
                          " via " + payment.getMethod());
        return payment.process();
    }

    @Override
    public String getProcessorName() {
        return "Card";
    }
}

/**
 * Mobile payment processor.
 */
class MobilePaymentProcessor implements PaymentProcessor {
    @Override
    public boolean processPayment(Payment payment) {
        System.out.println("Processing mobile payment of $" + 
                          String.format("%.2f", payment.getAmount()));
        return payment.process();
    }

    @Override
    public String getProcessorName() {
        return "Mobile";
    }
}

/**
 * Factory for creating payment processors.
 */
class PaymentProcessorFactory {
    public static PaymentProcessor getProcessor(PaymentMethod method) {
        switch (method) {
            case CASH:
                return new CashPaymentProcessor();
            case CREDIT_CARD:
            case DEBIT_CARD:
                return new CardPaymentProcessor();
            case MOBILE_PAYMENT:
                return new MobilePaymentProcessor();
            default:
                return new CashPaymentProcessor();
        }
    }
}
