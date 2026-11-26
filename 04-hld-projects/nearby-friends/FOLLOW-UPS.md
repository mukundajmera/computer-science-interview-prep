# Nearby Friends - Follow-Up Questions

## Follow-up questions

1. **Redis Pub/Sub Scaling:** At $14\text{M}$ messages per second, how do we partition the Redis Pub/Sub cluster? What happens if a node holding a popular user's channel goes down?
2. **Offline to Online Transition:** When a user opens the app after being offline, they haven't received Pub/Sub updates. How exactly do they get the initial state of their friends' locations?
3. **The Celebrity Problem:** If a user has 5,000 friends and 500 are online, they cause a massive localized fan-out. Do we throttle this? Do we degrade their updates from push to pull?
4. **WebSocket Reconnect Storms:** If a load balancer fails and drops 1 million WebSocket connections simultaneously, how do we prevent the resulting reconnect storm from taking down the auth and friend-graph services?

## Variants and extensions

- **"Discover Strangers" Variant:** Modify the design so users can see *anyone* within 1 mile. How does the architecture change from user-centric channels to Geohash grid channels?
- **Battery Optimization Variant:** Instead of a fixed 30-second interval, implement a dynamic interval. How does the client decide to update? (e.g., using local accelerometer/gyroscope to detect movement, or expanding the radius if battery is low).
- **Privacy Controls:** Users want to be "fuzzy" to certain groups of friends (e.g., showing only the city they are in, not exact coordinates). Where in the pipeline is this fuzzing logic applied?

## Interviewer probes to prepare

- "Why did you choose Redis over Kafka for the fan-out?"
- "Walk me through the exact network hops when User A's phone moves 100 feet and User B (a friend) is looking at the map."
- "If the Cassandra history database goes down, does the real-time map still work?"