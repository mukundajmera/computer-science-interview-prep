import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;

import v3.Node;
import v3.ShardedClient;

public class ShardedClientTest {
    @Test
    public void testBasicSetGet() {
        Node node1 = new Node("node1", "localhost", 6379);
        Node node2 = new Node("node2", "localhost", 6380);
        ShardedClient client = new ShardedClient(Arrays.asList(node1, node2));

        ShardedClient.Result res1 = client.executeCommand("SET", "key1", "val1", null);
        assertEquals("OK", res1.value);

        ShardedClient.Result res2 = client.executeCommand("GET", "key1", null, null);
        assertEquals("val1", res2.value);
    }

    @Test
    public void testHashTags() {
        Node node1 = new Node("node1", "localhost", 6379);
        ShardedClient client = new ShardedClient(Arrays.asList(node1));

        int slot1 = client.getHashSlot("{user:123}:profile");
        int slot2 = client.getHashSlot("{user:123}:settings");
        assertEquals(slot1, slot2);
    }

    @Test
    public void testHotKeyCache() {
        Node node1 = new Node("node1", "localhost", 6379);
        ShardedClient client = new ShardedClient(Arrays.asList(node1));

        client.executeCommand("SET", "hot", "val", null);
        for (int i = 0; i < 6; i++) {
            client.executeCommand("GET", "hot", null, null);
        }

        ShardedClient.Result res = client.executeCommand("GET", "hot", null, null);
        assertEquals("val", res.value); // Should be from cache internally
    }
    
    @Test
    public void testRedirectMoved() {
        Node node1 = new Node("node1", "localhost", 6379);
        Node node2 = new Node("node2", "localhost", 6380);
        ShardedClient client = new ShardedClient(Arrays.asList(node1, node2));

        String key = "testkey1";
        int slot = client.getHashSlot(key);
        
        // Find correct node
        String correctNodeId = slot % 2 == 0 ? "node1" : "node2";
        String wrongNodeId = correctNodeId.equals("node1") ? "node2" : "node1";
        
        ShardedClient.Result res1 = client.executeCommand("SET", key, "val", wrongNodeId);
        assertNull(res1.value);
        assertTrue(res1.error.startsWith("MOVED " + slot));
        
        ShardedClient.Result res2 = client.executeCommand("SET", key, "val", correctNodeId);
        assertEquals("OK", res2.value);
    }
}
