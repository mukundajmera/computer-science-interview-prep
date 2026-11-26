/**
 * Factory Method Pattern - V1 Basic (Classic Implementation)
 * 
 * Defines an interface for creating objects, but lets subclasses
 * decide which class to instantiate.
 */

// Product interface
interface Notification {
    void send(String message);

    String getType();
}

// Concrete Products
class EmailNotification implements Notification {
    private String recipient;

    public EmailNotification(String recipient) {
        this.recipient = recipient;
    }

    @Override
    public void send(String message) {
        System.out.println("Sending EMAIL to " + recipient + ": " + message);
    }

    @Override
    public String getType() {
        return "EMAIL";
    }
}

class SMSNotification implements Notification {
    private String phoneNumber;

    public SMSNotification(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    @Override
    public void send(String message) {
        System.out.println("Sending SMS to " + phoneNumber + ": " + message);
    }

    @Override
    public String getType() {
        return "SMS";
    }
}

class PushNotification implements Notification {
    private String deviceToken;

    public PushNotification(String deviceToken) {
        this.deviceToken = deviceToken;
    }

    @Override
    public void send(String message) {
        System.out.println("Sending PUSH to device " + deviceToken + ": " + message);
    }

    @Override
    public String getType() {
        return "PUSH";
    }
}

// Creator (Abstract)
abstract class NotificationCreator {

    // Factory Method - subclasses must implement
    public abstract Notification createNotification(String target);

    // Template method using factory method
    public void notifyUser(String target, String message) {
        Notification notification = createNotification(target);
        System.out.println("Created " + notification.getType() + " notification");
        notification.send(message);
    }
}

// Concrete Creators
class EmailNotificationCreator extends NotificationCreator {
    @Override
    public Notification createNotification(String target) {
        return new EmailNotification(target);
    }
}

class SMSNotificationCreator extends NotificationCreator {
    @Override
    public Notification createNotification(String target) {
        return new SMSNotification(target);
    }
}

class PushNotificationCreator extends NotificationCreator {
    @Override
    public Notification createNotification(String target) {
        return new PushNotification(target);
    }
}

// Demo
class FactoryMethodDemo {
    public static void main(String[] args) {
        System.out.println("=== Factory Method Pattern Demo ===\n");

        // Client code works with creators through abstract interface
        NotificationCreator emailCreator = new EmailNotificationCreator();
        NotificationCreator smsCreator = new SMSNotificationCreator();
        NotificationCreator pushCreator = new PushNotificationCreator();

        // Send notifications - client doesn't know concrete types
        emailCreator.notifyUser("user@example.com", "Welcome to our app!");
        System.out.println();

        smsCreator.notifyUser("+1234567890", "Your OTP is 123456");
        System.out.println();

        pushCreator.notifyUser("device-token-abc", "You have a new message");

        System.out.println("\n=== Demonstrating Polymorphism ===");

        // Can swap creators without changing client code
        NotificationCreator[] creators = {
                emailCreator, smsCreator, pushCreator
        };

        for (NotificationCreator creator : creators) {
            creator.notifyUser("target", "Broadcast message");
        }
    }
}
