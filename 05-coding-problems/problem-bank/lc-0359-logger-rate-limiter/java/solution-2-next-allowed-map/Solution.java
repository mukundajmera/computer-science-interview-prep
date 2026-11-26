import java.util.HashMap;
import java.util.Map;

class Logger {
    private final Map<String, Integer> nextAllowed = new HashMap<>();
    public boolean shouldPrintMessage(int timestamp, String message) {
        if (timestamp < nextAllowed.getOrDefault(message, 0)) return false;
        nextAllowed.put(message, timestamp + 10);
        return true;
    }
}
