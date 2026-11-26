
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.List;
import java.util.ArrayList;


public class WebhookDispatcherV3Test {

    public static void main(String[] args) {
        int passed = 0;
        int failed = 0;

        try { testV3CircuitBreakerTripAndRecover(); passed++; } catch (Exception e) { System.err.println("Test failed: testV3CircuitBreakerTripAndRecover - " + e.getMessage()); e.printStackTrace(); failed++; }
        try { testV3FullJitterBackoff(); passed++; } catch (Exception e) { System.err.println("Test failed: testV3FullJitterBackoff - " + e.getMessage()); failed++; }
        try { testV3DlqCaptureAndReplay(); passed++; } catch (Exception e) { System.err.println("Test failed: testV3DlqCaptureAndReplay - " + e.getMessage()); failed++; }
        try { testV3DlqRetentionAndFormat(); passed++; } catch (Exception e) { System.err.println("Test failed: testV3DlqRetentionAndFormat - " + e.getMessage()); failed++; }

        System.out.println("Tests passed: " + passed);
        System.out.println("Tests failed: " + failed);
        
        if (failed > 0) {
            System.exit(1);
        }
    }

    static class MockHttpClient implements HttpClient {
        final List<Object[]> calls = new ArrayList<>();
        int failCount = 0;
        int failStatus = 500;

        @Override
        public synchronized DeliveryResult post(String url, String data, Map<String, String> headers) {
            calls.add(new Object[]{url, data, headers});
            if (failCount > 0) {
                failCount--;
                return new DeliveryResult(failStatus, false);
            }
            return new DeliveryResult(200, true);
        }
    }

    private static void testV3CircuitBreakerTripAndRecover() throws Exception {
        MockHttpClient client = new MockHttpClient();
        client.failCount = 5;
        
        WebhookDispatcher dispatcher = new WebhookDispatcher(client, 2, 5, Map.of());
        Subscriber sub = new Subscriber("sub1", "http://example.com/cb", "secret", "cb.*");
        dispatcher.addSubscriber(sub);
        CircuitBreaker cb = dispatcher.getCircuitBreaker(sub.getEndpoint());
        
        // Reflection to set a shorter cooldown for testing
        java.lang.reflect.Field cooldownField = CircuitBreaker.class.getDeclaredField("cooldownMs");
        cooldownField.setAccessible(true);
        cooldownField.set(cb, 1000L);
        
        for (int i = 0; i < 5; i++) {
            dispatcher.publish(new Event("cb.test", Map.of("id", i)));
            Thread.sleep(100);
        }
        
        Thread.sleep(500);
        
        if (cb.getState() != CircuitBreaker.State.OPEN) {
            throw new RuntimeException("Expected CircuitBreaker to be OPEN, but was " + cb.getState());
        }
        
        Thread.sleep(1500); // wait for cooldown
        
        dispatcher.publish(new Event("cb.test", Map.of("id", 6)));
        Thread.sleep(1000);
        
        if (cb.getState() != CircuitBreaker.State.CLOSED) {
            throw new RuntimeException("Expected CircuitBreaker to be CLOSED, but was " + cb.getState());
        }
        
        synchronized(client) {
            if (client.calls.size() <= 0) {
                throw new RuntimeException("Expected at least 1 successful call after recovery");
            }
        }
        
        dispatcher.stop();
    }

    private static void testV3FullJitterBackoff() throws Exception {
        MockHttpClient client = new MockHttpClient();
        client.failCount = 100;
        
        WebhookDispatcher dispatcher = new WebhookDispatcher(client, 1, 5, Map.of());
        Subscriber sub = new Subscriber("sub1", "http://example.com/jitter", "secret", "jitter.*");
        dispatcher.addSubscriber(sub);
        
        dispatcher.publish(new Event("jitter.test", Map.of()));
        
        Thread.sleep(2000); // Wait for some retries
        
        synchronized(client) {
            if (client.calls.size() <= 1) {
                throw new RuntimeException("Expected retries to happen, got " + client.calls.size() + " calls");
            }
        }
        
        dispatcher.stop();
    }

    private static void testV3DlqCaptureAndReplay() throws Exception {
        MockHttpClient client = new MockHttpClient();
        client.failCount = 100; // Always fail
        
        WebhookDispatcher dispatcher = new WebhookDispatcher(client, 2, 5, Map.of());
        Subscriber sub = new Subscriber("sub1", "http://example.com/dlq", "secret", "dlq.*");
        dispatcher.addSubscriber(sub);
        
        Event event = new Event("dlq.test", Map.of("id", 1));
        WebhookTask task = new WebhookTask(event, sub, dispatcher);
        task.setAttempt(6); // Force it to go to DLQ
        
        task.handleFailure(dispatcher.getCircuitBreaker(sub.getEndpoint()));
        
        List<WebhookTask> items = dispatcher.getDlq().getItems();
        if (items.size() != 1) throw new RuntimeException("Expected 1 item in DLQ");
        if (!items.get(0).getEvent().getTopic().equals("dlq.test")) throw new RuntimeException("Wrong event in DLQ");
        
        client.failCount = 0; // Fix client
        
        dispatcher.replayDlq();
        
        if (dispatcher.getDlq().getItems().size() != 0) throw new RuntimeException("DLQ should be empty after replay");
        
        Thread.sleep(500); // wait for replay to process
        
        synchronized(client) {
            if (client.calls.size() != 1) {
                throw new RuntimeException("Expected 1 call after replay, got " + client.calls.size());
            }
        }
        
        dispatcher.stop();
    }

    private static void testV3DlqRetentionAndFormat() throws Exception {
        PersistentDlq dlq = new PersistentDlq(7);
        Subscriber sub = new Subscriber("sub1", "http://test.com", "secret", "topic.*");
        WebhookTask task = new WebhookTask(new Event("topic.a", Map.of()), sub, null);
        
        dlq.add(task);
        List<WebhookTask> items = dlq.getItems();
        
        if (items.size() != 1) throw new RuntimeException("Expected 1 item");
        if (items.get(0) != task) throw new RuntimeException("Task mismatch");
        if (dlq.getRetentionDays() != 7) throw new RuntimeException("Retention mismatch");
    }
}
