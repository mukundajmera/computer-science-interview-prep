import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class ConnectionManagerTest {
    @Test
    void shouldAddAndRemoveConnections() {
        ConnectionManager manager = new ConnectionManager();
        manager.connect("room", "u1");
        assertEquals(1, manager.broadcastTargets("room").size());
        manager.disconnect("room", "u1");
        assertEquals(0, manager.broadcastTargets("room").size());
    }

    @Test
    void duplicateConnectionsShouldNotDuplicateBroadcastTargets() {
        ConnectionManager manager = new ConnectionManager();
        manager.connect("room", "u1");
        manager.connect("room", "u1");
        assertEquals(java.util.List.of("u1"), manager.broadcastTargets("room"));
    }

    @Test
    void broadcastTargetsShouldReturnAnIndependentSnapshot() {
        ConnectionManager manager = new ConnectionManager();
        manager.connect("room", "u1");
        java.util.List<String> targets = manager.broadcastTargets("room");
        manager.disconnect("room", "u1");
        assertEquals(java.util.List.of("u1"), targets);
        assertEquals(java.util.List.of(), manager.broadcastTargets("room"));
    }
}
