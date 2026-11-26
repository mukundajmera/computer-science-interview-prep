import java.util.List;

public class Demo {
    public static void main(String[] args) throws Exception {
        System.out.println("Starting WriteBatcher demo...");

        // Demo 1: Batch size flush
        try (WriteBatcher<String> batcher = new WriteBatcher<>(10, 3, 5000, Demo::commitBatch)) {
            System.out.println("\nDemo 1: Flushing by batch size threshold (3)");
            batcher.write("msg1");
            batcher.write("msg2");
            System.out.println("Written 2 messages, waiting...");
            Thread.sleep(100);

            batcher.write("msg3");
            System.out.println("Written 3rd message, should flush now.");
            Thread.sleep(100);
        }

        // Demo 2: Time-based flush
        try (WriteBatcher<String> batcher = new WriteBatcher<>(10, 5, 1000, Demo::commitBatch)) {
            System.out.println("\nDemo 2: Flushing by wait duration (1000ms)");
            batcher.write("msg_time1");
            batcher.write("msg_time2");
            System.out.println("Written 2 messages, waiting for timeout...");
            Thread.sleep(1200); // Wait longer than 1000ms
        }

        // Demo 3: Capacity Backpressure
        try (WriteBatcher<String> batcher = new WriteBatcher<>(2, 5, 5000, Demo::commitBatch)) {
            System.out.println("\nDemo 3: Backpressure on full buffer (capacity 2)");
            System.out.println("Write 1: " + batcher.write("backpressure1"));
            System.out.println("Write 2: " + batcher.write("backpressure2"));
            System.out.println("Write 3 (should fail): " + batcher.write("backpressure3"));
            Thread.sleep(100);
        }
    }

    private static void commitBatch(List<String> batch) {
        System.out.println("Committed batch of " + batch.size() + " items: " + batch);
    }
}
