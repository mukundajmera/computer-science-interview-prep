package v2_extended;

public interface Appender {
    void append(LogEvent event);
    String getName();
}
