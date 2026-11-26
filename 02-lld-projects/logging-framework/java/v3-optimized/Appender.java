package v3_optimized;

public interface Appender {
    void append(LogEvent event);
    String getName();
}
