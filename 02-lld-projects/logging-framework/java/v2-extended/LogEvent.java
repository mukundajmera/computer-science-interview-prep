package v2_extended;

public class LogEvent {
    private final String loggerName;
    private final LogLevel level;
    private final String message;
    private final long timestamp;
    private final String threadName;

    public LogEvent(String loggerName, LogLevel level, String message) {
        this.loggerName = loggerName;
        this.level = level;
        this.message = message;
        this.timestamp = System.currentTimeMillis();
        this.threadName = Thread.currentThread().getName();
    }

    public String getLoggerName() {
        return loggerName;
    }

    public LogLevel getLevel() {
        return level;
    }

    public String getMessage() {
        return message;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public String getThreadName() {
        return threadName;
    }

    @Override
    public String toString() {
        return String.format("[%tT] [%s] [%s] %s - %s", timestamp, threadName, level, loggerName, message);
    }
}
