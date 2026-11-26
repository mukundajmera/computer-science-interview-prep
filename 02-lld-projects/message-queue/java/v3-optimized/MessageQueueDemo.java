
import java.util.List;

public class MessageQueueDemo {
    public static void main(String[] args) {
        MessageQueueBroker broker = new MessageQueueBroker();
        broker.createTopic("orders", 2);

        Producer producer = new Producer(broker);
        producer.send("orders", new Message("m1", "Order 1"));

        Consumer consumer1 = new Consumer(broker, "group1", "orders");
        List<Message> msgs = consumer1.poll();
        System.out.println("Consumer 1 polled: " + msgs);
        for(Message m : msgs) consumer1.ack(m);
    }
}
