package v2_extended;

/** Injectable sleeper so tests can record backoff delays without sleeping. */
public interface Sleeper {
    void sleep(long millis) throws InterruptedException;
}
