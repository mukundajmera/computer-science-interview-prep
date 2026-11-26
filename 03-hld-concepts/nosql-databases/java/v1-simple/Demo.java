import java.io.IOException;
import java.util.List;
import java.util.Map;

public class Demo {
    public static void main(String[] args) throws IOException {
        String dataDir = "demo_lsm_data";

        System.out.println("Starting LSM-Tree KeyStore Demo...");
        LsmKeyStore store = new LsmKeyStore(3, dataDir);

        // 1. Put and Get
        System.out.println("\n--- Basic Operations ---");
        store.put("user1", "Alice");
        store.put("user2", "Bob");
        System.out.println("Get user1: " + store.get("user1"));
        System.out.println("Get user2: " + store.get("user2"));
        System.out.println("Get missing user3: " + store.get("user3"));

        // 2. Triggering an SSTable Flush
        System.out.println("\n--- SSTable Flush ---");
        System.out.println("Putting user3 to trigger memtable flush (threshold=3).");
        store.put("user3", "Charlie");
        // Memtable should now be empty and 1 SSTable should be created
        System.out.println("Get user3 after flush: " + store.get("user3"));

        // 3. Scan Operation
        System.out.println("\n--- Range Scan ---");
        store.put("user4", "David");
        store.put("user5", "Eve");
        System.out.println("Scanning from user2 to user4:");
        List<Map.Entry<String, String>> results = store.scan("user2", "user4");
        for (Map.Entry<String, String> entry : results) {
            System.out.println("  " + entry.getKey() + " -> " + entry.getValue());
        }

        // 4. Delete Operation
        System.out.println("\n--- Delete Operation ---");
        store.delete("user4");
        System.out.println("Get user4 after delete: " + store.get("user4"));

        System.out.println("\nDemo completed. Data stored in: " + dataDir);
    }
}
