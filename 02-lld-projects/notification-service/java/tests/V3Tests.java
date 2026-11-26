import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;

public class V3Tests {
    @Test
    public void testRetryWithBackoff() throws InterruptedException {
        Dispatcher dispatcher = new Dispatcher(10, 3);
        dispatcher.setChannel("EMAIL", new Channel() {
            @Override
            public boolean send(Notification notification) {
                return notification.getAttempts() > 0;
            }
        });
        
        Notification n1 = new Notification("u1", "msg1", "EMAIL", 1);
        dispatcher.enqueue(n1);
        
        assertFalse(dispatcher.processOne());
        assertEquals(1, n1.getAttempts());
        
        // Wait for exponential backoff (1s * 2^1 = 2000ms)
        Thread.sleep(2050); 
        
        assertTrue(dispatcher.processOne());
    }
    
    @Test
    public void testPreferencesAndChannels() {
        Dispatcher dispatcher = new Dispatcher(10, 1);
        
        dispatcher.getUserPreferences().setPreference("u1", "MARKETING", Arrays.asList("SMS", "PUSH"));
        dispatcher.getUserPreferences().setPreference("u2", "ALERT", Arrays.asList("SLACK"));
        
        assertTrue(dispatcher.dispatchBasedOnPreference("u1", "sale", "MARKETING", 1));
        assertTrue(dispatcher.dispatchBasedOnPreference("u2", "error", "ALERT", 1));
        
        int count = 0;
        while (!dispatcher.isQueueEmpty()) {
            dispatcher.pollQueue();
            count++;
        }
        assertEquals(3, count); // SMS, PUSH, SLACK
    }
}
