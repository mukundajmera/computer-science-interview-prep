/**
 * Bridge Pattern - V3 Advanced: Notifications + Senders
 *
 * Notification policy and delivery channels vary independently.
 */

import java.util.ArrayList;
import java.util.List;

class DeliveryReceipt {
    private final String channel;
    private final String recipient;
    private final String subject;
    private final String body;
    private final String priority;

    public DeliveryReceipt(String channel, String recipient, String subject, String body, String priority) {
        this.channel = channel;
        this.recipient = recipient;
        this.subject = subject;
        this.body = body;
        this.priority = priority;
    }

    public String getChannel() { return channel; }
    public String getRecipient() { return recipient; }
    public String getSubject() { return subject; }
    public String getBody() { return body; }
    public String getPriority() { return priority; }
}

interface MessageSender {
    DeliveryReceipt send(String subject, String body, String priority);
}

class EmailSender implements MessageSender {
    private final String address;

    public EmailSender(String address) {
        this.address = address;
    }

    @Override
    public DeliveryReceipt send(String subject, String body, String priority) {
        return new DeliveryReceipt("email", address, subject, body, priority);
    }
}

class SmsSender implements MessageSender {
    private final String phoneNumber;

    public SmsSender(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    @Override
    public DeliveryReceipt send(String subject, String body, String priority) {
        return new DeliveryReceipt("sms", phoneNumber, subject, body, priority);
    }
}

class InAppSender implements MessageSender {
    private final String userId;

    public InAppSender(String userId) {
        this.userId = userId;
    }

    @Override
    public DeliveryReceipt send(String subject, String body, String priority) {
        return new DeliveryReceipt("in-app", userId, subject, body, priority);
    }
}

abstract class Notification {
    protected MessageSender sender;

    protected Notification(MessageSender sender) {
        this.sender = sender;
    }

    public void setSender(MessageSender sender) {
        this.sender = sender;
    }

    public abstract DeliveryReceipt notify(String body, String topic);
}

class UrgentNotification extends Notification {
    public UrgentNotification(MessageSender sender) {
        super(sender);
    }

    @Override
    public DeliveryReceipt notify(String body, String topic) {
        return sender.send("Urgent: " + topic, body, "HIGH");
    }
}

class RoutineNotification extends Notification {
    public RoutineNotification(MessageSender sender) {
        super(sender);
    }

    @Override
    public DeliveryReceipt notify(String body, String topic) {
        return sender.send("Update: " + topic, body, "NORMAL");
    }
}

class DigestNotification {
    private final List<MessageSender> senders;

    public DigestNotification(List<MessageSender> senders) {
        this.senders = new ArrayList<>(senders);
    }

    public List<DeliveryReceipt> notify(String body, String topic) {
        List<DeliveryReceipt> receipts = new ArrayList<>();
        for (MessageSender sender : senders) {
            receipts.add(sender.send("Digest: " + topic, body, "LOW"));
        }
        return receipts;
    }
}

public class NotificationBridgeDemo {
    public static void main(String[] args) {
        UrgentNotification notification = new UrgentNotification(new EmailSender("ops@example.com"));
        System.out.println(notification.notify("Database latency", "incident-7").getChannel());
        notification.setSender(new SmsSender("+15551234567"));
        System.out.println(notification.notify("Database latency", "incident-7").getChannel());
    }
}
