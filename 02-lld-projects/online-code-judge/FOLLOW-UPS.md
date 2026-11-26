# Follow-Ups: Online Code Judge (Optional Staff Follow-Ups)

1. **How would you distribute the workers across multiple machines?**
   - **Answer**: I would replace the in-memory queue with a message broker like Kafka or RabbitMQ. Workers on different machines would consume from this distributed queue, process the code, and write the verdict to a distributed database (like DynamoDB or PostgreSQL) and emit an event.

2. **How do you handle a malicious user submitting an infinite loop or resource exhaustion attack?**
   - **Answer**: Standard library execution timeouts are not a security sandbox. We must document a separately approved VM/container boundary (e.g., Docker, Firecracker microVMs) with strict filesystem, network, CPU, memory, output, and process controls. The orchestrator forcefully terminates processes exceeding constraints, yielding a `TLE` or `MLE` verdict.

3. **How would you scale to handle peak coding contest traffic?**
   - **Answer**: Implement auto-scaling for the worker nodes based on queue depth. The API layer would simply accept the submission and return a 202 Accepted, placing it on a Kafka topic, ensuring the web servers don't get bogged down by execution loads.
