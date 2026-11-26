
public class Producer {
    private final MessageQueueBroker broker;

    public Producer(MessageQueueBroker broker) {
        this.broker = broker;
    }

    public void send(String topic, Message message) {
        broker.publish(topic, message);
    }
}
