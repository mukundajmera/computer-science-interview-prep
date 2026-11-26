import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

/**
 * Tests for Bridge Pattern implementations.
 */
public class BridgeTest {

    @Test
    @DisplayName("Remote should control device through bridge interface")
    void testRemoteControlsDevice() {
        Radio radio = new Radio();
        AdvancedRemote remote = new AdvancedRemote(radio);

        remote.togglePower();
        remote.mute();

        assertTrue(radio.isOn());
    }

    @Test
    @DisplayName("Shape should switch renderer without changing abstraction")
    void testShapeSwitchesRenderer() {
        Circle circle = new Circle(5, 10, 3, new SvgRenderer());

        assertEquals("<circle cx=\"5\" cy=\"10\" r=\"3\" />", circle.draw());

        circle.setRenderer(new RasterRenderer());

        assertEquals("Raster circle at (5, 10) with radius 3", circle.draw());
    }

    @Test
    @DisplayName("Renderer should collect commands from multiple shapes")
    void testRecordingRendererCollectsCommands() {
        RecordingRenderer renderer = new RecordingRenderer();
        Shape circle = new Circle(0, 0, 2, renderer);
        Shape rectangle = new Rectangle(1, 1, 4, 6, renderer);

        List<String> commands = Arrays.asList(circle.draw(), rectangle.draw());

        assertEquals(Arrays.asList("circle:0:0:2", "rectangle:1:1:4:6"), commands);
        assertEquals(commands, renderer.getCommands());
    }

    @Test
    @DisplayName("Notification should switch sender independently")
    void testNotificationSwitchesSender() {
        UrgentNotification notification = new UrgentNotification(new EmailSender("ops@example.com"));

        DeliveryReceipt emailReceipt = notification.notify("db latency", "incident-7");
        notification.setSender(new SmsSender("+15551234567"));
        DeliveryReceipt smsReceipt = notification.notify("db latency", "incident-7");

        assertEquals("email", emailReceipt.getChannel());
        assertEquals("HIGH", emailReceipt.getPriority());
        assertEquals("sms", smsReceipt.getChannel());
        assertEquals("HIGH", smsReceipt.getPriority());
    }

    @Test
    @DisplayName("Digest notification should use all recipients")
    void testDigestUsesAllRecipients() {
        DigestNotification notification = new DigestNotification(Arrays.asList(
            new EmailSender("team@example.com"),
            new InAppSender("user-123")
        ));

        List<DeliveryReceipt> receipts = notification.notify("3 alerts pending", "daily-summary");

        assertEquals(Arrays.asList("email", "in-app"), Arrays.asList(
            receipts.get(0).getChannel(),
            receipts.get(1).getChannel()
        ));
        assertTrue(receipts.stream().allMatch(r -> "Digest: daily-summary".equals(r.getSubject())));
    }
}
