import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

public class FactoryMethodTest {

    @Test
    @DisplayName("EmailNotificationCreator creates EmailNotification")
    void testEmailNotificationCreation() {
        NotificationCreator creator = new EmailNotificationCreator();
        Notification notification = creator.createNotification("test@example.com");

        assertNotNull(notification);
        assertEquals("EMAIL", notification.getType());
        assertDoesNotThrow(() -> notification.send("Test email message"));
    }

    @Test
    @DisplayName("SMSNotificationCreator creates SMSNotification")
    void testSMSNotificationCreation() {
        NotificationCreator creator = new SMSNotificationCreator();
        Notification notification = creator.createNotification("+1234567890");

        assertNotNull(notification);
        assertEquals("SMS", notification.getType());
        assertDoesNotThrow(() -> notification.send("Test SMS message"));
    }

    @Test
    @DisplayName("PushNotificationCreator creates PushNotification and notifyUser executes")
    void testPushNotificationCreationAndNotifyUser() {
        NotificationCreator creator = new PushNotificationCreator();
        Notification notification = creator.createNotification("device-tok-123");

        assertNotNull(notification);
        assertEquals("PUSH", notification.getType());
        assertDoesNotThrow(() -> creator.notifyUser("device-tok-123", "Broadcast message"));
    }
}
