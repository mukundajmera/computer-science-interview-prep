import java.util.HashMap;
import java.util.Map;

public class Demo {
    public static void main(String[] args) {
        InnoDBEngineSimulator engine = new InnoDBEngineSimulator();

        System.out.println("Starting Transaction 1");
        int tx1 = engine.startTransaction();

        Map<String, Object> data = new HashMap<>();
        data.put("name", "Alice");
        data.put("balance", 100);

        engine.write(tx1, 1, data);
        engine.commit(tx1);
        System.out.println("Transaction 1 committed. Data: " + engine.read(tx1, 1));

        System.out.println("Starting Transaction 2");
        int tx2 = engine.startTransaction();
        System.out.println("Transaction 2 sees: " + engine.read(tx2, 1));

        System.out.println("Starting Transaction 3");
        int tx3 = engine.startTransaction();

        Map<String, Object> update = new HashMap<>();
        update.put("name", "Alice");
        update.put("balance", 200);

        engine.write(tx3, 1, update);

        System.out.println("Transaction 2 sees (Snapshot): " + engine.read(tx2, 1));
        System.out.println("Transaction 3 sees (Own Write): " + engine.read(tx3, 1));

        engine.commit(tx3);
        System.out.println("Transaction 3 committed.");

        System.out.println("Transaction 2 still sees (Snapshot Isolation): " + engine.read(tx2, 1));
        engine.commit(tx2);
    }
}
