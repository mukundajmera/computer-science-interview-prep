# Hotel Reservation System — Follow-Up Questions

Use these variants to drive deeper interview discussion after the baseline design.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

---

## 1. How would you handle high concurrency during a flash sale?
- **Model Answer**: Implement a distributed lock (e.g., Redis) or use a message queue to serialize booking requests. For reads, aggressively cache availability, accepting that it's eventually consistent, but strictly validate at checkout.

## 2. How to implement dynamic/surge pricing?
- **Model Answer**: Use a Rules Engine (Strategy pattern). The engine evaluates parameters (current occupancy rate, historical demand, local events) to calculate a price multiplier on the base rate dynamically upon search.

## 3. How would you scale the search functionality?
- **Model Answer**: Offload complex availability and full-text searches (by amenities, location) from the primary transactional database (SQL) to a dedicated search engine (Elasticsearch). Sync data via Change Data Capture (CDC).

## 4. How to handle overbooking policies?
- **Model Answer**: Decouple 'logical' availability from 'physical' room count. Allow the system to sell 105% of capacity based on historical no-show rates. Build an allocation service to handle upgrades or "walks" (relocating guests) when physical capacity is breached.

## 5. How would you implement distributed tracing across microservices?
- **Model Answer**: Inject a correlation ID at the API Gateway. Pass it through all internal microservice calls via headers. Log it centrally (ELK stack) to track a single reservation flow across Search, Booking, Payment, and Notification services.

## 6. How do you assign specific physical rooms efficiently?
- **Model Answer**: Guests book a `RoomType`. Run a nightly batch job or use an allocation algorithm at check-in to map reservations to specific physical `Room` IDs, optimizing for contiguous stays and maintenance schedules.

## 7. How to manage data retention and archiving?
- **Model Answer**: Run periodic background jobs to move old, completed reservations from the operational database to cold storage (e.g., AWS S3 or Glacier). Keep the hot operational DB lean for faster queries.

## 8. What is your strategy for handling third-party OTA integrations (Expedia, Booking.com)?
- **Model Answer**: Expose a rate-limited API for OTAs. Use an inventory distribution service that pushes availability updates to OTAs and consumes booking events from them, utilizing idempotency keys to handle network retries safely.

## 9. How to ensure idempotency for payment retries?
- **Model Answer**: Require clients to include a unique `Idempotency-Key` in request headers. The payment service checks if it has processed a request with this key. If yes, it returns the cached response; otherwise, it processes and stores the result.

## 10. How would you handle real-time housekeeping updates?
- **Model Answer**: Use a mobile app for staff that sends status updates (Clean, Dirty, Inspecting) via API. Publish these as events to a message broker. The Front Desk service subscribes to update room assignment availability in real-time.

---

## Follow-Up Scoring Signals

1. Candidate explains trade-offs, not only feature lists.
2. Candidate preserves API boundaries while extending behavior.
3. Candidate keeps concurrency and safety constraints explicit.
