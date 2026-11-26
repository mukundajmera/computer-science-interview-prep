import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class CassandraConceptTest {
    @Test
    @DisplayName("upsert and get should return stored row")
    void testUpsertAndGet() {
        SimpleCassandraTable table = new SimpleCassandraTable();
        Map<String, Object> columns = new HashMap<>();
        columns.put("event", "login");

        table.upsert("user-1", 1001L, columns);

        SimpleCassandraTable.Row row = table.get("user-1", 1001L);
        assertNotNull(row);
        assertEquals("login", row.columns.get("event"));
    }

    @Test
    @DisplayName("queryPartition should return clustering-key order")
    void testPartitionOrdering() {
        SimpleCassandraTable table = new SimpleCassandraTable();
        table.upsert("user-1", 3L, Map.of("event", "c"));
        table.upsert("user-1", 1L, Map.of("event", "a"));
        table.upsert("user-1", 2L, Map.of("event", "b"));

        List<SimpleCassandraTable.Row> rows = table.queryPartition("user-1");
        assertEquals(3, rows.size());
        assertEquals(1L, rows.get(0).clusteringKey);
        assertEquals(3L, rows.get(2).clusteringKey);
    }

    @Test
    @DisplayName("range query should include only requested keys")
    void testRangeQuery() {
        SimpleCassandraTable table = new SimpleCassandraTable();
        table.upsert("order-1", 10L, Map.of("status", "created"));
        table.upsert("order-1", 20L, Map.of("status", "packed"));
        table.upsert("order-1", 30L, Map.of("status", "shipped"));

        List<SimpleCassandraTable.Row> rows = table.queryRange("order-1", 15L, 30L);
        assertEquals(2, rows.size());
    }

    @Test
    @DisplayName("consistency setter should reject unsupported level")
    void testConsistencyLevel() {
        SimpleCassandraTable table = new SimpleCassandraTable();
        table.setReadConsistency(SimpleCassandraTable.ConsistencyLevel.ONE);
        assertEquals(SimpleCassandraTable.ConsistencyLevel.ONE, table.getReadConsistency());
    }
}
