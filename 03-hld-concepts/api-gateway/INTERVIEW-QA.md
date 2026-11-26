# Interview Questions: API Gateway

## Basic Questions

### 1. Why do we need an API Gateway?
**Q**: What does an API Gateway do in one sentence?
**A**: It acts as a single entry point for clients, centralizing routing, authentication, rate limiting, and request policies for a collection of backend services.

### 2. Gateway vs Load Balancer
**Q**: What is the key difference between an API Gateway and a standard Load Balancer?
**A**: Load balancers operate primarily at Layer 4 (distributing traffic blindly based on IP/Port), while Gateways operate at Layer 7, applying application-specific policies (like token validation) and complex routing rules.

### 3. Gateway vs Service Mesh
**Q**: When would you use a Service Mesh vs an API Gateway?
**A**: Use an API Gateway for "North-South" traffic (external clients entering the system) to handle edge security and routing. Use a Service Mesh for "East-West" traffic (internal service-to-service communication) to handle internal mTLS, retries, and internal load balancing.

### 4. What is the Backend-For-Frontend (BFF) pattern?
**Q**: How does a BFF differ from a traditional API Gateway?
**A**: A traditional Gateway serves all clients, whereas a BFF is a specialized Gateway tailored for a specific client interface (e.g., one BFF for mobile, one for web), allowing UI teams to optimize their own data aggregation.

## Intermediate Questions

### 5. Mandatory Gateway Policies
**Q**: What controls should be mandatory in a production API Gateway?
**A**: Authentication/authorization, route-level rate limits, strict timeouts, observability (metrics/tracing), and basic payload size protections.

### 6. Managing the Latency Budget
**Q**: How do you ensure the API Gateway doesn't become a latency bottleneck?
**A**: By keeping the gateway data plane stateless and fast, heavily caching auth/rate limit lookups (or using fast local approximations), and enforcing strict upper-bound timeouts on backend calls.

### 7. Avoiding a Single Point of Failure (SPOF)
**Q**: Since all traffic flows through the Gateway, how do you design it for High Availability?
**A**: Deploy multiple stateless gateway instances across different availability zones behind a Layer 4 Network Load Balancer (NLB), and decouple the control plane (management) from the data plane (traffic handling).

### 8. The Filter Pipeline
**Q**: Explain how a request flows through an API Gateway.
**A**: It passes through a "filter chain" or middleware pipeline. First, security filters (WAF, AuthN), then traffic management filters (Rate Limiting), then routing/transformation, and finally it's sent to the backend. The response passes back through response filters.

### 9. Control Plane vs Data Plane
**Q**: What happens if the API Gateway's Control Plane goes down?
**A**: The Data Plane (the nodes actually proxying traffic) will continue to operate normally using the last known configuration, but you won't be able to update routes or policies until the Control Plane recovers.

## Advanced Questions

### 10. API Composition and Aggregation
**Q**: How does a Gateway improve performance for mobile clients needing data from multiple microservices?
**A**: Instead of the mobile client making multiple high-latency network calls, it makes one call to the Gateway. The Gateway executes the multiple calls to the backend concurrently over the fast internal network, aggregates the JSON, and returns a single response.

### 11. Tiered Rate Limiting
**Q**: How do you support free and premium tiers with different rate limits?
**A**: The Gateway inspects the authenticated user's token/profile, applies a route-level policy configuration with separate quotas (e.g., using Token Buckets), and returns specific headers indicating remaining quota to the client.

### 12. Version Migration and Canary Releases
**Q**: How do you shift traffic safely between service versions using a Gateway?
**A**: Use weighted routing rules on the Gateway to send a small percentage of traffic (e.g., 5%) to the new version (canary). Monitor latency and error rates on the gateway metrics, and automatically rollback if thresholds are breached.

### 13. Retry Budgets and Cascading Failures
**Q**: Why is it dangerous for an API Gateway to blindly retry failed backend requests?
**A**: If a backend is failing because it is overloaded, blind retries from the Gateway will multiply the load, causing a cascading failure ("retry storm"). Gateways must implement "retry budgets" (e.g., cap retries at 10% of total traffic) and circuit breakers.

### 14. Thundering Herd and Caching
**Q**: How does an API Gateway handle a "thundering herd" when a popular cache item expires?
**A**: It can use "request collapsing" (or coalescing). The Gateway holds all concurrent requests for the expired item, forwards only the *first* request to the backend, and then uses that response to serve all the waiting clients.

### 15. Handling Massive File Uploads
**Q**: Should clients stream 5GB video uploads directly through the API Gateway?
**A**: Generally, no. This ties up Gateway connections and memory. The Gateway should issue a short-lived "presigned URL", and the client should upload the file directly to object storage (like S3), bypassing the Gateway for the heavy data transfer.

## Red flags to avoid
- Stateful gateway design (e.g., storing session state in the gateway's local memory).
- Embedding deep business workflow logic into the gateway layer.
- Missing explicit timeout and backpressure controls on backend routes.

## 30-second explanation
"An API Gateway is the policy and routing layer at the system edge. It centralizes auth, quota, and request controls, then routes to backend services. I keep it stateless, enforce strict timeout budgets, manage cross-cutting concerns via a filter pipeline, and use route-level policies with clear rollout and rollback strategies to ensure resilience."
