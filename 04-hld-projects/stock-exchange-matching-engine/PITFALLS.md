# Stock Exchange Matching Engine - Common Pitfalls

## 1. Using a Relational DB in the Critical Path
- **Signal:** Candidate designs an architecture where `PlaceOrder` executes a `BEGIN; SELECT FOR UPDATE; INSERT; COMMIT;` on a Postgres database.
- **Root Cause:** Defaulting to standard web-tier CRUD patterns.
- **Mitigation:** Explicitly state the latency constraint ($< 100\text{ }\mu\text{s}$). A database network hop alone takes 1-2ms. State must live in memory.

## 2. Horizontally Scaling a Single Ticker
- **Signal:** Candidate proposes load balancing AAPL orders across 5 matching instances to handle high QPS.
- **Root Cause:** Misunderstanding race conditions in financial matching.
- **Mitigation:** Explain that matching requires strict serialization. You cannot have two nodes matching AAPL simultaneously without complex, slow distributed locking. Scale by sharding tickers (e.g., AAPL on Server A, MSFT on Server B).

## 3. Poor Data Structure Choices
- **Signal:** Using an array or standard list to store orders, requiring $O(N)$ scans to find an order to cancel.
- **Root Cause:** Not anticipating the high volume of cancel requests from market makers.
- **Mitigation:** Use a `HashMap` alongside the tree to maintain $O(1)$ lookup for cancellations.

## 4. Floating Point Math
- **Signal:** Using `double` or `float` for prices and quantities.
- **Root Cause:** Lack of domain experience in financial engineering.
- **Mitigation:** Always use fixed-point integers (`long` in Java) representing the smallest fractional unit (e.g., pennies or hundredths of a penny).
