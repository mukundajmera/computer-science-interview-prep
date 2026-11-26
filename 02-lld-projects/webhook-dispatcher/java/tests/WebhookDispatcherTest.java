import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

class MockHttpClient implements HttpClient {
    private final List<Object[]> calls = new ArrayList<>();
    private int failCount = 0;

    public void setFailCount(int failCount) {
        this.failCount = failCount;
    }

    public List<Object[]> getCalls() {
        synchronized(calls) {
            return new ArrayList<>(calls);
        }
    }

    @Override
    public DeliveryResult post(String url, String data, Map<String, String> headers) {
        synchronized(calls) {
            calls.add(new Object[]{url, data, headers});
            if (failCount > 0) {
                failCount--;
                return new DeliveryResult(500, false);
            }
        }
        return new DeliveryResult(200, true);
    }
}

class DelayHttpClient implements HttpClient {
    private AtomicInteger concurrentRequests = new AtomicInteger(0);
    private AtomicInteger maxObserved = new AtomicInteger(0);
    private AtomicInteger calls = new AtomicInteger(0);

    @Override
    public DeliveryResult post(String url, String data, Map<String, String> headers) {
        int current = concurrentRequests.incrementAndGet();
        updateMax(current);

        try {
            Thread.sleep(200);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        concurrentRequests.decrementAndGet();
        calls.incrementAndGet();

        return new DeliveryResult(200, true);
    }

    private synchronized void updateMax(int current) {
        if (current > maxObserved.get()) {
            maxObserved.set(current);
        }
    }

    public int getMaxObserved() { return maxObserved.get(); }
    public int getCalls() { return calls.get(); }
}

public class WebhookDispatcherTest {
    private WebhookDispatcher dispatcher;
    private MockHttpClient client;

    @BeforeEach
    void setUp() {
        client = new MockHttpClient();
        dispatcher = new WebhookDispatcher(client, 4, 5);
    }

    @AfterEach
    void tearDown() {
        if (dispatcher != null) {
            dispatcher.stop();
        }
    }

    @Test
    void testFastPathDeliveryAndHmac() throws InterruptedException {
        Subscriber sub = new Subscriber("sub1", "http://example.com/webhook", "mysecret", "order.*");
        dispatcher.addSubscriber(sub);

        Event event = new Event("order.created", Map.of("order_id", 123));
        dispatcher.publish(event);

        Thread.sleep(500);

        List<Object[]> calls = client.getCalls();
        assertEquals(1, calls.size());
        assertEquals("http://example.com/webhook", calls.get(0)[0]);
        assertTrue(((String) calls.get(0)[1]).contains("\"order_id\":123"));

        @SuppressWarnings("unchecked")
        Map<String, String> headers = (Map<String, String>) calls.get(0)[2];
        assertTrue(headers.containsKey("X-Hub-Signature-256"));
        assertTrue(headers.get("X-Hub-Signature-256").startsWith("sha256="));
    }

    @Test
    void testRetryBackoffAndDlq() throws InterruptedException {
        client.setFailCount(10); // Ensure all retries fail
        Subscriber sub = new Subscriber("sub1", "http://example.com/fail", "secret", "user.*");
        dispatcher.addSubscriber(sub);

        Event event = new Event("user.created", Map.of("user_id", 1));
        dispatcher.publish(event);

        // Max retries = 3. Base delay = 100ms. Total max wait ~1.4s
        Thread.sleep(2000);

        List<Object[]> calls = client.getCalls();
        assertEquals(4, calls.size()); // Initial + 3 retries

        List<WebhookTask> dlq = dispatcher.getDlq();
        assertEquals(1, dlq.size());
        assertEquals(4, dlq.get(0).getAttempt());
        assertEquals("user.created", dlq.get(0).getEvent().getTopic());
    }

    @Test
    void testPerDestinationConcurrencyLimits() throws InterruptedException {
        DelayHttpClient delayClient = new DelayHttpClient();
        // Limit to 3 concurrent requests per destination
        WebhookDispatcher delayDispatcher = new WebhookDispatcher(delayClient, 10, 3);
        Subscriber sub = new Subscriber("sub1", "http://slow.com/hook", "secret", "batch.*");
        delayDispatcher.addSubscriber(sub);

        for (int i = 0; i < 10; i++) {
            delayDispatcher.publish(new Event("batch." + i, Map.of("id", i)));
        }

        Thread.sleep(3000);
        delayDispatcher.stop();

        assertEquals(10, delayClient.getCalls());
        assertTrue(delayClient.getMaxObserved() <= 3, "Observed concurrency should be <= 3");
        assertTrue(delayClient.getMaxObserved() > 0);
    }

    @Test
    void testMultipleSubscribers() throws InterruptedException {
        dispatcher.addSubscriber(new Subscriber("sub1", "http://sub1.com", "secret", "event.*"));
        dispatcher.addSubscriber(new Subscriber("sub2", "http://sub2.com", "secret", "event.specific"));
        dispatcher.addSubscriber(new Subscriber("sub3", "http://sub3.com", "secret", "other.*"));

        dispatcher.publish(new Event("event.specific", Map.of("val", 1)));

        Thread.sleep(500);

        List<Object[]> calls = client.getCalls();
        assertEquals(2, calls.size());
        
        List<String> urls = new ArrayList<>();
        for (Object[] call : calls) {
            urls.add((String) call[0]);
        }
        assertTrue(urls.contains("http://sub1.com"));
        assertTrue(urls.contains("http://sub2.com"));
        assertFalse(urls.contains("http://sub3.com"));
    }

    @Test
    void testNoMatchTopic() throws InterruptedException {
        Subscriber sub = new Subscriber("sub_nomatch", "http://example.com/nomatch", "mysecret", "nomatch.*");
        dispatcher.addSubscriber(sub);
        
        Event event = new Event("user.created", Map.of("user_id", 456));
        dispatcher.publish(event);
        
        Thread.sleep(500);
        
        assertEquals(0, client.getCalls().size());
    }
}
