from broker import MessageQueueBroker
from producer import Producer
from consumer import Consumer
from message import Message

if __name__ == "__main__":
    broker = MessageQueueBroker()
    broker.create_topic("orders", 2)
    
    producer = Producer(broker)
    producer.send("orders", Message("1", "Order 1 details"))
    producer.send("orders", Message("2", "Order 2 details"))
    
    consumer1 = Consumer(broker, "group1", "orders")
    print(f"Consumer 1 polled: {[str(m) for m in consumer1.poll_and_commit()]}")
