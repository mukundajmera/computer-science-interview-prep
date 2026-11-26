import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class V2Tests {
    @Test
    public void testPriority() {
        Dispatcher dispatcher = new Dispatcher(10);
        Notification n1 = new Notification("u1", "low", "EMAIL", 2);
        Notification n2 = new Notification("u2", "high", "EMAIL", 1);
        
        dispatcher.enqueue(n1);
        dispatcher.enqueue(n2);
        
        assertEquals("u2", dispatcher.peekQueue().getUserId());
    }
    
    @Test
    public void testRateLimit() {
        Dispatcher dispatcher = new Dispatcher(1);
        Notification n1 = new Notification("u1", "msg1", "EMAIL", 1);
        Notification n2 = new Notification("u2", "msg2", "EMAIL", 1);
        
        dispatcher.enqueue(n1);
        dispatcher.enqueue(n2);
        
        assertTrue(dispatcher.processOne());
        assertFalse(dispatcher.processOne()); // Hits rate limit
    }

    @Test
    public void testNotificationServiceV2() throws InterruptedException {
        Dispatcher dispatcher = new Dispatcher(100);
        NotificationService service = new NotificationService(dispatcher, 2, 1);
        
        // Test idempotency
        assertEquals(NotificationService.IntentState.PENDING, service.submitIntent("PROMO", "u1", "EMAIL", "msg1", 1));
        assertEquals(NotificationService.IntentState.CONFLICT, service.submitIntent("PROMO", "u1", "EMAIL", "msg1", 1));
        
        // Test unsubscribe
        service.unsubscribe("u2");
        assertEquals(NotificationService.IntentState.FAILED, service.submitIntent("PROMO", "u2", "EMAIL", "msg2", 1));
        
        // Test queue overflow
        NotificationService serviceSmall = new NotificationService(dispatcher, 0, 0);
        assertEquals(NotificationService.IntentState.FAILED, serviceSmall.submitIntent("PROMO", "u3", "EMAIL", "msg", 1));
        
        // Test fake provider timeout (hanging) doesn't block main thread
        Dispatcher hangingDispatcher = new Dispatcher(100);
        NotificationService serviceHanging = new NotificationService(hangingDispatcher, 10, 0);
        
        serviceHanging.wrapChannel("HANG", new Channel() {
            @Override
            public boolean send(Notification n) {
                try { Thread.sleep(5000); } catch (InterruptedException e) {}
                return false;
            }
        });
        
        long start = System.currentTimeMillis();
        assertEquals(NotificationService.IntentState.PENDING, serviceHanging.submitIntent("ALERT", "u4", "HANG", "msg", 1));
        long duration = System.currentTimeMillis() - start;
        assertTrue(duration < 1000, "Main thread should not block");
        
        service.shutdown();
        serviceSmall.shutdown();
        serviceHanging.shutdown();
    }
}
