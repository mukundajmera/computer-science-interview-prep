import java.util.*;

public class Demo {
    public static void main(String[] args) {
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
        System.out.println("All users: " + allUsers);

        List<Map<String, Object>> bobs = db.select("users", r -> "Bob".equals(r.get("name")));
        System.out.println("Bobs: " + bobs);
    }
}
