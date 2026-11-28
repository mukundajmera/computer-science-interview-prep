package v2_extended;

/**
 * Raised when no worker ID lease is available (v2 improvement #2,
 * FOLLOW-UPS.md #3).
 */
public class WorkerIdPoolExhaustedException extends RuntimeException {
    public WorkerIdPoolExhaustedException(String message) {
        super(message);
    }
}
