
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.List;
import java.util.ArrayList;


public class WebhookDispatcherV2Test {

    public static void main(String[] args) {
        int passed = 0;
        int failed = 0;

        try { testV2FastPathDeliveryAndHmac(); passed++; } catch (Exception e) { System.err.println("Test failed: testV2FastPathDeliveryAndHmac - " + e.getMessage()); failed++; }
        try { testV2SignatureVerificationReplayAttack(); passed++; } catch (Exception e) { System.err.println("Test failed: testV2SignatureVerificationReplayAttack - " + e.getMessage()); failed++; }
        try { testV2PerHostConcurrencyLimits(); passed++; } catch (Exception e) { System.err.println("Test failed: testV2PerHostConcurrencyLimits - " + e.getMessage()); e.printStackTrace(); failed++; }
        try { testV2RetryBackoffAndDlq(); passed++; } catch (Exception e) { System.err.println("Test failed: testV2RetryBackoffAndDlq - " + e.getMessage()); failed++; }

        System.out.println("Tests passed: " + passed);
        System.out.println("Tests failed: " + failed);
        
        if (failed > 0) {
            System.exit(1);
        }
    }

    static class MockHttpClient implements HttpClient {
        final List<Object[]> calls = new ArrayList<>();
        int failCount = 0;

        @Override
        public synchronized DeliveryResult post(String url, String data, Map<String, String> headers) {
            calls.add(new Object[]{url, data, headers});
            if (failCount > 0) {
                failCount--;
                return new DeliveryResult(500, false);
            }
            return new DeliveryResult(200, true);
        }
    }

    private static void testV2FastPathDeliveryAndHmac() throws Exception {
        MockHttpClient client = new MockHttpClient();
        WebhookDispatcher dispatcher = new WebhookDispatcher(client, 2, 5, Map.of());

        Subscriber sub = new Subscriber("sub1", "http://example.com/webhook", "mysecret", "order.*");
        dispatcher.addSubscriber(sub);

        Event event = new Event("order.created", Map.of("order_id", 123));
        dispatcher.publish(event);

        Thread.sleep(500);
        dispatcher.stop();

        if (client.calls.size() != 1) throw new RuntimeException("Expected 1 call");
        Map<String, String> headers = (Map<String, String>) client.calls.get(0)[2];
        if (!headers.containsKey("X-Hub-Signature-256")) throw new RuntimeException("Missing signature");
        if (!headers.containsKey("X-Webhook-Timestamp")) throw new RuntimeException("Missing timestamp");
        
        String data = (String) client.calls.get(0)[1];
        String timestamp = headers.get("X-Webhook-Timestamp");
        String signature = headers.get("X-Hub-Signature-256").replace("sha256=", "");
        
        if (!WebhookTask.verifySignature("mysecret", data, timestamp, signature, 300)) {
            throw new RuntimeException("Signature verification failed");
        }
    }

    private static void testV2SignatureVerificationReplayAttack() throws Exception {
        String secret = "mysecret";
        String payload = "{\"order_id\":123}";
        
        String oldTimestamp = String.valueOf((System.currentTimeMillis() / 1000L) - 400);
        String oldSignature = WebhookTask.generateHmacSha256(secret, payload, oldTimestamp);
        
        if (WebhookTask.verifySignature(secret, payload, oldTimestamp, oldSignature, 300)) {
            throw new RuntimeException("Should fail for old timestamp");
        }
        
        String recentTimestamp = String.valueOf((System.currentTimeMillis() / 1000L) - 100);
        String recentSignature = WebhookTask.generateHmacSha256(secret, payload, recentTimestamp);
        
        if (!WebhookTask.verifySignature(secret, payload, recentTimestamp, recentSignature, 300)) {
            throw new RuntimeException("Should pass for recent timestamp");
        }
        
        if (WebhookTask.verifySignature(secret, payload, recentTimestamp, "badsignature", 300)) {
            throw new RuntimeException("Should fail for bad signature");
        }
    }

    private static void testV2PerHostConcurrencyLimits() throws Exception {
        class DelayHttpClient implements HttpClient {
            final Map<String, AtomicInteger> concurrentRequests = new ConcurrentHashMap<>();
            final Map<String, AtomicInteger> maxObserved = new ConcurrentHashMap<>();
            int calls = 0;

            @Override
            public DeliveryResult post(String url, String data, Map<String, String> headers) {
                String host = "";
                try {
                    host = new java.net.URI(url).getHost();
                } catch (Exception e) {}
                
                concurrentRequests.putIfAbsent(host, new AtomicInteger(0));
                maxObserved.putIfAbsent(host, new AtomicInteger(0));
                
                int current = concurrentRequests.get(host).incrementAndGet();
                synchronized(maxObserved) {
                    if (current > maxObserved.get(host).get()) {
                        maxObserved.get(host).set(current);
                    }
                }
                
                try { Thread.sleep(200); } catch (InterruptedException e) {}
                
                concurrentRequests.get(host).decrementAndGet();
                synchronized(this) { calls++; }
                return new DeliveryResult(200, true);
            }
        }

        DelayHttpClient client = new DelayHttpClient();
        Map<String, Integer> hostLimits = Map.of(
            "hostA.com", 5,
            "hostB.com", 2
        );
        
        WebhookDispatcher dispatcher = new WebhookDispatcher(client, 10, 1, hostLimits);
        
        dispatcher.addSubscriber(new Subscriber("subA", "http://hostA.com/hook", "secret", "batch.*"));
        dispatcher.addSubscriber(new Subscriber("subB", "http://hostB.com/hook", "secret", "batch.*"));
        dispatcher.addSubscriber(new Subscriber("subC", "http://hostC.com/hook", "secret", "batch.*"));
        
        for (int i = 0; i < 10; i++) {
            dispatcher.publish(new Event("batch." + i, Map.of("id", i)));
        }
        
        Thread.sleep(3000);
        dispatcher.stop();
        
        if (client.calls != 30) throw new RuntimeException("Expected 30 calls, got " + client.calls);
        if (client.maxObserved.get("hostA.com").get() > 5) throw new RuntimeException("hostA limit exceeded");
        if (client.maxObserved.get("hostB.com").get() > 2) throw new RuntimeException("hostB limit exceeded");
        if (client.maxObserved.get("hostC.com").get() > 1) throw new RuntimeException("hostC limit exceeded");
    }

    private static void testV2RetryBackoffAndDlq() throws Exception {
        MockHttpClient client = new MockHttpClient();
        client.failCount = 10;
        
        WebhookDispatcher dispatcher = new WebhookDispatcher(client, 2, 5, Map.of());
        dispatcher.addSubscriber(new Subscriber("sub1", "http://example.com/fail", "secret", "user.*"));
        
        dispatcher.publish(new Event("user.created", Map.of("user_id", 1)));
        
        Thread.sleep(2000);
        dispatcher.stop();
        
        if (client.calls.size() != 4) throw new RuntimeException("Expected 4 calls (1 init + 3 retries), got " + client.calls.size());
        
        if (dispatcher.getDlq().size() != 1) throw new RuntimeException("Expected 1 item in DLQ");
        WebhookTask dlqTask = dispatcher.getDlq().get(0);
        if (!dlqTask.getEvent().getTopic().equals("user.created")) throw new RuntimeException("Wrong event in DLQ");
        if (dlqTask.getAttempt() != 4) throw new RuntimeException("Expected 4 attempts, got " + dlqTask.getAttempt());
    }
}
