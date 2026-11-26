import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class DynamoDbConceptTest {
    @Test
    @DisplayName("put and get should return exact item")
    void testPutAndGet() {
        SimpleDynamoTable table = new SimpleDynamoTable();
        table.putItem("chat-1", "0001", Map.of("message", "hello", "user", "u1"));

        SimpleDynamoTable.Item item = table.getItem("chat-1", "0001");
        assertNotNull(item);
        assertEquals("hello", item.attributes.get("message"));
    }

    @Test
    @DisplayName("query range should return sorted subset")
    void testRangeQuery() {
        SimpleDynamoTable table = new SimpleDynamoTable();
        table.putItem("chat-1", "0001", Map.of("message", "a"));
        table.putItem("chat-1", "0002", Map.of("message", "b"));
        table.putItem("chat-1", "0003", Map.of("message", "c"));

        List<SimpleDynamoTable.Item> items = table.queryRange("chat-1", "0002", "0003");
        assertEquals(2, items.size());
        assertEquals("0002", items.get(0).sortKey);
    }

    @Test
    @DisplayName("GSI query should return matching items")
    void testGsiQuery() {
        SimpleDynamoTable table = new SimpleDynamoTable();
        table.defineGsi("user-index", "user", "ts");

        table.putItem("chat-1", "0001", Map.of("user", "u1", "ts", "2026-01-01T10:00:00Z"));
        table.putItem("chat-2", "0001", Map.of("user", "u1", "ts", "2026-01-01T11:00:00Z"));
        table.putItem("chat-2", "0002", Map.of("user", "u2", "ts", "2026-01-01T12:00:00Z"));

        List<SimpleDynamoTable.Item> results = table.queryGsi("user-index", "u1");
        assertEquals(2, results.size());
    }

    @Test
    @DisplayName("scan should paginate deterministically")
    void testScanPagination() {
        SimpleDynamoTable table = new SimpleDynamoTable();
        table.putItem("chat-1", "0001", Map.of("x", 1));
        table.putItem("chat-1", "0002", Map.of("x", 2));
        table.putItem("chat-1", "0003", Map.of("x", 3));

        List<SimpleDynamoTable.Item> page = table.scan(2, 1);
        assertEquals(2, page.size());
    }
}
