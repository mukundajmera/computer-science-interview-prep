package v2_extended;

/** A simulated downstream failure (timeout or 5xx), injectable in tests. */
public class DownstreamError extends RuntimeException {
    public DownstreamError(String message) {
        super(message);
    }
}
