public class PaymentOrchestrationMotif {
    public boolean shouldCompensate(String status) {
        return "FAILED".equalsIgnoreCase(status);
    }
}
