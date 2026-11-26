import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class V1Tests {
    @Test
    public void testDispatch() {
        Dispatcher dispatcher = new Dispatcher();
        Notification n = new Notification("u1", "msg", "EMAIL");
        assertTrue(dispatcher.dispatch(n));
    }

    @Test
    public void testNotificationServiceV1() throws InterruptedException {
        Dispatcher dispatcher = new Dispatcher();
        NotificationService service = new NotificationService(dispatcher, 2, 1);
        
        // Test idempotency
        assertEquals(NotificationService.IntentState.PENDING, service.submitIntent("PROMO", "u1", "EMAIL", "msg1"));
        assertEquals(NotificationService.IntentState.CONFLICT, service.submitIntent("PROMO", "u1", "EMAIL", "msg1"));
        
        // Test unsubscribe
        service.unsubscribe("u2");
        assertEquals(NotificationService.IntentState.FAILED, service.submitIntent("PROMO", "u2", "EMAIL", "msg2"));
        
        // Test queue overflow
        NotificationService serviceSmall = new NotificationService(dispatcher, 0, 0);
        assertEquals(NotificationService.IntentState.FAILED, serviceSmall.submitIntent("PROMO", "u3", "EMAIL", "msg"));
        
        // Test fake provider timeout (hanging) doesn't block main thread
        Dispatcher hangingDispatcher = new Dispatcher();
        hangingDispatcher.setChannel("HANG", new Channel() {
            @Override
            public boolean send(Notification n) {
                try { Thread.sleep(5000); } catch (InterruptedException e) {}
                return false;
            }
        });
        NotificationService serviceHanging = new NotificationService(hangingDispatcher, 10, 0);
        long start = System.currentTimeMillis();
        assertEquals(NotificationService.IntentState.PENDING, serviceHanging.submitIntent("ALERT", "u4", "HANG", "msg"));
        long duration = System.currentTimeMillis() - start;
        assertTrue(duration < 1000, "Main thread should not block");
    }
}
