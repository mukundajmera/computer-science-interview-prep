import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class RelationalQueryEngineTest {

    @Test
    public void testInsertAndSelect() {
        RelationalQueryEngine db = new RelationalQueryEngine();
        RelationalQueryEngine.Table users = new RelationalQueryEngine.Table("users", Arrays.asList(
            new RelationalQueryEngine.Column("id", Integer.class, true, true),
            new RelationalQueryEngine.Column("name", String.class, false, false),
            new RelationalQueryEngine.Column("age", Integer.class, false, false)
        ));
        db.createTable(users);

        Map<String, Object> u1 = new HashMap<>();
        u1.put("id", 1); u1.put("name", "Alice"); u1.put("age", 30);
        db.insert("users", u1);

        Map<String, Object> u2 = new HashMap<>();
        u2.put("id", 2); u2.put("name", "Bob"); u2.put("age", 25);
        db.insert("users", u2);

        List<Map<String, Object>> allUsers = db.select("users", null);
        assertEquals(2, allUsers.size());

        List<Map<String, Object>> bobs = db.select("users", r -> "Bob".equals(r.get("name")));
        assertEquals(1, bobs.size());
        assertEquals(25, bobs.get(0).get("age"));
    }

    @Test
    public void testConstraintsValidation() {
        RelationalQueryEngine db = new RelationalQueryEngine();
        RelationalQueryEngine.Table users = new RelationalQueryEngine.Table("users", Arrays.asList(
            new RelationalQueryEngine.Column("id", Integer.class, true, true),
            new RelationalQueryEngine.Column("email", String.class, false, true)
        ));
        db.createTable(users);

        // Missing PK
        Map<String, Object> u1 = new HashMap<>();
        u1.put("email", "alice@example.com");
        assertThrows(IllegalArgumentException.class, () -> db.insert("users", u1));

        // Type mismatch
        Map<String, Object> u2 = new HashMap<>();
        u2.put("id", "1"); // String instead of Integer
        u2.put("email", "alice@example.com");
        assertThrows(IllegalArgumentException.class, () -> db.insert("users", u2));

        Map<String, Object> u3 = new HashMap<>();
        u3.put("id", 1);
        u3.put("email", "alice@example.com");
        db.insert("users", u3);

        // Unique constraint violation
        Map<String, Object> u4 = new HashMap<>();
        u4.put("id", 2);
        u4.put("email", "alice@example.com");
        assertThrows(IllegalArgumentException.class, () -> db.insert("users", u4));

        // PK constraint violation
        Map<String, Object> u5 = new HashMap<>();
        u5.put("id", 1);
        u5.put("email", "bob@example.com");
        assertThrows(IllegalArgumentException.class, () -> db.insert("users", u5));
    }

    @Test
    public void testUpdateAndDelete() {
        RelationalQueryEngine db = new RelationalQueryEngine();
        RelationalQueryEngine.Table users = new RelationalQueryEngine.Table("users", Arrays.asList(
            new RelationalQueryEngine.Column("id", Integer.class, true, true),
            new RelationalQueryEngine.Column("status", String.class, false, false)
        ));
        db.createTable(users);

        Map<String, Object> u1 = new HashMap<>();
        u1.put("id", 1); u1.put("status", "active");
        db.insert("users", u1);

        Map<String, Object> u2 = new HashMap<>();
        u2.put("id", 2); u2.put("status", "inactive");
        db.insert("users", u2);

        // Update
        Map<String, Object> updates = new HashMap<>();
        updates.put("status", "active");
        db.update("users", r -> Integer.valueOf(2).equals(r.get("id")), updates);

        List<Map<String, Object>> updatedUser = db.select("users", r -> Integer.valueOf(2).equals(r.get("id")));
        assertEquals("active", updatedUser.get(0).get("status"));

        // Delete
        db.delete("users", r -> Integer.valueOf(1).equals(r.get("id")));
        List<Map<String, Object>> allUsers = db.select("users", null);
        assertEquals(1, allUsers.size());
        assertEquals(2, allUsers.get(0).get("id"));
    }

    @Test
    public void testInnerJoinAndGroupBy() {
        RelationalQueryEngine db = new RelationalQueryEngine();
        RelationalQueryEngine.Table users = new RelationalQueryEngine.Table("users", Arrays.asList(
            new RelationalQueryEngine.Column("id", Integer.class, true, true),
            new RelationalQueryEngine.Column("department", String.class, false, false)
        ));
        db.createTable(users);

        RelationalQueryEngine.Table orders = new RelationalQueryEngine.Table("orders", Arrays.asList(
            new RelationalQueryEngine.Column("id", Integer.class, true, true),
            new RelationalQueryEngine.Column("user_id", Integer.class, false, false),
            new RelationalQueryEngine.Column("amount", Double.class, false, false)
        ));
        db.createTable(orders);

        Map<String, Object> u1 = new HashMap<>(); u1.put("id", 1); u1.put("department", "Sales"); db.insert("users", u1);
        Map<String, Object> u2 = new HashMap<>(); u2.put("id", 2); u2.put("department", "Marketing"); db.insert("users", u2);

        Map<String, Object> o1 = new HashMap<>(); o1.put("id", 101); o1.put("user_id", 1); o1.put("amount", 100.0); db.insert("orders", o1);
        Map<String, Object> o2 = new HashMap<>(); o2.put("id", 102); o2.put("user_id", 1); o2.put("amount", 250.0); db.insert("orders", o2);
        Map<String, Object> o3 = new HashMap<>(); o3.put("id", 103); o3.put("user_id", 2); o3.put("amount", 50.0); db.insert("orders", o3);

        // Join
        List<Map<String, Object>> joined = db.innerJoin("users", "orders",
            (u, o) -> Objects.equals(u.get("id"), o.get("user_id")), null);

        assertEquals(3, joined.size());
        assertEquals("Sales", joined.get(0).get("users.department"));
        assertEquals(100.0, joined.get(0).get("orders.amount"));

        // Group by COUNT
        List<Map<String, Object>> countGrouped = db.groupBy("orders", Arrays.asList("user_id"), "id", "COUNT");
        assertEquals(2, countGrouped.size());
        for (Map<String, Object> row : countGrouped) {
            if (Integer.valueOf(1).equals(row.get("user_id"))) {
                assertEquals(2, row.get("COUNT(id)"));
            } else if (Integer.valueOf(2).equals(row.get("user_id"))) {
                assertEquals(1, row.get("COUNT(id)"));
            }
        }

        // Group by SUM
        List<Map<String, Object>> sumGrouped = db.groupBy("orders", Arrays.asList("user_id"), "amount", "SUM");
        for (Map<String, Object> row : sumGrouped) {
            if (Integer.valueOf(1).equals(row.get("user_id"))) {
                assertEquals(350.0, row.get("SUM(amount)"));
            } else if (Integer.valueOf(2).equals(row.get("user_id"))) {
                assertEquals(50.0, row.get("SUM(amount)"));
            }
        }
    }
}
