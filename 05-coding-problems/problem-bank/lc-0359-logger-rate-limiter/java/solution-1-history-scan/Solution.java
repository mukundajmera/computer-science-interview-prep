import java.util.ArrayList;
import java.util.List;

class Logger {
    private static class Event { int timestamp; String message; Event(int t, String m) { timestamp = t; message = m; } }
    private final List<Event> events = new ArrayList<>();
    public boolean shouldPrintMessage(int timestamp, String message) {
        for (int i = events.size() - 1; i >= 0; i--) {
            Event event = events.get(i);
            if (timestamp - event.timestamp >= 10) break;
            if (event.message.equals(message)) return false;
        }
        events.add(new Event(timestamp, message));
        return true;
    }
}
