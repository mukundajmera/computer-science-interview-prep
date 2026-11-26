import java.util.*;

public class Demo {
    public static void main(String[] args) {
        DocumentStoreEngine engine = new DocumentStoreEngine();

        System.out.println("Creating collection and adding documents...");
        String usersCollection = "users";

        engine.createIndex(usersCollection, "age");
        engine.createIndex(usersCollection, "address.city");

        engine.insert(usersCollection, new DocumentStoreEngine.Document()
            .append("name", "Alice")
            .append("age", 25)
            .append("address", new DocumentStoreEngine.Document().append("city", "New York").append("zip", "10001"))
            .append("hobbies", Arrays.asList(
                new DocumentStoreEngine.Document().append("name", "reading").append("frequency", "high"),
                new DocumentStoreEngine.Document().append("name", "tennis").append("frequency", "low")
            ))
        );

        engine.insert(usersCollection, new DocumentStoreEngine.Document()
            .append("name", "Bob")
            .append("age", 30)
            .append("address", new DocumentStoreEngine.Document().append("city", "San Francisco").append("zip", "94105"))
            .append("hobbies", Arrays.asList(
                new DocumentStoreEngine.Document().append("name", "gaming").append("frequency", "high")
            ))
        );

        System.out.println("\nFinding users with age > 20:");
        DocumentStoreEngine.Document query1 = new DocumentStoreEngine.Document()
            .append("age", new DocumentStoreEngine.Document().append("$gt", 20));
        List<DocumentStoreEngine.Document> results1 = engine.find(usersCollection, query1);
        System.out.println(results1);

        System.out.println("\nFinding users in New York or San Francisco:");
        DocumentStoreEngine.Document query2 = new DocumentStoreEngine.Document()
            .append("address.city", new DocumentStoreEngine.Document().append("$in", Arrays.asList("New York", "San Francisco")));
        List<DocumentStoreEngine.Document> results2 = engine.find(usersCollection, query2);
        System.out.println(results2);

        System.out.println("\nFinding users who have reading as a high-frequency hobby:");
        DocumentStoreEngine.Document query3 = new DocumentStoreEngine.Document()
            .append("hobbies", new DocumentStoreEngine.Document().append("$elemMatch",
                new DocumentStoreEngine.Document().append("name", "reading").append("frequency", "high")));
        List<DocumentStoreEngine.Document> results3 = engine.find(usersCollection, query3);
        System.out.println(results3);

        System.out.println("\nFinding Bob with projection (only name and age):");
        DocumentStoreEngine.Document query4 = new DocumentStoreEngine.Document().append("name", "Bob");
        DocumentStoreEngine.Document proj = new DocumentStoreEngine.Document().append("name", 1).append("age", 1).append("_id", 0);
        List<DocumentStoreEngine.Document> results4 = engine.find(usersCollection, query4, proj);
        System.out.println(results4);
    }
}
