"""
Tests for Bridge Pattern implementations.
"""
import os
import sys
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2-pythonic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v3-advanced"))


class TestV1RemoteBridge(unittest.TestCase):
    """Tests for V1 Basic Remote + Device Bridge."""

    def test_remote_controls_device_without_knowing_concrete_type(self):
        """Remote abstraction should operate through the Device bridge."""
        from bridge_demo import AdvancedRemote, Radio

        radio = Radio()
        remote = AdvancedRemote(radio)

        remote.toggle_power()
        remote.mute()

        self.assertTrue(radio.is_on())


class TestV2ShapeRendererBridge(unittest.TestCase):
    """Tests for V2 Pythonic Shape Renderer Bridge."""

    def test_shapes_render_through_different_renderers(self):
        """Shape abstraction should vary independently from renderer."""
        from shape_renderer import Circle, RasterRenderer, SvgRenderer

        circle = Circle(5, 10, 3, SvgRenderer())
        self.assertEqual(circle.draw(), '<circle cx="5" cy="10" r="3" />')

        circle.set_renderer(RasterRenderer())
        self.assertEqual(circle.draw(), "Raster circle at (5, 10) with radius 3")

    def test_renderer_collects_commands_for_multiple_shapes(self):
        """Renderer implementation should receive calls from different shapes."""
        from shape_renderer import Circle, Rectangle, RecordingRenderer

        renderer = RecordingRenderer()
        shapes = [
            Circle(0, 0, 2, renderer),
            Rectangle(1, 1, 4, 6, renderer),
        ]

        commands = [shape.draw() for shape in shapes]

        self.assertEqual(commands, ["circle:0:0:2", "rectangle:1:1:4:6"])
        self.assertEqual(renderer.commands, commands)


class TestV3NotificationBridge(unittest.TestCase):
    """Tests for V3 Advanced Notification Bridge."""

    def test_notifications_can_switch_sender_without_changing_message_type(self):
        """Notification abstraction should be independent of delivery sender."""
        from notification_bridge import EmailSender, SmsSender, UrgentNotification

        notification = UrgentNotification(EmailSender("ops@example.com"))
        email_receipt = notification.notify("db latency", "incident-7")

        notification.set_sender(SmsSender("+15551234567"))
        sms_receipt = notification.notify("db latency", "incident-7")

        self.assertEqual(email_receipt.channel, "email")
        self.assertEqual(email_receipt.priority, "HIGH")
        self.assertEqual(sms_receipt.channel, "sms")
        self.assertEqual(sms_receipt.priority, "HIGH")

    def test_digest_notification_uses_all_recipients(self):
        """Digest abstraction should format one message for many senders."""
        from notification_bridge import DigestNotification, EmailSender, InAppSender

        notification = DigestNotification(
            [
                EmailSender("team@example.com"),
                InAppSender("user-123"),
            ]
        )

        receipts = notification.notify("3 alerts pending", "daily-summary")

        self.assertEqual([receipt.channel for receipt in receipts], ["email", "in-app"])
        self.assertTrue(all(receipt.subject == "Digest: daily-summary" for receipt in receipts))


if __name__ == "__main__":
    unittest.main()
