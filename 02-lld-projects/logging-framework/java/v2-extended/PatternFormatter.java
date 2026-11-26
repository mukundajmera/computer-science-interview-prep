package v2_extended;

import java.text.SimpleDateFormat;
import java.util.Date;

public class PatternFormatter implements Formatter {
    private final String pattern;

    // Simple implementation of pattern formatting.
    // e.g., "[%d] [%t] [%l] %c - %m"
    // %d = date/time, %t = thread, %l = level, %c = logger, %m = message
    public PatternFormatter(String pattern) {
        this.pattern = pattern;
    }

    @Override
    public String format(LogEvent event) {
        String result = pattern;
        
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
        String dateStr = sdf.format(new Date(event.getTimestamp()));
        
        result = result.replace("%d", dateStr);
        result = result.replace("%t", event.getThreadName());
        result = result.replace("%l", event.getLevel().name());
        result = result.replace("%c", event.getLoggerName());
        result = result.replace("%m", event.getMessage());
        
        return result;
    }
}
