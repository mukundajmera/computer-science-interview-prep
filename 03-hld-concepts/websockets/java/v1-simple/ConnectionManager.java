import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Simple WebSocket-style connection manager simulation. */
public class ConnectionManager {
    private final Map<String, List<String>> rooms = new HashMap<>();

    public void connect(String room, String clientId) {
        List<String> clients = rooms.computeIfAbsent(room, ignored -> new ArrayList<>());
        if (!clients.contains(clientId)) {
            clients.add(clientId);
        }
    }

    public void disconnect(String room, String clientId) {
        List<String> clients = rooms.get(room);
        if (clients != null) {
            clients.remove(clientId);
            if (clients.isEmpty()) {
                rooms.remove(room);
            }
        }
    }

    public List<String> broadcastTargets(String room) {
        return new ArrayList<>(rooms.getOrDefault(room, List.of()));
    }
}
