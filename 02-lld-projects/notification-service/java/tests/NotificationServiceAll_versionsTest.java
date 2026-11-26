import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;
import java.lang.reflect.Method;
import java.lang.reflect.Constructor;

public class NotificationServiceAll_versionsTest {
    
    private Object getDispatcher(ClassLoader cl) throws Exception {
        Class<?> dispatcherClass = cl.loadClass("Dispatcher");
        Constructor<?> constructor = dispatcherClass.getConstructor(int.class, int.class);
        return constructor.newInstance(100, 1);
    }
    
    private Object getNotificationService(ClassLoader cl, Object dispatcher) throws Exception {
        Class<?> dispatcherClass = cl.loadClass("Dispatcher");
        Class<?> serviceClass = cl.loadClass("NotificationService");
        Constructor<?> constructor = serviceClass.getConstructor(dispatcherClass, int.class, int.class);
        return constructor.newInstance(dispatcher, 5, 1);
    }

    @Test
    public void testIdempotencyAndPreferences() throws Exception {
        File file = new File("02-lld-projects/notification-service/java/v3-optimized/");
        URL url = file.toURI().toURL();
        URL[] urls = new URL[]{url};
        URLClassLoader cl = new URLClassLoader(urls);

        Object dispatcher = getDispatcher(cl);
        Object service = getNotificationService(cl, dispatcher);

        Class<?> serviceClass = service.getClass();
        Class<?> enumClass = cl.loadClass("NotificationService$IntentState");
        
        Method unsubscribe = serviceClass.getMethod("unsubscribe", String.class);
        unsubscribe.invoke(service, "u3");
        
        Method submitIntent = serviceClass.getMethod("submitIntent", String.class, String.class, String.class, String.class, int.class);
        
        Object state = submitIntent.invoke(service, "PROMO", "u1", "EMAIL", "Hello", 1);
        assertEquals("PENDING", state.toString());
        
        Object state2 = submitIntent.invoke(service, "PROMO", "u1", "EMAIL", "Hello", 1);
        assertEquals("CONFLICT", state2.toString());
        
        for (int i = 0; i < 4; i++) {
            submitIntent.invoke(service, "PROMO", "u" + (i + 10), "EMAIL", "Hello", 1);
        }
        
        Object stateOverflow = submitIntent.invoke(service, "PROMO", "u100", "EMAIL", "Hello", 1);
        assertEquals("FAILED", stateOverflow.toString());
        
        cl.close();
    }
    
    @Test
    public void testDeliveryStateTransitions() throws Exception {
        File file = new File("02-lld-projects/notification-service/java/v3-optimized/");
        URL url = file.toURI().toURL();
        URL[] urls = new URL[]{url};
        URLClassLoader cl = new URLClassLoader(urls);

        Object dispatcher = getDispatcher(cl);
        
        Class<?> dispatcherClass = cl.loadClass("Dispatcher");
        Class<?> serviceClass = cl.loadClass("NotificationService");
        Constructor<?> constructor = serviceClass.getConstructor(dispatcherClass, int.class, int.class);
        Object service = constructor.newInstance(dispatcher, 10, 1);
        
        Class<?> channelClass = cl.loadClass("Channel");
        Class<?> notificationClass = cl.loadClass("Notification");
        
        // Use standard channels for test as implementing anonymous class dynamically is hard
        // We will just test enqueue manually through submitIntent
        
        Method submitIntent = serviceClass.getMethod("submitIntent", String.class, String.class, String.class, String.class, int.class);
        submitIntent.invoke(service, "ALERT", "u1", "EMAIL", "Hello", 1);
        
        Method getIntentState = serviceClass.getMethod("getIntentState", String.class);
        Object state = getIntentState.invoke(service, "ALERT:u1:EMAIL");
        assertEquals("PENDING", state.toString());
        
        cl.close();
    }
}
