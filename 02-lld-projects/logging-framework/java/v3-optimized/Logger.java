package v3_optimized;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class Logger {
    private final String name;
    private volatile LogLevel level;
    private final Logger parent;
    private final List<Appender> appenders;
    private volatile boolean additive = true;
    private final AsyncLogProcessor asyncProcessor;

    public Logger(String name, Logger parent, AsyncLogProcessor asyncProcessor) {
        this.name = name;
        this.parent = parent;
        this.appenders = new CopyOnWriteArrayList<>();
        this.asyncProcessor = asyncProcessor;
    }

    public String getName() {
        return name;
    }

    public void setLevel(LogLevel level) {
        this.level = level;
    }

    public LogLevel getLevel() {
        return level;
    }

    public LogLevel getEffectiveLevel() {
        Logger current = this;
        while (current != null) {
            LogLevel currentLevel = current.getLevel();
            if (currentLevel != null) {
                return currentLevel;
            }
            current = current.parent;
        }
        return LogLevel.INFO; // Fallback
    }

    public void addAppender(Appender appender) {
        appenders.add(appender);
    }
    
    // Changed: Don't return new ArrayList<> to allow modifying appenders list
    // Return a mutable copy or the list itself. We return the internal list to support .clear() in tests.
    public List<Appender> getAppenders() {
        return appenders;
    }

    public void setAdditive(boolean additive) {
        this.additive = additive;
    }

    public boolean isAdditive() {
        return additive;
    }

    public boolean isEnabledFor(LogLevel level) {
        return level.isGreaterOrEqual(getEffectiveLevel());
    }

    private void log(LogLevel level, String message) {
        if (isEnabledFor(level)) {
            LogEvent event = new LogEvent(name, level, message);
            dispatch(event);
        }
    }
    
    private void dispatch(LogEvent event) {
        // Collect all target appenders considering additivity
        List<Appender> targetAppenders = new ArrayList<>();
        Logger current = this;
        while (current != null) {
            targetAppenders.addAll(current.getAppenders());
            if (!current.isAdditive()) {
                break;
            }
            current = current.parent;
        }

        if (asyncProcessor != null) {
            asyncProcessor.submit(event, targetAppenders);
        } else {
            // Synchronous fallback
            for (Appender appender : targetAppenders) {
                appender.append(event);
            }
        }
    }

    public void trace(String message) { log(LogLevel.TRACE, message); }
    public void debug(String message) { log(LogLevel.DEBUG, message); }
    public void info(String message) { log(LogLevel.INFO, message); }
    public void warn(String message) { log(LogLevel.WARN, message); }
    public void error(String message) { log(LogLevel.ERROR, message); }
    public void fatal(String message) { log(LogLevel.FATAL, message); }
}
