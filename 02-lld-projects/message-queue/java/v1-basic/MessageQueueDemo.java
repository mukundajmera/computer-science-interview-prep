public class MessageQueueDemo {
    public static void main(String[] args) {
        MessageQueueBroker broker = new MessageQueueBroker();
        broker.createTopic("orders", 2);

        Producer producer = new Producer(broker);
        producer.send("orders", new Message("1", "Order 1 details"));
        producer.send("orders", new Message("2", "Order 2 details"));

        Consumer consumer1 = new Consumer(broker, "group1", "orders");
        System.out.println("Consumer 1 polled: " + consumer1.pollAndCommit());
    }
}
