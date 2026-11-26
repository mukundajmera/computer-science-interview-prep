public interface PaymentGateway {
    String getName();
    PaymentResponse processPayment(PaymentRequest request);
    double getSuccessRate();
    void recordMetrics(boolean success);
}
