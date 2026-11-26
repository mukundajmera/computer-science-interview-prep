package v3_optimized;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class InMemoryAppender implements Appender {
    private final String name;
    private final List<LogEvent> logs;
    private final Formatter formatter;

    public InMemoryAppender(String name, Formatter formatter) {
        this.name = name;
        this.logs = new CopyOnWriteArrayList<>();
        this.formatter = formatter;
    }
    
    public InMemoryAppender(String name) {
        this(name, new PatternFormatter("[%d] [%t] [%l] %c - %m"));
    }

    @Override
    public void append(LogEvent event) {
        logs.add(event);
    }

    @Override
    public String getName() {
        return name;
    }

    public List<LogEvent> getLogs() {
        return logs;
    }
    
    public void clear() {
        logs.clear();
    }
    
    public Formatter getFormatter() {
        return formatter;
    }
}
