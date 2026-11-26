package v1_basic;

public class ClockMovedBackwardsException extends RuntimeException {
    public ClockMovedBackwardsException(String message) {
        super(message);
    }
}
