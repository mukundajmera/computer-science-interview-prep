package v2_extended;

/**
 * Raised when the timestamp no longer fits the 41-bit delta field
 * (v2 improvement #3, FOLLOW-UPS.md #1).
 */
public class TimestampOverflowException extends RuntimeException {
    public TimestampOverflowException(String message) {
        super(message);
    }
}
