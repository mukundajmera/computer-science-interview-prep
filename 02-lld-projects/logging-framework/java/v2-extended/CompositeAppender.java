package v2_extended;

import java.util.ArrayList;
import java.util.List;

public class CompositeAppender implements Appender {
    private final String name;
    private final List<Appender> appenders;

    public CompositeAppender(String name) {
        this.name = name;
        this.appenders = new ArrayList<>();
    }

    public CompositeAppender(String name, List<Appender> appenders) {
        this.name = name;
        this.appenders = new ArrayList<>(appenders);
    }

    public void addAppender(Appender appender) {
        this.appenders.add(appender);
    }

    @Override
    public void append(LogEvent event) {
        for (Appender appender : appenders) {
            appender.append(event);
        }
    }

    @Override
    public String getName() {
        return name;
    }
}
