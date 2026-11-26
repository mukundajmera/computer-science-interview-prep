package models;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class Payment {
    private static int counter = 0;
    
    private final String paymentId;
    private final double amount;
    private PaymentStatus status;
    private final String paymentMethod;
    private final LocalDateTime transactionDate;

    public Payment(double amount, String paymentMethod) {
        this.paymentId = "PAY-" + (++counter);
        this.amount = amount;
        this.paymentMethod = paymentMethod;
        this.status = PaymentStatus.PENDING;
        this.transactionDate = LocalDateTime.now();
    }

    public void process() {
        // Simulate payment processing
        this.status = PaymentStatus.COMPLETED;
    }

    public void refund() {
        if (status == PaymentStatus.COMPLETED) {
            status = PaymentStatus.REFUNDED;
        }
    }

    public String getPaymentId() { return paymentId; }
    public double getAmount() { return amount; }
    public PaymentStatus getStatus() { return status; }
    public String getPaymentMethod() { return paymentMethod; }
}
