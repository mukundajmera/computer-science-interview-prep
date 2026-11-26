package v3_optimized;

public class ConsoleAppender implements Appender {
    private final String name;
    private final Formatter formatter;

    public ConsoleAppender(String name, Formatter formatter) {
        this.name = name;
        this.formatter = formatter;
    }
    
    public ConsoleAppender(String name) {
        this(name, new PatternFormatter("[%d] [%t] [%l] %c - %m"));
    }

    @Override
    public void append(LogEvent event) {
        System.out.println(formatter.format(event));
    }

    @Override
    public String getName() {
        return name;
    }
}
