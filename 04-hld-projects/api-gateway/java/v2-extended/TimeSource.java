package v2_extended;

/** Injectable clock so tests can advance time deterministically. */
public interface TimeSource {
    long nowMillis();
}
