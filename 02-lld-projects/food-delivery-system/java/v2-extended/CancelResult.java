package v2_extended;

/**
 * Outcome of a cancellation attempt: whether it happened, how much the
 * customer is refunded, and a human-readable reason either way.
 */
public class CancelResult {
    private final boolean cancelled;
    private final double refund;
    private final String reason;

    public CancelResult(boolean cancelled, double refund, String reason) {
        this.cancelled = cancelled;
        this.refund = refund;
        this.reason = reason;
    }

    public boolean isCancelled() {
        return cancelled;
    }

    public double getRefund() {
        return refund;
    }

    public String getReason() {
        return reason;
    }
}
