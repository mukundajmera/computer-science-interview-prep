package v1_basic;

public interface Appender {
    void append(LogEvent event);
    String getName();
}
